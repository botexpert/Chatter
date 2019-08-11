'''Script for adding new users to database'''
import sqlite3
import hashlib
from enums_server import Host


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


def run():
    '''main program that creates new users in database

    Users are created by adding tuple(username,password) to list "korisnici" '''

    try:
        database = sqlite3.connect(Host.DATABASE)
        cursor = database.cursor()
        korisnici = {('admin', 'admin'), ('pera', 'pera'), ('zika', 'zika'),('mika','mika')}
        for user in korisnici:
            password = pass_encript(user[0], user[1])
            try:
                cursor.execute("INSERT INTO users(username,password) VALUES (?,?)", (user[0], password))
                print('New user {}'.format(user[0]))
            except sqlite3.IntegrityError:
                print('User {}'.format(user[0]))
                continue
        database.commit()
        database.close()
    except:
        print('Cannot create new users...')

