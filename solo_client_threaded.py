import zmq
from threading import Thread


class StandaloneClient():
    def __init__(self, interface, sub_port, pub_port, host):
        self.interface = interface
        self.sub_port = sub_port
        self.pub_port = pub_port
        self.host = host
        self.context = zmq.Context.instance()

    def listener(self):
        sub_socket = self.context.socket(zmq.SUB)
        connection = "tcp://{}:{}".format(self.host, self.sub_port)
        sub_socket.connect(connection)
        sub_socket.setsockopt(zmq.SUBSCRIBE, b'')
        while True:
            message = sub_socket.recv_json()
            print(message)

    def sender(self):
        listen_thread = Thread(target=self.listener)
        listen_thread.daemon = True
        listen_thread.start()
        senders = self.context.socket(zmq.PUB)
        senders.bind("tcp://{}:{}".format(self.interface, self.pub_port))
        while True:
            msg = input()
            senders.send_json(msg)


if __name__ == '__main__':
    interface = '*'
    sub_port = '5555'
    pub_port = '5556'
    host = 'localhost'
    client = StandaloneClient(interface, sub_port, pub_port, host)
    client.sender()
