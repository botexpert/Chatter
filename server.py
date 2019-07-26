import zmq
import json
from login_server import LoginServer


class Server:
    def __init__(self, address, rcv_port):
        self.address = address
        self.recv_port = rcv_port
        self.context = zmq.Context.instance()
        self.recv_socket = None
        login_server = LoginServer('5557')
        login_server.start()

    def server_bind(self):
        self.recv_socket = self.context.socket(zmq.ROUTER)
        self.recv_socket.setsockopt(zmq.IDENTITY, b'serverID')
        bind_address_rcv = 'tcp://{}:{}'.format(self.address, self.recv_port)
        self.recv_socket.bind(bind_address_rcv)
        print('Socket bound')

    def receive_message(self):
        ID, data_raw = self.recv_socket.recv_multipart()
        data = json.loads(data_raw)
        TO = data['to']
        message = data['message']
        print('{}sent to {}: {}'.format(ID, TO, message))
        return ID.decode("utf-8"), TO.encode(), message

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
                    ID, TO, new_message = self.receive_message()
                    self.send_message(ID, TO, new_message)
                else:
                    break
