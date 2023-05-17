import typing
import uuid

import loguru
import sqlalchemy
from sqlalchemy.sql import functions as sqlalchemy_functions

from src.models.db.account import Account
from src.models.db.profile import Profile
from src.models.schema.profile import ProfileInUpdate
from src.repository.crud.base import BaseCRUDRepository
from src.utility.exceptions.custom import EntityDoesNotExist
from src.utility.exceptions.database import DatabaseError


class ProfileCRUDRepository(BaseCRUDRepository):
    async def create_profile(self, parent_account: Account) -> Profile:
        try:
            new_profile = Profile(
                account=parent_account,
            )
            self.async_session.add(instance=new_profile)
            await self.async_session.commit()
            await self.async_session.refresh(instance=new_profile)
            await self.async_session.close()
            return new_profile
        except Exception as e:
            loguru.logger.error(e)
            raise DatabaseError(error_msg="Failed to create profile")

    async def read_profiles(self) -> typing.Sequence[Profile]:
        stmt = sqlalchemy.select(Profile)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()

    async def read_profile_by_id(self, id: uuid.UUID) -> Profile:
        try:
            stmt = sqlalchemy.select(Profile).where(Profile.id == id)
            query = await self.async_session.execute(statement=stmt)

            if not query:
                raise EntityDoesNotExist(error_msg=f"Profile with that ID does not exist")

            return query.scalar()
        except Exception as e:
            loguru.logger.error(e)
            raise DatabaseError(error_msg="Failed to read profile by id")

    async def read_profile_by_account_id(self, account_id: int) -> Profile:
        try:
            stmt = sqlalchemy.select(Profile).where(Profile.account_id == account_id)
            query = await self.async_session.execute(statement=stmt)

            if not query:
                raise EntityDoesNotExist(error_msg=f"Profile related to that account ID does not exist")

            loguru.logger.info(f"Closing db session of profile...")
            await self.async_session.close()
            loguru.logger.info(f"Closed db session of profile")

            return query.scalar()

        except Exception as e:
            loguru.logger.error(e)
            raise DatabaseError(error_msg="Failed to read profile by account id")

    async def read_profile_by_first_name(self, first_name: str) -> Profile:
        try:
            stmt = sqlalchemy.select(Profile).where(Profile.first_name == first_name)
            query = await self.async_session.execute(statement=stmt)

            if not query:
                raise EntityDoesNotExist(error_msg=f"Profile with that first name does not exist")

            return query.scalar()
        except Exception as e:
            loguru.logger.error(e)
            raise DatabaseError(error_msg="Failed to read profile by first name")

    async def read_profile_by_last_name(self, last_name: str) -> Profile:
        try:
            stmt = sqlalchemy.select(Profile).where(Profile.last_name == last_name)
            query = await self.async_session.execute(statement=stmt)

            if not query:
                raise EntityDoesNotExist(error_msg=f"Profile with that last name does not exist")

            return query.scalar()
        except Exception as e:
            loguru.logger.error(e)
            raise DatabaseError(error_msg="Failed to read profile by last name")

    async def update_profile_by_id(self, id: uuid.UUID, profile_update: ProfileInUpdate) -> Profile:
        new_profile_data = profile_update.dict(exclude_unset=True)
        current_profile = await self.read_profile_by_id(id)

        if not current_profile:
            raise EntityDoesNotExist(f"Profile with that ID does not exist!")  # type: ignore

        update_stmt = (
            sqlalchemy.update(table=Profile)
            .where(Profile.id == current_profile.id)
            .values(updated_at=sqlalchemy_functions.now())
        )

        if new_profile_data["first_name"]:
            update_stmt = update_stmt.values(first_name=new_profile_data["first_name"])

        if new_profile_data["last_name"]:
            update_stmt = update_stmt.values(last_name=new_profile_data["last_name"])

        # if new_profile_data["photo"]:

        #     try:

        #         #TODO:  1. Getting the name # type: ignore
        #         #       2. Uploading the photo to somewhere
        #     except:

        try:
            await self.async_session.execute(statement=update_stmt)
            await self.async_session.commit()
            await self.async_session.refresh(instance=current_profile)

            return current_profile

        except Exception as e:
            loguru.logger.error(e)
            raise DatabaseError(error_msg="Failed to update profile by id")

    async def delete_profile_by_id(self, id: uuid.UUID) -> str:
        delete_profile = await self.read_profile_by_id(id)

        try:
            delete_stmt = sqlalchemy.delete(Profile).where(Profile.id == delete_profile.id)

            await self.async_session.execute(statement=delete_stmt)
            await self.async_session.commit()

            return f"Profile with id '{id}' is successfully deleted!"

        except Exception as e:
            loguru.logger.error(e)
            raise DatabaseError(error_msg="Failed to delete profile by id")
