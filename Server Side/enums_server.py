import os


class Intervals:
    TOKEN_CHECK_INTERVAL = 10 # Frequency of checking expired tokens
    TOKEN_EXPIRATION = 60  # Time of expiration for sessions
    POLL_IN_TIME = 2500  # Frequency of message refreshing


class Host:
    HOST = b'serverID' # Server socket IDENTITY
    ADDRESS = '*'   # Localhost for now?
    LOGIN_PORT = os.getenv('HOST', '5557')  # Login server port
    PORT = os.getenv('HOST', '5555')  # Main server port
    # TODO make it an actual system value
    DATABASE = 'database.db' # Name of storage database
