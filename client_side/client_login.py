import zmq


class LoginClient:
    def __init__(self, login_server_address):
        self.context = zmq.Context.instance()
        self.login_server_address = login_server_address
        self.token = None
        self.try_again = None

    # Enables data input for username and password, and calls the client upon
    # login success.
    def login(self):
        while True:
            username = input('Username: ')
            password = input('Password: ')
            data = {'username': username, 'password': password}
            self.login_request(data)
            if self.try_again is True:
                print('Login unauthorized! Try again.')
            else:
                return username, self.token # username gets set as this client's name

    # Requests a credential check from login server.
    def login_request(self, data):
        login_socket = self.context.socket(zmq.REQ)
        login_socket.connect(
            "tcp://localhost:{}".format(self.login_server_address))

        login_socket.send_json(data)

        if login_socket.poll(5000):
            reply = login_socket.recv_json()
            self.try_again = reply['try_again']
            self.token = reply['token']

        else:
            print('Login error, please try again.')
            self.try_again = True
            self.token = 'Not_allowed'
