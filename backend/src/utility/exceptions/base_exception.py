class BaseException(Exception):
    """
    Base exception class.
    """
    def __init__(self, error_msg: str):
        self.error_msg = error_msg

