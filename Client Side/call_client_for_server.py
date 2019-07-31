#!/usr/bin/env python3.7
from client_for_server import Client

send_to = input("Kome saljes: ")
client = Client('5555', b'serverID', send_to)
client.run()
