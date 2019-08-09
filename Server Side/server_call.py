#!/usr/bin/env python3.7
'''Just creating server object and starting Server'''

import os.path
from server import Server

path: str = os.getcwd()
print(path)
Server: Server = Server()
Server.server_run()
