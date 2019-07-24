import zmq
from threading import Thread
import queue


class Client:
    def __init__(self, username, server_address, server_router_ID, target):
        self.context = zmq.Context.instance()
        self.username = username
        self.server_address = server_address
        self.q = queue.Queue()
        self.message = None
        self.server_router_ID = server_router_ID
        self.target = target

    def run(self):
        # heartbeat = Thread(target=self.heartbeat)
        # heartbeat.daemon = True
        # heartbeat.start()
        self.relay()

    def relay(self):
        main_socket = self.context.socket(zmq.DEALER)
        main_socket.setsockopt(zmq.IDENTITY, self.username.encode())
        main_socket.connect("tcp://localhost:{}".format(self.server_address))

        inputting = Thread(target=self.input_message)
        inputting.daemon = True
        inputting.start()

        while True:
            if main_socket.poll(1):
                incoming_message = main_socket.recv_json()
                self.message_received(incoming_message)
            if not self.q.empty():
                client_message = self.q.get()
                data = {'id': self.username,
                        'to': self.target,
                        'message': client_message}
                print(data)

                main_socket.send_json(data)

    def input_message(self):
        while True:
            self.message = input('message: ')
            self.q.put(self.message)

    @staticmethod
    def message_received(incoming_message):
        print(incoming_message)
        return

    # def heartbeat(self):
    # heart_socket = self.context.socket(zmq.DEALER)
    # heart_socket.setsockopt(zmq.IDENTITY, self.username)
    # heart_socket.connect("tcp://localhost:{}".format('5556'))
