import zmq
from threading import Thread
import time

class Server:
    def __init__(self,address,rcv_port,snd_port):
        self.address=address
        self.recv_port=rcv_port
        self.send_port=snd_port
        self.contex=zmq.Context.instance()
        self.recv_socket=None
        self.send_socket=None

    def server_bind (self):
        self.recv_socket = self.contex.socket(zmq.ROUTER)
        bind_address_rcv = 'tcp://{}:{}'.format(self.address,self.recv_port)
        self.recv_socket.bind(bind_address_rcv)

        self.send_socket = self.contex.socket(zmq.ROUTER)
        bind_address_snd = 'tcp://{}:{}'.format(self.address,self.send_port)
        self.send_socket.bind(bind_address_snd)

    def recieve_message(self):
        data = self.send_socket.recv_json()
        ID = data['id']
        message = data['message']
        return ID,message

    def send_message (self,client_id,client_message):
        self.send_socket.send(b'{}sent: {}' % client_id %client_message)

    def server_run(self):
        self.server_bind()
        receive = Thread(target=self.recieve_message())
        receive.daemon = True
        receive.start()
        while True:
            if self.recv_socket.poll(1):
                ID,new_message = self.recieve_message()
                self.send_message(ID,new_message)
