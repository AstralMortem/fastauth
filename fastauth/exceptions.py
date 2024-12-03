class FastAuthException(Exception):
    pass


class MissingAuthToken(FastAuthException):
    pass


class InvalidAuthToken(FastAuthException):
    pass
