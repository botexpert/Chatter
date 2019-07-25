import zmq


class LoginServer:
    def __init__(self, login_server_address):
        self.context = zmq.Context.instance()
        self.login_server_address = login_server_address

    # Receives requests and unpacks their data. Calls for a credential
    # check and generates a token if successful
    def receive_request(self):
        login_socket = self.context.socket(zmq.REP)
        login_socket.bind(
            "tcp://*:{}".format(self.login_server_address))
        print('port bound')
        while True:
            if login_socket.poll(1):
                data = login_socket.recv_json()

                check = self.check_credentials(data)
                if check:
                    token = self.generate_token()
                    reply = {'try_again': False,
                             'token': token}
                    login_socket.send_json(reply)
                else:
                    token = 'Not_allowed'
                    reply = {'try_again': True,
                             'token': token}

                    login_socket.send_json(reply)

    # Intended to check the database for the username password pair.
    def check_credentials(self, data):
        a = data['username']
        b = data['password']
        if a == 'branko' and b == 'kralj':
            print('Successful login.')
            return True
        else:
            print('Failed login attempt.')

    # Generates a token upon successful identification.
    def generate_token(self):
        token = 'hoho'
        print('Token generated')
        return token


kola = LoginServer('5557')
kola.receive_request()
