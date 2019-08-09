#!/usr/bin/env python3.7
from server import Server
import os.path

put = os.getcwd()
print(put)
server = Server()
#try:
server.server_run()
#except(KeyboardInterrupt, SystemExit):
#   server.context.destroy()
