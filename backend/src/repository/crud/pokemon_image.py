import typing
import uuid

import fastapi
import loguru
import pydantic
import sqlalchemy
from sqlalchemy.orm import object_session, selectinload as sqlalchemy_selectinload
from sqlalchemy.sql import functions as sqlalchemy_functions

from src.api.dependency.crud import get_crud
from src.api.dependency.header import get_auth_current_user
from src.models.db.account import Account
from src.models.db.pokemon_image import PokemonImage
from src.models.db.profile import Profile
from src.models.schema.pokemon_image import PokemonImageInCreate, PokemonImageInResponse, PokemonImageInUpdate
from src.repository.crud.base import BaseCRUDRepository
from src.utility.exceptions.custom import EntityDoesNotExist, PasswordDoesNotMatch


class PokemonImageCRUDRepository(BaseCRUDRepository):
    async def create_pokemon_image(
        self, pokemon_image_create: PokemonImageInCreate, current_profile: Profile
    ) -> PokemonImage:
        try:
            new_pokemon_image = PokemonImage(**pokemon_image_create.dict(exclude={"image"}))
            new_pokemon_image.file_name = await self._generate_file_name()
            new_pokemon_image.profile = current_profile
            # await self._save_image_on_S3(pokemon_image_create.image)
            self.async_session.add(instance=new_pokemon_image)
            await self.async_session.commit()
            await self.async_session.refresh(instance=new_pokemon_image)
            await self.async_session.close()

        except:
            loguru.logger.error("Error in create_pokemon_image()")
            raise Exception("Error in create_pokemon_image()")

        return new_pokemon_image

    async def _generate_file_name(self) -> str:
        file_name = str(uuid.uuid4())
        return file_name

    # async def _save_image_on_S3(self, image: fastapi.UploadFile) -> bool:
    #     return True

    async def read_all_pokemon_images(self) -> list[PokemonImageInResponse]:
        select_stmt = sqlalchemy.select(PokemonImage).options(sqlalchemy_selectinload("*"))
        query = await self.async_session.execute(statement=select_stmt)
        return query.scalars().all()
