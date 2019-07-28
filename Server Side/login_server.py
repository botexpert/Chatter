import zmq
import threading
import sqlite3


class LoginServer(threading.Thread):
    def __init__(self, login_server_address):
        self.context = zmq.Context.instance()
        self.login_server_address = login_server_address
        threading.Thread.__init__(self)

    # Receives requests and unpacks their data. Calls for a credential
    # check and generates a token if successful
    def run(self):
        login_socket = self.context.socket(zmq.REP)
        login_socket.bind(
            "tcp://*:{}".format(self.login_server_address))
        print('Login socket bound!')

        while True:
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

    # Checks the database for the username and password pair.
    @staticmethod
    def check_credentials(data):
        username = data['username']
        password = data['password']
        credentials = (username, password)
        print(credentials)
        database = sqlite3.connect('user_database.db')
        cursor = database.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        for i in range(len(users)):
            if credentials in users:
                print('Successful login for user {}'.format(username))
                return True
        print('Failed login attempt. User does not exist.')

    # Generates a token upon successful identification.
    def generate_token(self):
        token = 'hoho'
        print('Token generated')
        return token
