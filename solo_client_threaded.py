import zmq
from threading import Thread
import time


class StandaloneClient():
    def __init__(self, interface, sub_port, pub_port, host, heart_port,
                 echo_port):
        self.interface = interface
        self.sub_port = sub_port
        self.pub_port = pub_port
        self.host = host
        self.heart_port = heart_port
        self.echo_port = echo_port
        self.context = zmq.Context.instance()

        heart_thread = Thread(target=self.heart, name='heart_thread')
        heart_thread.daemon = True
        heart_thread.start()
        echo_thread = Thread(target=self.echo, name='echo_thread')
        echo_thread.daemon = True
        echo_thread.start()

    # This part opens up the sockets for receiving messages and loops the
    # new message check, that will be improved later.
    def listener(self):
        sub_socket = self.context.socket(zmq.SUB)
        sub_socket.setsockopt(zmq.SUBSCRIBE, b'')
        sub_socket.connect("tcp://{}:{}".format(self.host, self.sub_port))
        while True:
            message = sub_socket.recv_json()
            print(message)

    # This part starts a separate thread that activates the receiving part of
    # the client, enabling messages to come while the user is inputing a new
    # message.
    def sender(self):
        listen_thread = Thread(target=self.listener, name='listener_thread')
        listen_thread.daemon = True
        listen_thread.start()
        senders = self.context.socket(zmq.PUB)
        senders.bind("tcp://{}:{}".format(self.interface, self.pub_port))
        while True:
            msg = input()
            senders.send_json(msg)
    # Waits for ping from other client and responds if alive.
    def heart(self):
        heart_socket = self.context.socket(zmq.REP)
        heart_socket.bind(
            "tcp://{}:{}".format(self.interface, self.heart_port))
        while True:
            time.sleep(1)
            heart_socket.recv()
            heart_socket.send(b"pong")
    # Pings at intervals at the other client and detects if there is a
    # response within the time limit. Ping interval should be changed.
    def echo(self):
        echo_socket = self.context.socket(zmq.REQ)
        echo_socket.connect("tcp://{}:{}".format(self.host, self.echo_port))
        echo_socket.setsockopt(zmq.REQ_RELAXED, 1)

        poller = zmq.Poller()
        poller.register(echo_socket, zmq.POLLIN)
        while True:
            time.sleep(1)

            echo_socket.send(b"ping")
            poll_check = (poller.poll(2500))
            if poll_check:
                message = echo_socket.recv()
            else:
                print('The other client is offline.')
                print('They might not receive sent messages.')


# Should be replaced with a better variety of setup options.
# Currently based on manual input for both sides.
if __name__ == '__main__':
    interface = '*'
    sub_port = '5555'
    pub_port = '5556'
    host = 'localhost'
    heart_port = '7777'
    echo_port = '7778'
    client = StandaloneClient(interface, sub_port, pub_port, host, heart_port,
                              echo_port)
    client.sender()
