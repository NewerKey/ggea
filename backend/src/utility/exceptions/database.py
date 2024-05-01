from src.utility.exceptions.base_exception import BaseException


class DatabaseError(BaseException):
    """
    Throw an exception when there is an error in the database.
    """
