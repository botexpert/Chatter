import zmq
import json
from login_server import LoginServer
import sqlite3
import time
from threading import Thread


# Server for communication between two or more zmq type clients, working with Router-Dealer connection and
# sending multipart messages in json format


class Server:
    def __init__(self, address, rcv_port, db):
        self.db_name = db
        self.address = address  # address for main port (probably :localhost:)
        self.recv_port = rcv_port  # receive socket port
        self.context = zmq.Context.instance()  # zmq Context for making socket
        self.recv_socket = None
        self.database = sqlite3.connect(db)  # database of users and their tokens

    # Bind server socket to port and setting identity for server main socket
    def server_bind(self):
        self.recv_socket = self.context.socket(zmq.ROUTER)
        self.recv_socket.setsockopt(zmq.IDENTITY, b'serverID')
        bind_address_rcv = 'tcp://{}:{}'.format(self.address, self.recv_port)
        self.recv_socket.bind(bind_address_rcv)
        print('Receiving socket bound!')

    # Receive and process the message
    def receive_message(self):
        id, data_raw = self.recv_socket.recv_multipart()  # recv_multipart recieves Id of sender and raw json data
        data = json.loads(data_raw)  # that needs to be processed
        to = data['to']
        token = data['token']
        message = data['message']
        can_do=False
        # Inspect token, if token is in database of active clients return confirmation for sending message
        cursor = self.database.cursor()
        cursor.execute("SELECT token FROM tokens")
        for row in cursor:
            if token == row[0]:
                print('{} sent to {}: {} token({})'.format(id.decode('utf-8'),to, message,token))
                can_do= True
        if can_do:
            cursor.execute('UPDATE tokens SET timestamp = ? WHERE username = ? ',
                           (str(round(time.time())), id.decode('utf-8')))
            self.database.commit()
            return id.decode('utf-8'), to.encode(), message, True
        print('{} sent to {}: {} token({} expired)'.format(id.decode('utf-8'),to, message,token))
        return id.decode('utf-8'), to.encode(), message, False

    # send message that has been formatted to be read on client

    def send_message(self, client_id, client_to, client_message):
        data = {'id': client_id,
                'message': client_message}
        s = json.dumps(data).encode()
        cursor = self.database.cursor()
        cursor.execute("INSERT INTO history VALUES (?,?,?,?)",
                       (str(time.asctime(time.localtime(time.time()))),
                        client_id, client_to.decode(), client_message))
        self.database.commit()

        send_data = [client_to, s]
        self.recv_socket.send_multipart(send_data)

    def delete_token(self,db_name):
        while True:
            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            cursor.execute("SELECT * FROM tokens")
            tokens_select=cursor.fetchall()
            for tmp in tokens_select:
                user = tmp[0]
                token_time = tmp[2]
                if (round(time.time())-int(token_time)>=60):
                    cursor.execute("DELETE FROM tokens WHERE username = ?",(user,))
                    db.commit()
            cursor.close()
            db.close()
            time.sleep(1)
            continue

    def server_run(self):
        try:
            self.server_bind()
            poller = zmq.Poller()
            poller.register(self.recv_socket, zmq.POLLIN)
        except(zmq.ZMQError):
            print("Error while binding occured, server closing now...")
            return

        login_server = LoginServer('5557',self.db_name)  # login server object on port 5557
        login_server.start()
        time.sleep(1)

        delete_token= Thread(target=self.delete_token,args=(self.db_name,))
        delete_token.start()

        # if message is received process it, if not, try again
        while True:
            try:
                while True:
                    events = dict(poller.poll(timeout=250))
                    while True:
                        if self.recv_socket in events:
                            id_, to_, new_message, send = self.receive_message()
                            # if token is OK, send message to targeted receiver
                            if not new_message :
                                break
                            elif send:
                                self.send_message(id_, to_, new_message)
                            # if token isn't OK, return token_expired message to sender
                            else:
                                self.send_message(id_, id_.encode(),'Your token expired!')
                        else:
                            break
            except(KeyboardInterrupt, SystemExit):
            # if we get KeyboardInterupt or SystemExit we delete tokens table
                cursor = self.database.cursor()
                cursor.execute('DROP TABLE tokens')
                self.database.close()
                self.context.destroy()
                print('MAIN SERVER CLOSING...')
                return 0

            except(zmq.ZMQError):
                print('Some error occured, trying again')
                continue

