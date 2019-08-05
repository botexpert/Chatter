import zmq
import json
from login_server import LoginServer
import sqlite3
import time


# Server for communication between two or more zmq type clients, working with Router-Dealer connection and
# sending multipart messages in json format


class Server:
    def __init__(self, address, rcv_port, db):
        self.address = address  # address for main port (probably :localhost:)
        self.recv_port = rcv_port  # receive socket port
        self.context = zmq.Context.instance()  # zmq Context for making socket
        self.recv_socket = None
        self.database = sqlite3.connect(
            db)  # database of users and their tokens
        login_server = LoginServer('5557',
                                   db)  # login server object on port 5557
        login_server.start()

    # Bind server socket to port and setting identity for server main socket
    def server_bind(self):
        self.recv_socket = self.context.socket(zmq.ROUTER)
        self.recv_socket.setsockopt(zmq.IDENTITY, b'serverID')
        bind_address_rcv = 'tcp://{}:{}'.format(self.address, self.recv_port)
        self.recv_socket.bind(bind_address_rcv)
        print('Receiving socket bound!')

    # Receive and process the message
    def receive_message(self):
        id_, data_raw = self.recv_socket.recv_multipart()  # recv_multipart recieves Id of sender and raw json data
        data = json.loads(data_raw)  # that needs to be processed
        to_ = data['to']
        token = data['token']
        message = data['message']

        # Inspect token, if token is in database of active clients return confirmation for sending message
        cursor = self.database.cursor()
        cursor.execute("SELECT token FROM tokens")
        for row in cursor:
            if token == row[0]:
                print('{} sent to {}: {} token({})'.format(id_.decode('utf-8'),
                                                           to_, message,
                                                           token))
                return id_.decode('utf-8'), to_.encode(), message, True
        print('{} sent to {}: {} token({} expired)'.format(id_.decode('utf-8'),
                                                           to_, message,
                                                           token))
        return id_.decode('utf-8'), to_.encode(), message, False

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

    def server_run(self):
        self.server_bind()
        poller = zmq.Poller()
        poller.register(self.recv_socket, zmq.POLLIN)
        # if message is received process it, if not, try again
        try:
            while True:
                events = dict(poller.poll(timeout=250))
                while True:
                    if self.recv_socket in events:
                        id_, to_, new_message, send = self.receive_message()
                        # if token is OK, send message to targeted receiver
                        if send:
                            self.send_message(id_, to_, new_message)
                        # if token isn't OK, return token_expired message to sender
                        else:
                            self.send_message(id_, id_.encode(),
                                              'Your token expired!')
                    else:
                        break
        except(KeyboardInterrupt, SystemExit):
            # if we get KeyboardInterupt or SystemExit we delete tokens table
            cursor = self.database.cursor()
            cursor.execute('DROP TABLE tokens')
            print('SERVER STOPPED WORKING')
            raise
