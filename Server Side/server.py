'''Server for communication between two or more zmq type clients.

    Working with Router-Dealer connection.
    Sending multipart messages in custom json format.
'''
import json
import sys
import sqlite3
import time
import traceback
from threading import Thread
import zmq
from enums_server import Host, Intervals
from login_server import LoginServer


class Server:
    '''Server Class where all communication is proccessed'''

    def __init__(self):
        self.context = zmq.Context.instance()
        self.recv_socket = None
        self.database = sqlite3.connect(Host.DATABASE)  # database of users and their tokens

    # Bind server socket to port and setting identity for server main socket
    def server_bind(self):
        '''Binding zmq socket to context in Server class'''
        self.recv_socket = self.context.socket(zmq.ROUTER)
        self.recv_socket.setsockopt(zmq.IDENTITY, Host.HOST)
        bind_address_rcv = 'tcp://{}:{}'.format(Host.ADDRESS, Host.PORT)
        self.recv_socket.bind(bind_address_rcv)
        print('Receiving socket bound!')

    # Receive and process the message
    def receive_message(self):
        '''Receiving message from recv_socket'''
        id_, data_raw = self.recv_socket.recv_multipart()  # recv id and raw message
        data = json.loads(data_raw)  # that needs to be processed
        to_ = data['to']
        token = data['token']
        message = data['message']
        can_do = False

        # Inspect token, if token is active you can send message
        cursor = self.database.cursor()
        cursor.execute("SELECT token FROM tokens")
        temp = cursor.fetchall()
        if any(token == row[0] for row in temp):
            print('{} sent to {}: {} token({})'.format(
                id_.decode('utf-8'), to_, message, token))
            cursor.execute(
                'UPDATE tokens SET timestamp = ? WHERE username = ? ',
                (str(round(time.time())), id_.decode('utf-8')))
            self.database.commit()
            return id_.decode('utf-8'), to_.encode(), message, True
        print('{} sent to {}: {} token({} expired)'.format(id_.decode('utf-8'),
                                                           to_, message, token))
        return id_.decode('utf-8'), to_.encode(), message, False

    # send message that has been formatted to be read on client

    def send_message(self, client_id, client_to, client_message):
        '''Sending message to target client'''
        data = {'id': client_id, 'message': client_message}
        message = json.dumps(data).encode()
        send_data = [client_to, message]
        self.recv_socket.send_multipart(send_data)

    @staticmethod
    def delete_token():
        '''Token deletion method'''
        db_name = Host.DATABASE
        while True:
            database = sqlite3.connect(db_name)
            cursor = database.cursor()
            cursor.execute("SELECT * FROM tokens")
            tokens_select = cursor.fetchall()
            for tmp in tokens_select:
                user = tmp[0]
                token_time = tmp[2]
                if round(time.time()) - int(
                        token_time) >= Intervals.TOKEN_EXPIRATION:
                    cursor.execute("DELETE FROM tokens WHERE username = ?",
                                   (user,))
                    database.commit()
            cursor.close()
            database.close()
            time.sleep(Intervals.TOKEN_CHECK_INTERVAL)
            continue

    def save_message_to_base(self, client_id, client_to, client_message):
        '''Saving currently received message to database'''
        cursor = self.database.cursor()
        cursor.execute("INSERT INTO history VALUES (?,?,?,?)",
                       (str(time.asctime(time.localtime(time.time()))),
                        client_id, client_to.decode(), client_message))
        self.database.commit()
        cursor.close()

    def server_run(self):
        '''Main server program, running all functionalities'''
        try:
            self.server_bind()
            poller = zmq.Poller()
            poller.register(self.recv_socket, zmq.POLLIN)

            login_server = LoginServer()  # login server object on port 5557
            login_server.start()
            time.sleep(1)  # wait for login server to finish creating database tables

            delete_token = Thread(target=self.delete_token, daemon=True)
            delete_token.start()
            # if message is received process it, if not, try again

            while True:
                events = dict(poller.poll(timeout=Intervals.POLL_IN_TIME))
                while True:
                    if self.recv_socket in events:
                        id_, to_, new_message, send = self.receive_message()
                        # if token is OK, send message to targeted receiver
                        if not new_message:
                            break
                        elif send:
                            self.send_message(id_, to_, new_message)
                            self.save_message_to_base(id_, to_, new_message)
                        # if token isn't OK, return token_expired message to sender
                        else:
                            self.send_message(id_, id_.encode(), 'Your token expired!')
                    else:
                        break

        except(KeyboardInterrupt, SystemExit) as ex:
            # if we get KeyboardInterupt,SystemExit or some ZMQError we delete tokens table
            cursor = self.database.cursor()
            cursor.execute('DROP TABLE IF EXISTS tokens')
            cursor.close()
            self.database.close()
            self.context.destroy()
            print('\nKeyboard Interupt ! Main Server closing...')
            sys.exit(0)
        except (zmq.ZMQError):
            cursor = self.database.cursor()
            cursor.execute('DROP TABLE IF EXISTS tokens')
            cursor.close()
            self.database.close()
            self.context.destroy()
            print('ZMQError occured, Closing Main Server...')
            sys.exit(0)
        except Exception as ex:
            print("Not handled: ", type(ex).__name__)
            print(traceback.format_exc())
