import typing

import fastapi
import loguru
import pydantic
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import object_session

from src.api.dependency.crud import get_crud
from src.api.dependency.header import get_auth_current_user
from src.models.db.account import Account
from src.models.schema.account import (
    AccountInRead,
    AccountInSignin,
    AccountInSignout,
    AccountInSignup,
    AccountInUpdate,
)
from src.models.schema.base import BaseSchemaModel
from src.models.schema.pokemon_image import PokemonImageInCreate, PokemonImageInResponse
from src.repository.crud.account import AccountCRUDRepository
from src.repository.crud.pokemon_image import PokemonImageCRUDRepository
from src.repository.crud.profile import ProfileCRUDRepository
from src.utility.exceptions.custom import EntityDoesNotExist
from src.utility.exceptions.database import DatabaseError
from src.utility.exceptions.http.exc_400 import http_exc_400_bad_request
from src.utility.exceptions.http.exc_403 import http_exc_403_forbidden_request
from src.utility.exceptions.http.exc_404 import http_exc_404_id_not_found_request

router = fastapi.APIRouter(prefix="/pokemon_images", tags=["pokemon_images"])


@router.get(
    path="",
    name="pokemon_images:read-pokemon_images",
    response_model=list[PokemonImageInResponse],
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_pokemon_image(
    pokemon_image_repo: PokemonImageCRUDRepository = fastapi.Depends(get_crud(repo_type=PokemonImageCRUDRepository)),
) -> list[PokemonImageInResponse]:
    pokemon_image_list: list = list()
    try:
        db_pokemon_images = await pokemon_image_repo.read_all_pokemon_images()

    except EntityDoesNotExist:
        loguru.logger.info("No pokemon_images found")
        raise await http_exc_404_id_not_found_request(id=0)

    for pokemon_image in db_pokemon_images:
        new_pokemon_image = PokemonImageInResponse(**pokemon_image.__dict__)
        pokemon_image_list.append(new_pokemon_image)

    return pokemon_image_list


@router.post(
    path="",
    name="pokemon_images:uploaded-pokemon_image",
    response_model=PokemonImageInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def upload_pokemon_image(
    pokemon_image_create: PokemonImageInCreate = fastapi.Body(..., embed=True),
    pokemon_image_repo: PokemonImageCRUDRepository = fastapi.Depends(get_crud(repo_type=PokemonImageCRUDRepository)),
    profile_crud_repo: ProfileCRUDRepository = fastapi.Depends(get_crud(repo_type=ProfileCRUDRepository)),
    current_account: Account = fastapi.Depends(get_auth_current_user()),
) -> PokemonImageInResponse:
    current_profile = await profile_crud_repo.read_profile_by_account_id(account_id=current_account.id)

    db_pokemon_image = await pokemon_image_repo.create_pokemon_image(
        pokemon_image_create=pokemon_image_create, current_profile=current_profile
    )

    new_pokemon_image = PokemonImageInResponse(**db_pokemon_image.__dict__)

    return new_pokemon_image
