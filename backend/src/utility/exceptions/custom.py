class EntityDoesNotExist(Exception):
    """
    Throw an exception when the dentity does not exist in the database.
    """


class EntityAlreadyExists(Exception):
    """
    Throw an exception when the entity already exists in the database.
    """


class UsernameAlreadyExists(Exception):
    """
    Throw an exception when the username already registered.
    """


class EmailAlreadyExists(Exception):
    """
    Throw an exception when the email already registered.
    """


class PasswordDoesNotMatch(Exception):
    """
    Throw an error if Account password doesn't match.
    """


class AccountIsNotVerified(Exception):
    """
    Throw an error if Account is not verified.
    """

class AccountIsAlreadyVerified(Exception):
    """
    Throw an error if Account is already verified.
    """

class VerificationCodeDoesNotMatch(Exception):
    """
    Throw an error if Account verification code doesn't match.
    """


class FailedToSaveAccount(Exception):
    """
    Throw an error if an error accured while saving the Account
    """
