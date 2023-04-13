import datetime

import pydantic
from fastapi import UploadFile

from src.models.schema.base import BaseSchemaModel

# ? Question:   How is the photo being handled?
# ?             How do we validate it?
# ?             How is it being send to the client?


class PokemonImageInUpdate(BaseSchemaModel):
    nickname: str


class PokemonImageInCreate(BaseSchemaModel):
    name: str
    nickname: str
    # image: UploadFile | None


class PokemonImageInResponse(BaseSchemaModel):
    id: int
    file_name: str
    name: str
    nickname: str
    correct_predicted: int
    wrong_predicted: int
    win: int
    loss: int
    created_at: datetime.datetime
    updated_at: datetime.datetime | None
    profile_id: int | None
