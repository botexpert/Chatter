#!/usr/bin/env python3.7
'''Just creating server object and starting Server'''

import os.path
from server import Server
from administrator import run as run_admin


def main():
    '''Main function printing working folder and running server'''
    path: str = os.getcwd()
    print(path)
    print("---------List of users---------")
    run_admin()
    print('--------------------------------')
    server = Server()
    server.server_run()


main()
