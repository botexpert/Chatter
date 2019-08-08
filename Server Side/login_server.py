import zmq
import threading
import sqlite3
import time
import random
from enums_server import Host


class LoginServer(threading.Thread):
    def __init__(self):
        self.db_name = Host.DATABASE
        self.context = zmq.Context.instance()
        threading.Thread.__init__(self)

    # Receives requests and unpacks their data. Calls for a credential
    # check and generates a token if successful
    def run(self):
        login_socket = self.context.socket(zmq.REP)
        login_socket.bind(
            "tcp://{}:{}".format(Host.ADDRESS, Host.LOGIN_PORT))
        print('Login socket bound!')
        database = sqlite3.connect(Host.DATABASE)
        cursor = database.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS tokens(username TEXT,token TEXT UNIQUE, timestamp TEXT)""")
        database.commit()
        # thread for deleting tokens for users not currently online
        while True:
            try:
                data = login_socket.recv_json()  # receives username and password in json
            except zmq.ContextTerminated:
                print('Main server unavailable,closing login server...')
                return
            username = data['username']
            check = self.check_credentials(data, self.db_name)

            if check:
                # token = self.generate_token()
                cursor.execute("SELECT username FROM tokens")
                users = cursor.fetchall()
                # If user is active, update token. If not, create new token in base
                if (username,) in users:
                    cursor.execute(
                        "UPDATE tokens SET timestamp = ? WHERE username = ?",
                        (str(round(time.time())), username))
                    print('UPDATE')
                    cursor.execute(
                        "SELECT token FROM tokens WHERE username = ?",
                        (username,))
                    token = cursor.fetchone()
                    database.commit()
                else:
                    token = self.generate_token()
                    cursor.execute("INSERT INTO tokens VALUES (?,?,?)",
                                   (username, token, str(round(time.time()))))
                    print('NEW USER')
                    database.commit()
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
    def check_credentials(data, db_name):
        username = data['username']
        password = data['password']
        credentials = (username, password)
        print(credentials)
        database = sqlite3.connect(db_name)
        cursor = database.cursor()
        cursor.execute("SELECT username,password FROM users")
        users = cursor.fetchall()
        if credentials in users:
            print('Successful login for user {}'.format(username))
            database.close()
            return True
        print('Failed login attempt. User does not exist.')
        database.close()

    # Generates a token upon successful identification.
    @staticmethod
    def generate_token():
        # token is a 9 digit number
        num_token = round(random.randint(1, 100) * time.time())
        str_token = str(num_token)[:9]
        print('Token generated {}'.format(str_token))
        return str_token
