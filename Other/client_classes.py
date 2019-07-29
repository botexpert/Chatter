import zmq
from threading import Thread
import time
import json


class StandaloneClient:
    def __init__(self, interface, host, user, target):
        self.interface = interface
        self.host = host
        self.connect_port = target.message_port
        self.bind_port = user.message_port
        self.heart_port = user.heart_port
        self.echo_port = target.heart_port
        self.context = zmq.Context.instance()
        self.ID = user.name
        self.target_ID = target.name

    def run(self):
        heart_thread = Thread(target=self.heart, name='heart_thread')
        heart_thread.daemon = True
        heart_thread.start()
        echo_thread = Thread(target=self.echo, name='echo_thread')
        echo_thread.daemon = True
        echo_thread.start()
        listen_thread = Thread(target=self.listener, name='listener_thread')
        listen_thread.daemon = True
        listen_thread.start()
        self.sender()

    # This part opens up the sockets for receiving messages and loops the
    # new message check, that will be improved later.
    def listener(self):
        listen_socket = self.context.socket(zmq.DEALER)
        listen_socket.setsockopt(zmq.IDENTITY, self.ID)
        listen_socket.connect(
            "tcp://{}:{}".format(self.host, self.connect_port))
        while True:
            if listen_socket.poll():
                message = listen_socket.recv_json()
                print(message)

    # This part starts a separate thread that activates the receiving part of
    # the client, enabling messages to come while the user is inputting a new
    # message.
    def sender(self):
        sender_socket = self.context.socket(zmq.ROUTER)
        sender_socket.bind(
            "tcp://{}:{}".format(self.interface, self.bind_port))
        while True:
            send_text = json.dumps(input()).encode()
            send_message = [self.target_ID, send_text]
            sender_socket.send_multipart(send_message)

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

        while True:
            echo_socket.send(b"ping")
            if not echo_socket.poll(2500):
                print('The other client is offline.')
                print('They might not receive sent messages.')


# Class consisting of basic user information.
class User:
    def __init__(self, name, message_port, heart_port):
        self.name = name.encode()
        self.message_port = message_port
        self.heart_port = heart_port
