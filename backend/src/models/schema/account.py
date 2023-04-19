import datetime
import uuid

import loguru
import pydantic
from password_strength import PasswordPolicy

from src.models.schema.base import BaseSchemaModel


class AccountInSignup(BaseSchemaModel):
    username: str
    email: pydantic.EmailStr
    password: str

    @pydantic.validator("password")
    def password_strength(cls, v):
        loguru.logger.info("Evaluating password strength")
        policy = PasswordPolicy.from_names(
            length=8,
            uppercase=1,
            numbers=1,
            special=1,
        )
        if policy.test(v) != []:
            raise ValueError("Password is not strong enough")
        return v


class AccountInOAuthSignIn(BaseSchemaModel):
    username: str
    password: str


class AccountInSignin(BaseSchemaModel):
    username: str
    email: pydantic.EmailStr
    password: str


class AccountInSignout(BaseSchemaModel):
    id: uuid.UUID


class AccountInRead(BaseSchemaModel):
    id: uuid.UUID | None
    username: str | None
    email: pydantic.EmailStr | None


class CurrentAccountInRead(BaseSchemaModel):
    username: str
    email: pydantic.EmailStr


class AccountInUpdate(BaseSchemaModel):
    username: str | None
    email: str | None
    password: str | None


class AccountWithToken(BaseSchemaModel):
    id: uuid.UUID
    token: str
    username: str
    email: pydantic.EmailStr
    hashed_password: str
    is_verified: bool
    is_logged_in: bool
    is_admin: bool
    is_otp_enabled: bool
    is_otp_verified: bool
    otp_secret: str | None
    otp_auth_url: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


class AccountInResponse(BaseSchemaModel):
    authorized_account: AccountWithToken


class AccountInSignupResponse(BaseSchemaModel):
    authorized_account: AccountWithToken
    is_profile_created: bool


class AccountInSignoutResponse(BaseSchemaModel):
    username: str
    is_logged_out: bool


class AccountInDeletionResponse(BaseSchemaModel):
    is_deleted: bool
