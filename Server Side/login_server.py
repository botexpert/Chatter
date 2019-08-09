import threading
import sqlite3
import time
import random
from enums_server import Host
from uuid import uuid1
import zmq


class LoginServer(threading.Thread):
    def __init__(self, login_server_address, db):
        self.database = None
        self.db_name = Host.DATABASE
        self.context = zmq.Context.instance()
        self.login_server_address = login_server_address
        self.login_socket = self.context.socket(zmq.REP)
        threading.Thread.__init__(self)

    # Receives requests and unpacks their data.
    # Calls for a credential check and generates a token if successful
    def run(self):
        self.login_socket.bind("tcp://{}:{}".format(Host.ADDRESS, Host.LOGIN_PORT))
        print('Login socket bound!')

        self.database = sqlite3.connect(Host.DATABASE)
        cursor = self.database.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS tokens(
                        username TEXT,token TEXT UNIQUE, timestamp TEXT)""")
        self.database.commit()

        while True:
            try:
                data = self.login_socket.recv_json()  # recieves username and password
            except zmq.ContextTerminated:
                print('Main server unavailable,closing login server...')
                return 0

            username = data['username']

            if self.check_credentials(data, self.database):
                cursor.execute("SELECT username FROM tokens")
                if any(username == value for (value,) in cursor):
                    cursor.execute("UPDATE tokens SET timestamp = ? WHERE username = ?",
                                   (str(round(time.time())), username))
                    print('UPDATE')
                    cursor.execute("SELECT token FROM tokens WHERE username = ?", (username,))
                    (token,) = cursor.fetchone()
                    self.database.commit()
                else:
                    token = str(uuid1())
                    cursor.execute("INSERT INTO tokens VALUES (?,?,?)",
                                   (username, token, str(round(time.time()))))
                    print('NEW USER')
                    self.database.commit()
                reply = {'try_again': False,
                         'token': token}
                self.login_socket.send_json(reply)
            else:
                token = 'Not_allowed'
                reply = {'try_again': True,
                         'token': token}
                self.login_socket.send_json(reply)

    # Checks the database for the username and password pair.
    @staticmethod
    def check_credentials(data, datab) -> bool:
        username = data['username']
        password = data['password']
        credentials = (username, password)
        print(credentials)
        cursor = datab.cursor()
        cursor.execute("SELECT username,password FROM users")
        # users = cursor.fetchall()
        # if credentials in users:
        if any(credentials == pair for pair in cursor):
            print('Successful login for user {}'.format(username))
            return True
        print('Failed login attempt. User does not exist.')
        return False

    # def generate_token(self):
    #     # token is a 9 digit number
    #     num_token = round(random.randint(1, 100) * time.time())
    #     str_token = str(num_token)[:9]
    #     print('Token generated {}'.format(str_token))
    #     return str_token
