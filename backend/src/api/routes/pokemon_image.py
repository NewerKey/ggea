import typing

import fastapi
import loguru
import pydantic
from sqlalchemy.orm import object_session

from src.api.dependency.crud import get_crud
from src.api.dependency.header import get_auth_current_user
from src.models.db.account import Account
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
async def get_profiles(
    pokemon_image_repo: PokemonImageCRUDRepository = fastapi.Depends(get_crud(repo_type=PokemonImageCRUDRepository)),
) -> list[PokemonImageInResponse]:
    pokemon_image_list: list = list()
    try:
        db_pokemon_images = await pokemon_image_repo.read_all_pokemon_images()

    except EntityDoesNotExist:
        loguru.logger.info("No pokemon_images found")
        raise await http_exc_404_id_not_found_request(id=0)

    for pokemon_image in db_pokemon_images:
        new_pokemon_image = PokemonImageInResponse(
            id=pokemon_image.id,
            file_name=pokemon_image.file_name,
            name=pokemon_image.name,
            nickname=pokemon_image.nickname,
            correct_predicted=pokemon_image.correct_predicted,
            wrong_predicted=pokemon_image.wrong_predicted,
            win=pokemon_image.win,
            loss=pokemon_image.loss,
            created_at=pokemon_image.created_at,
            updated_at=pokemon_image.updated_at,
            profile_id=pokemon_image.profile_id,
        )
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
    current_account: Account = fastapi.Depends(get_auth_current_user()),
) -> PokemonImageInResponse:
    loguru.logger.info("getting current_profile")
    current_profile = current_account.profile
    #! DIRTY HACK -----------------------------------------------------
    # expunge all to avoid "profile is already attached to session n+1 this is session n" error
    loguru.logger.info("getting session of current_profile")
    session_of_current_profile = object_session(current_profile)
    session_of_current_profile.expunge_all()
    loguru.logger.info("Successfully expunged all")
    #! ----------------------------------------------------------------
    db_pokemon_image = await pokemon_image_repo.create_pokemon_image(
        pokemon_image_create=pokemon_image_create, current_profile=current_profile
    )
    loguru.logger.info("Successfully created pokemon_image")

    new_pokemon_image = PokemonImageInResponse(
        id=db_pokemon_image.id,
        file_name=db_pokemon_image.file_name,
        name=db_pokemon_image.name,
        nickname=db_pokemon_image.nickname,
        correct_predicted=db_pokemon_image.correct_predicted,
        wrong_predicted=db_pokemon_image.wrong_predicted,
        win=db_pokemon_image.win,
        loss=db_pokemon_image.loss,
        created_at=db_pokemon_image.created_at,
        updated_at=db_pokemon_image.updated_at,
        profile_id=db_pokemon_image.profile_id,
    )

    return new_pokemon_image
