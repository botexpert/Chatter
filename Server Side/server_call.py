#!/usr/bin/env python3.7
from server import Server

server = Server('*', 5555)
server.server_run()
