import pyotp


def validate_otp(otp_token: int, otp_secret: str):
    totp = pyotp.TOTP(otp_secret)
    return totp.verify(otp_token, valid_window=1)


def separate_password_and_otp(input_str):
    password = input_str[:-6]
    otp_token = input_str[-6:]

    if len(password) < 8:
        raise ValueError("After removing OTP, password is too short")

    if len(otp_token) != 6:
        raise ValueError("OTP is not 6 digits long")

    return password, int(otp_token)
