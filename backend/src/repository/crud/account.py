import datetime
import typing
import uuid
from random import randint

import fastapi
import loguru
import pydantic
import sqlalchemy
from sqlalchemy.orm import selectinload as sqlalchemy_selectinload
from sqlalchemy.sql import functions as sqlalchemy_functions

from src.models.db.account import Account
from src.models.schema.account import (
    AccountInRead,
    AccountInSignin,
    AccountInSignout,
    AccountInSignup,
    AccountInStateUpdate,
    AccountInUpdate,
    AccountInVerification,
)
from src.repository.crud.base import BaseCRUDRepository
from src.security.authorizations import two_factor_auth
from src.utility.exceptions.custom import (
    AccountIsAlreadyVerified,
    AccountIsNotVerified,
    EntityDoesNotExist,
    FailedToSaveAccount,
    PasswordDoesNotMatch,
    VerificationCodeDoesNotMatch,
)
from src.utility.exceptions.database import DatabaseError
from src.utility.exceptions.http.exc_400 import (
    http_exc_400_credentials_bad_signup_request,
)
from src.utility.typing.account import (
    AccountForInput,
    AccountForUpdate,
    AccountRetriever,
    Accounts,
)


class AccountCRUDRepository(BaseCRUDRepository):
    async def create_account(self, account_signup: AccountInSignup) -> Account:
        new_account = Account(**account_signup.dict(exclude={"password"}))
        new_account.hashed_salt, new_account.hashed_password = new_account.set_password(
            password=account_signup.password
        )
        new_account.verification_code = randint(100000, 999999)

        try:
            self.async_session.add(instance=new_account)
            await self.async_session.commit()
            await self.async_session.refresh(instance=new_account)
            await self.async_session.close()

        except Exception as e:
            await self.async_session.rollback()
            loguru.logger.error(e)
            raise FailedToSaveAccount(error_msg="Failed to create account")

        return new_account

    async def _is_username_available(self, username: str) -> bool:
        select_stmt = (
            sqlalchemy.select(Account.username)
            .select_from(Account)
            .where(Account.username == username)
        )
        query = await self.async_session.execute(select_stmt)
        db_username = query.scalar()
        if db_username:
            return False
        return True

    async def _is_email_available(self, email: str) -> bool:
        select_stmt = (
            sqlalchemy.select(Account.email)
            .select_from(Account)
            .where(Account.email == email)
        )
        query = await self.async_session.execute(select_stmt)
        db_email = query.scalar()
        if db_email:
            return False
        return True

    async def is_credentials_available(self, account_input: AccountForInput) -> bool:
        if account_input.email:
            is_email_available = await self._is_email_available(
                email=account_input.email
            )
            if not is_email_available:
                return False

        if account_input.username:
            is_username_taken = await self._is_username_available(
                username=account_input.username
            )
            if not is_username_taken:
                return False

        if not account_input.email and not account_input.username:
            return False
        return True

    async def read_accounts(self) -> Accounts:
        try:
            select_stmt = sqlalchemy.select(Account).options(
                sqlalchemy_selectinload("*")
            )
            query = await self.async_session.execute(statement=select_stmt)
            return query.scalars().all()
        except Exception as e:
            loguru.logger.error(e)
            raise DatabaseError("Failed to read accounts from database!")

    async def read_account(self, account_in_read: AccountInRead) -> Account:
        if account_in_read.id:
            db_account = await self._read_account_by_id(id=account_in_read.id)
        elif account_in_read.username:
            db_account = await self._read_account_by_username(
                username=account_in_read.username
            )
        elif account_in_read.email:
            db_account = await self._read_account_by_email(email=account_in_read.email)

        if not db_account:
            raise EntityDoesNotExist(f"Account with these details does not exist!")

        if not await self._check_db_account_matches_account_in_read(
            db_account=db_account, account_in_read=account_in_read
        ):
            raise EntityDoesNotExist(f"Account with these details does not exist!")

        else:
            return db_account

    async def _check_db_account_matches_account_in_read(
        self, db_account: Account, account_in_read: AccountInRead
    ) -> bool:
        if account_in_read.id:
            if db_account.id != account_in_read.id:
                return False
        if account_in_read.username:
            if db_account.username != account_in_read.username:
                return False
        if account_in_read.email:
            if db_account.email != account_in_read.email:
                return False
        return True

    async def _read_account_by_id(self, id: uuid.UUID) -> Account:
        select_stmt = sqlalchemy.select(Account).where(Account.id == id)
        query = await self.async_session.execute(statement=select_stmt)
        if not query:
            raise EntityDoesNotExist(f"Account with id `{id}` does not exist!")
        return query.scalar()  # type: ignore

    async def _read_account_by_username(self, username: str) -> Account:
        select_stmt = sqlalchemy.select(Account).where(Account.username == username)
        query = await self.async_session.execute(statement=select_stmt)
        if not query:
            raise EntityDoesNotExist(
                f"Account with username `{username}` does not exist!"
            )
        return query.scalar()  # type: ignore

    async def _read_account_by_email(self, email: pydantic.EmailStr) -> Account:
        select_stmt = sqlalchemy.select(Account).where(Account.email == email)
        query = await self.async_session.execute(statement=select_stmt)
        if not query:
            raise EntityDoesNotExist(f"Account with email `{email}` does not exist!")
        return query.scalar()  # type: ignore

    async def update_account(
        self, account_in_read: AccountInRead, account_update: AccountForUpdate
    ) -> Account:
        update_data = account_update.dict(exclude_unset=True)
        db_account = await self.read_account(account_in_read=account_in_read)

        if not db_account:
            raise EntityDoesNotExist(f"Account with that details does not exist!")  # type: ignore

        update_stmt = (
            sqlalchemy.update(table=Account)
            .where(Account.id == db_account.id)
            .values(updated_at=sqlalchemy_functions.now())
        )  # type: ignore

        for key, value in update_data.items():
            if key == "password":
                salt, password = db_account.set_password(
                    password=update_data["password"]
                )
                update_stmt = update_stmt.values(
                    hashed_salt=salt, hashed_password=password
                )
                loguru.logger.debug(f"Updating {key} to {value}")
            else:
                update_stmt = update_stmt.values(**{key: value})
                loguru.logger.debug(f"Updating {key} to {value}")

        try:
            await self.async_session.execute(statement=update_stmt)
            await self.async_session.commit()
            await self.async_session.refresh(instance=db_account)
            return db_account

        except Exception as e:
            await self.async_session.rollback()
            loguru.logger.error(e)
            raise DatabaseError(error_msg="Failed to update account in database!")

    async def set_otp_details(self, account: Account) -> tuple[Account, str, str]:
        db_account = await self._read_account_by_id(id=account.id)

        if not db_account:
            raise EntityDoesNotExist(f"Account with that id does not exist!")  # type: ignore

        otp_secret, otp_auth_url = two_factor_auth.generate_otp()

        update_stmt = (
            sqlalchemy.update(table=Account)
            .where(Account.id == db_account.id)
            .values(
                otp_secret=otp_secret,
                otp_auth_url=otp_auth_url,
                is_otp_enabled=True,
                updated_at=sqlalchemy_functions.now(),
            )
        )
        await self.async_session.execute(statement=update_stmt)
        await self.async_session.commit()
        await self.async_session.refresh(instance=db_account)
        return (db_account, otp_secret, otp_auth_url)

    async def delete_account(self, account_in_read: AccountInRead) -> bool:
        db_account = await self.read_account(account_in_read=account_in_read)

        if not db_account:
            raise EntityDoesNotExist(f"Account with these details does not exist!")

        try:
            delete_stmt = sqlalchemy.delete(table=Account).where(
                Account.id == db_account.id
            )
            await self.async_session.execute(statement=delete_stmt)
            await self.async_session.commit()
            return True
        except Exception as e:
            await self.async_session.rollback()
            loguru.logger.error(e)
            raise DatabaseError(error_msg="Failed to delete account from database!")

    async def signin_account(self, account_signin: AccountInSignin) -> Account:
        db_account = await self.read_account(
            account_in_read=AccountInRead(username=account_signin.username)
        )

        if not db_account:
            raise EntityDoesNotExist("Wrong username or wrong email!")

        if not db_account.is_verified:
            raise AccountIsNotVerified(
                "Account is not verified! Please verify your account first."
            )

        if not db_account.is_password_verified(password=account_signin.password):
            raise PasswordDoesNotMatch("Password does not match! Please try again.")

        db_account = await self.update_account(
            AccountInRead(id=db_account.id),
            account_update=AccountInStateUpdate(
                is_logged_in=True, credentials_validated_at=datetime.datetime.utcnow()
            ),
        )
        return db_account

    async def signout_account(self, account_signout: AccountInSignout) -> Account:
        try:
            db_account = await self._read_account_by_id(id=account_signout.id)  # type: ignore
            update_stmt = (
                sqlalchemy.update(table=Account)
                .where(Account.id == db_account.id)
                .values(is_logged_in=False)
            )
            await self.async_session.execute(statement=update_stmt)
            await self.async_session.commit()
            await self.async_session.refresh(instance=db_account)
            return db_account
        except Exception:
            await self.async_session.rollback()
            raise Exception("Failed to signout account, try again!")

    async def is_otp_enabled(self, username: str) -> bool:
        db_account = await self._read_account_by_username(username=username)

        if not db_account:
            raise EntityDoesNotExist(
                f"Account with username `{username}` does not exist!"
            )

        return db_account.is_otp_enabled

    async def verify_account(
        self, account_in_verification: AccountInVerification
    ) -> bool:
        db_account = await self._read_account_by_email(
            email=account_in_verification.email
        )

        if not db_account:
            raise EntityDoesNotExist(f"Account with email does not exist!")

        if db_account.is_verified:
            raise AccountIsAlreadyVerified("Account is already verified!")

        if db_account.verification_code != account_in_verification.verification_code:
            raise VerificationCodeDoesNotMatch("Verification code does not match!")

        else:
            update_stmt = (
                sqlalchemy.update(table=Account)
                .where(Account.id == db_account.id)
                .values(is_verified=True)
            )
            await self.async_session.execute(statement=update_stmt)
            await self.async_session.commit()
            await self.async_session.refresh(instance=db_account)
            return True
