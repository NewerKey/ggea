class BaseException(Exception):
    """
    Base exception class.
    """
    def __init__(self, error_msg: str):
        self.error_msg = error_msg



class EntityDoesNotExist(BaseException):
    """
    Throw an exception when the dentity does not exist in the database.
    """


class EntityAlreadyExists(BaseException):
    """
    Throw an exception when the entity already exists in the database.
    """


class UsernameAlreadyExists(BaseException):
    """
    Throw an exception when the username already registered.
    """


class EmailAlreadyExists(BaseException):
    """
    Throw an exception when the email already registered.
    """


class PasswordDoesNotMatch(BaseException):
    """
    Throw an error if Account password doesn't match.
    """


class AccountIsNotVerified(BaseException):
    """
    Throw an error if Account is not verified.
    """

class AccountIsAlreadyVerified(BaseException):
    """
    Throw an error if Account is already verified.
    """

class VerificationCodeDoesNotMatch(BaseException):
    """
    Throw an error if Account verification code doesn't match.
    """


class FailedToSaveAccount(BaseException):
    """
    Throw an error if an error accured while saving the Account
    """
