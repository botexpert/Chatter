import zmq
from threading import Thread
import time
import json

class Server:
    def __init__(self,address,rcv_port,server_id):
        self.address=address
        self.recv_port=rcv_port
        self.server_id=server_id.encode()
        self.contex=zmq.Context.instance()
        self.recv_socket=None

    def server_bind (self):
        self.recv_socket = self.contex.socket(zmq.ROUTER)
        self.recv_socket.setsockopt(zmq.IDENTITY,self.server_id)
        bind_address_rcv = 'tcp://{}:{}'.format(self.address,self.recv_port)
        self.recv_socket.bind(bind_address_rcv)
        print('Socket Binded')

    def recieve_message(self):
        ID,data_raw = self.recv_socket.recv_multipart()
        data=json.loads(data_raw)
        TO = data['to']
        message = data['message']
        print('{}sent to {}: {}'.format(ID,TO,message))
        return ID.decode('utf-8'),TO.encode(),message


    def send_message (self,client_id,client_to,client_message):
        data={'id':client_id,
              'message':client_message}
        s=json.dumps(data).encode()
        send_data=[client_to,s]
        self.recv_socket.send_multipart(send_data)
        '''routing_id=client_to'''

    def server_run(self):
        self.server_bind()
        poller=zmq.Poller()
        poller.register(self.recv_socket,zmq.POLLIN)
        print('socket Registered in poller')
        #receive = Thread(target=self.recieve_message())
        #receive.daemon = True
        #receive.start()
        while True:
            print('in while 1')
            events = dict(poller.poll(timeout=250))
            print('events done')
            while True:
                print('in while 2')
                if self.recv_socket in events:
                    ID,TO,new_message = self.recieve_message()
                    print('message received')
                    self.send_message(ID,TO,new_message)
                    print('message sent')
                    break
                else:
                    print('no messages')
                    break
