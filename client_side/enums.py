import os


class Intervals:
    POLL_REFRESH_INTERVAL = 1000


class Host:
    HOST = 'dummy'
    PORT = os.getenv('HOST', '5557')
