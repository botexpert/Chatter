import os


class Intervals:
    POLL_REFRESH_INTERVAL = 1
    HEARTBEAT_INTERVAL = 30
    TOKEN_CHECK_INTERVAL = 10
    TOKEN_EXPIRATION = 60
    POLL_IN_TIME = 2500


class Host:
    HOST = b'serverID'
    ADDRESS = '*'
    LOGIN_PORT = os.getenv('HOST', '5557')
    PORT = os.getenv('HOST', '5555')  # TODO make it an actual system value
    DATABASE = 'database.db'
