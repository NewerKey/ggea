import datetime
import uuid

import loguru
import pydantic
from password_strength import PasswordPolicy

from src.models.schema.base import BaseSchemaModel


class EmailInVerification(BaseSchemaModel):
    email: pydantic.EmailStr
    verification_code: int
