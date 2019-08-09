import os


class Intervals:
    POLL_REFRESH_INTERVAL = 1 # Receiving message check frequency
    HEARTBEAT_INTERVAL = 30 # Sent heartbeat frequency
    LOGIN_POLL_INTERVAL = 5000 # Wait time at login request


class Host:
    LOGIN_PORT = os.getenv('HOST', '5557')  # Login server port
    PORT = os.getenv('HOST', '5555')  # Main server port
    # TODO make it an actual system value
