from Other.client_classes import User, StandaloneClient

interface = '*'
host = 'localhost'
Dragan = User('Dragan', '5555', '7777')
Boban = User('Boban', '5556', '7778')

client = StandaloneClient(interface, host, Boban, Dragan)
client.sender()
