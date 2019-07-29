import zmq
import json
from login_server import LoginServer
import sqlite3


class Server:
    def __init__(self, address, rcv_port):
        self.address = address
        self.recv_port = rcv_port
        self.context = zmq.Context.instance()
        self.recv_socket = None
        login_server = LoginServer('5557')
        login_server.start()
        self.database = database = sqlite3.connect('user_database.db')

    # Bind server  socket
    def server_bind(self):
        self.recv_socket = self.context.socket(zmq.ROUTER)
        self.recv_socket.setsockopt(zmq.IDENTITY, b'serverID')
        bind_address_rcv = 'tcp://{}:{}'.format(self.address, self.recv_port)
        self.recv_socket.bind(bind_address_rcv)
        print('Receiving socket bound!')

    # Receive and process the message
    def receive_message(self):
        ID, data_raw = self.recv_socket.recv_multipart()
        data = json.loads(data_raw)
        TO = data['to']
        TOKEN = data['token']
        message = data['message']
        print('{} sent to {}: {} token({})'.format(ID.decode('utf-8'), TO, message, TOKEN))
        cursor = self.database.cursor()
        cursor.execute("SELECT token FROM tokens")
        for row in cursor:
            if TOKEN == row[0]:
                return ID.decode('utf-8'), TO.encode(), message, True
        return ID.decode('utf-8'), TO.encode(), message, False

    def send_message(self, client_id, client_to, client_message):
        data = {'id': client_id,
                'message': client_message}
        s = json.dumps(data).encode()
        send_data = [client_to, s]
        self.recv_socket.send_multipart(send_data)

    def server_run(self):
        self.server_bind()
        poller = zmq.Poller()
        poller.register(self.recv_socket, zmq.POLLIN)
        while True:
            events = dict(poller.poll(timeout=250))
            while True:
                if self.recv_socket in events:
                    ID, TO, new_message, send = self.receive_message()
                    if send == True:
                        self.send_message(ID, TO, new_message)
                    #self.send_message('serverID', ID, 'Your token expired!')
                else:
                    break
