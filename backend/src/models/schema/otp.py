import datetime
import uuid

import loguru
import pydantic
from password_strength import PasswordPolicy

from src.models.schema.base import BaseSchemaModel


class OtpIn(BaseSchemaModel):
    otp_token: int
    email: pydantic.EmailStr


class OtpInGenerateResponse(BaseSchemaModel):
    is_valid: bool


class OtpInVerifyResponse(BaseSchemaModel):
    otp_secret: str
    otp_auth_url: str
