import zmq
from threading import Thread
import queue
from client_login import LoginClient
from enums import Host
import time


class Client:
    def __init__(self, server_address, target):
        self.context = zmq.Context.instance()
        self.username = None
        self.server_address = server_address
        self.queue = queue.Queue()
        self.message = None
        self.target = target
        self.token = None

    def run(self):
        self.username, self.token = LoginClient(Host.PORT).login()
        self.main()

        # heartbeat

    def main(self):
        main_socket = self.context.socket(zmq.DEALER)
        main_socket.setsockopt(zmq.IDENTITY, self.username.encode())
        main_socket.connect("tcp://localhost:{}".format(self.server_address))
        print('Client connected!\n')

        relay = ClientRelay(main_socket, self.queue, self.target, self.token)
        relay.start()
        while True:
            self.message = input('')
            self.queue.put(self.message)


class ClientRelay(Thread):
    def __init__(self, main_socket, msg_queue, target, token):
        self.main_socket = main_socket
        self.msg_queue = msg_queue
        self.target = target
        self.token = token
        Thread.__init__(self)

    def run(self):
        heartbeat=Thread(target= self.heartbeat)
        heartbeat.start()
        while True:
            if self.main_socket.poll(1):
                incoming_message = self.main_socket.recv_json()
                self.message_received(incoming_message)
            if not self.msg_queue.empty():
                client_message = self.msg_queue.get()
                data = {
                    'to': self.target,
                    'token': self.token,
                    'message': client_message}

                self.main_socket.send_json(data)

    def message_received(self, incoming_message):

        id_ = incoming_message['id']
        new_message = incoming_message['message']
        if new_message == 'Your token expired!':
            print(
                'WARNING : YOUR SESSION HAS EXPIRED, RESTART THE CLIENT OR RELOG!!!')
        if id_ == self.target:
                print('{}: {}'.format(id_, new_message))

        return

    def heartbeat(self):
        data = {
            'to': 'ping',
            'token': self.token,
            'message': None
        }
        while True:
            time.sleep(30)
            self.main_socket.send_json(data)
