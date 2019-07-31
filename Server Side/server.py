import zmq
import json
from login_server import LoginServer
import sqlite3
import time

# Server for communication between two or more zmq type clients, working with Router-Dealer connection and
# sending myltipart messages custom formated with json

class Server:
    def __init__(self, address, rcv_port):
        self.address = address  # adress for main port (probably :localhost:)
        self.recv_port = rcv_port  # recieve socket port
        self.context = zmq.Context.instance()  # zmq Context for making socket
        self.recv_socket = None
        login_server = LoginServer('5557')  # login server object on port 5557
        login_server.start()
        self.database = database = sqlite3.connect('user_database.db')  # database of users and their tokens

    # Bind server socket to port and setting identity for server main socket
    def server_bind(self):
        self.recv_socket = self.context.socket(zmq.ROUTER)
        self.recv_socket.setsockopt(zmq.IDENTITY, b'serverID')
        bind_address_rcv = 'tcp://{}:{}'.format(self.address, self.recv_port)
        self.recv_socket.bind(bind_address_rcv)
        print('Receiving socket bound!')

    # Receive and process the message
    def receive_message(self):
        ID, data_raw = self.recv_socket.recv_multipart()  # recv_multipart recieves Id of sender and raw json data
        data = json.loads(data_raw)  # that needs to be processed
        TO = data['to']
        TOKEN = data['token']
        message = data['message']

        # Inspect token, if token is in database of active clients return confirmation for sending message
        cursor = self.database.cursor()
        cursor.execute("SELECT token FROM tokens")
        for row in cursor:
            if TOKEN == row[0]:
                print('{} sent to {}: {} token({})'.format(ID.decode('utf-8'), TO, message, TOKEN))
                return ID.decode('utf-8'), TO.encode(), message, True
        print('{} sent to {}: {} token({} expired)'.format(ID.decode('utf-8'), TO, message, TOKEN))
        return ID.decode('utf-8'), TO.encode(), message, False

    # send message that has been firstly formated customly to be read on client
    def send_message(self, client_id, client_to, client_message):
        data = {'id': client_id,
                'message': client_message}
        s = json.dumps(data).encode()
        cursor = self.database.cursor()
        table = 'CREATE TABLE IF NOT EXISTS {}(sent_to TEXT,message TEXT,timestamp TEXT)'.format(client_id)

        cursor.execute(table)
        cursor.execute("INSERT INTO {} VALUES (?,?,?)".format(client_id),(client_to.decode(),client_message,str(time.asctime(time.localtime(time.time())))))
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
                        ID, TO, new_message, send = self.receive_message()
                        # if token is OK, send message to targeted receiver
                        if send:
                            self.send_message(ID, TO, new_message)
                        # if token isn't OK, return token_expired message to sender
                        else:
                            self.send_message(ID, ID.encode(), 'Your token expired!')
                    else:
                        break
        except(KeyboardInterrupt, SystemExit):
            #if we get KeyboardInterupt or SystemExit we delete tokens table
            cursor=self.database.cursor()
            cursor.execute('DROP TABLE tokens')
            raise