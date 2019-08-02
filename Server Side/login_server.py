import zmq
import threading
import sqlite3
import time
import random


class LoginServer(threading.Thread):
    def __init__(self, login_server_address, db):
        self.db_name = db
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
        database = sqlite3.connect(self.db_name)
        cursor = database.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS tokens(username TEXT,token TEXT UNIQUE, timestamp TEXT)""")
        database.commit()
        while True:
            data = login_socket.recv_json()
            username = data['username']
            check = self.check_credentials(data, self.db_name)
            if check:
                token = self.generate_token()
                cursor.execute("SELECT username FROM tokens")
                users = cursor.fetchall()
                # If user is active, update token. If not, create new token in base
                if (username,) in users:
                    cursor.execute("UPDATE tokens SET token = ?, timestamp = ? WHERE username = ?",
                                   (token, str(time.asctime(time.localtime(time.time()))), username))
                    print('UPDATE')
                    database.commit()
                else:
                    cursor.execute("INSERT INTO tokens VALUES (?,?,?)",
                                   (username, token, str(time.asctime(time.localtime(time.time())))))
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
    def generate_token(self):
        # token is 9 digit number
        num_token = round(random.randint(1, 100) * time.time())
        str_token = str(num_token)[:9]
        print('Token generated {}'.format(str_token))
        return str_token
