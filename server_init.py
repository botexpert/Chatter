from server_class import Server
#Server class : def __init__(self,address,rcv_port,server_id)
server = Server('127.0.0.1',5555,'serverID')
server.server_run()