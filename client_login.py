import zmq


class LoginClient:
    def __init__(self, login_server_address):
        self.context = zmq.Context.instance()
        self.login_server_address = login_server_address

    # Enables data input for username and password, and calls the client upon
    # login success.
    def login(self):
        try_again = True
        while try_again:
            username = input('Username: ')
            password = input('Password: ')
            data = {'username': username,
                    'password': password}
            [try_again, token] = self.login_request(data)
            if try_again:
                print('Login unauthorized! Try again.')
            else:
                return True  # add username return and implement later

    # Requests a credential check from login server.
    def login_request(self, data):
        login_socket = self.context.socket(zmq.REQ)
        login_socket.connect(
            "tcp://localhost:{}".format(self.login_server_address))

        login_socket.send_json(data)

        if login_socket.poll(1):
            reply = login_socket.recv_json()
            try_again = reply['try_again']
            token = reply['token']

        else:
            print(
                'Login server currently unavailable, please try again later.')
            try_again = True
            token = 'Not_allowed'

        return try_again, token
