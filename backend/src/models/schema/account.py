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

    @pydantic.validator("username")
    def username_length(cls, v):
        loguru.logger.info("Evaluating username length")
        if len(v) < 4:
            raise ValueError("Username is too short")
        return v


class AccountInSignin(BaseSchemaModel):
    username: str
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


class AccountInStateUpdate(BaseSchemaModel):
    is_logged_in: bool | None
    is_verified: bool | None
    is_admin: bool | None
    is_otp_enabled: bool | None
    is_otp_verified: bool | None
    credentials_validated_at: datetime.datetime | None


class AccountWithToken(BaseSchemaModel):
    id: uuid.UUID
    token: str
    username: str
    email: pydantic.EmailStr
    is_verified: bool
    is_logged_in: bool
    is_admin: bool
    is_otp_enabled: bool
    is_otp_verified: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    credentials_validated_at: datetime.datetime | None


class AccountInResponse(BaseSchemaModel):
    authorized_account: AccountWithToken | None


class AccountInSignupResponse(BaseSchemaModel):
    username: str
    email: pydantic.EmailStr
    is_profile_created: bool


class AccountInSignoutResponse(BaseSchemaModel):
    username: str
    is_logged_out: bool


class AccountInDeletionResponse(BaseSchemaModel):
    is_deleted: bool


class AccountInVerification(BaseSchemaModel):
    email: pydantic.EmailStr
    verification_code: int


class AccountOutVerification(BaseSchemaModel):
    email: pydantic.EmailStr
    is_verified: bool


class AccountOutPublic(BaseSchemaModel):
    username: str
    email: pydantic.EmailStr
