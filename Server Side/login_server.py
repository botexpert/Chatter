import zmq
import threading
import sqlite3
import time
import random


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
            username = data['username']
            check = self.check_credentials(data)
            if check:
                token = self.generate_token()
                database = sqlite3.connect('user_database.db')
                cursor = database.cursor()
                cursor.execute("SELECT username FROM tokens")
                users = cursor.fetchall()
                print (users)
                #If user is active, update token. If not, create new token in base
                if (username,) in users:
                    cursor.execute("UPDATE tokens SET token = ?, timestamp = ? WHERE username = ?",(token ,str(time.asctime(time.localtime(time.time()))),username))
                    print('UPDATE')
                else:
                    cursor.execute("INSERT INTO tokens VALUES (?,?,?)",
                               (username, token, str(time.asctime(time.localtime(time.time())))))
                    print('NEW USER')
                database.commit()
                #database.close()
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

        if credentials in users:
            print('Successful login for user {}'.format(username))
            database.close()
            return True
        print('Failed login attempt. User does not exist.')
        database.close()

    # Generates a token upon successful identification.
    def generate_token(self):
        db = sqlite3.connect('user_database.db')
        c = db.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS tokens(username text,token text, timestamp texts)""")
        db.commit()
        db.close()
        num_token = round(random.randint(1, 100) * time.time())
        str_token = str(num_token)[:9]
        print('Token generated {}'.format(str_token))
        return str_token
