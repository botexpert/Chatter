'''Login server for zmq client-server-client communication'''
import hashlib
import sqlite3
import sys
import threading
import time
from uuid import uuid1
import zmq
from enums_server import Host


class LoginServer(threading.Thread):
    '''Login server class'''

    def __init__(self):
        self.database = None
        self.db_name = Host.DATABASE
        self.context = zmq.Context.instance()
        self.login_socket = self.context.socket(zmq.REP)
        threading.Thread.__init__(self, daemon=True)

    # Receives requests and unpacks their data.
    # Calls for a credential check and generates a token if successful
    def run(self):
        '''Main server program, running all functionalities'''
        self.login_socket.bind("tcp://{}:{}".format(Host.ADDRESS, Host.LOGIN_PORT))
        print('Login socket bound!')

        self.database = sqlite3.connect(Host.DATABASE)
        cursor = self.database.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS tokens(
                        username TEXT UNIQUE,token TEXT UNIQUE, timestamp TEXT)""")
        self.database.commit()
        try:
            while True:
                data = self.login_socket.recv_json()  # recieves username and password
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
                    token = 'Not allowed'
                    reply = {'try_again': True,
                             'token': token}
                    self.login_socket.send_json(reply)
        except (KeyboardInterrupt, SystemExit):
            print('\nClosing login server...')
            sys.exit(1)
        except zmq.ContextTerminated:
            print('\nMain server Context unavailable,closing login server...')
            sys.exit(0)

    # Checks the database for the username and password pair.
    def check_credentials(self, data, datab) -> bool:
        '''Method for checking username,password pair credibility'''
        username = data['username']
        password = data['password']
        enc_pass = self.pass_encript(username, password)
        credentials = (username, enc_pass)
        print(credentials)
        cursor = datab.cursor()
        cursor.execute("SELECT username,password FROM users")
        # users = cursor.fetchall()
        # if credentials in users:
        if any(credentials == pair for pair in cursor):
            print('Successful login for user {}'.format(username))
            return True
        print('Failed login attempt. Bad username {} or password {}.'.format(username,password))
        return False

    @staticmethod
    def pass_encript(username, password):
        '''Encription of password'''
        salt = username.encode() + password.encode()
        key = hashlib.pbkdf2_hmac(
            'sha256',  # The hash digest algorithm for HMAC
            password.encode('utf-8'),  # Convert the password to bytes
            salt,  # Provide the salt
            100000  # It is recommended to use at least 100,000 iterations of SHA-256
        )
        return key
