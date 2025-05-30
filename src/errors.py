class UnrecoverableConnectionError(Exception):
    """raised when we simply cannot connect to rabbit anymore (even after retry logic is fulfilled)"""

    ...
