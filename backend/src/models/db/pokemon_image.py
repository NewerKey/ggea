import datetime

import uuid
import sqlalchemy
from sqlalchemy.orm import (
    Mapped as SQLAlchemyMapped,
    mapped_column as sqlalchemy_mapped_column,
    relationship as sqlalchemy_relationship,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import functions as sqlalchemy_functions

from src.models.db.base import DBBaseTable


class PokemonImage(DBBaseTable):
    __tablename__ = "pokemon_image"

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(
        sqlalchemy.String(length=124), nullable=False, default=None
    )
    name: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=124), nullable=False, default=None)
    nickname: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(
        sqlalchemy.String(length=124), nullable=False, default=name
    )
    correct_predicted: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(
        sqlalchemy.Integer(), nullable=False, default=0
    )
    wrong_predicted: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer(), nullable=False, default=0)
    loss: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer(), nullable=False, default=0)
    win: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.Integer(), nullable=False, default=0)
    created_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True), nullable=False, server_default=sqlalchemy_functions.now()
    )
    updated_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
        server_onupdate=sqlalchemy.schema.FetchedValue(for_update=True),
        default=None,
    )
    profile_id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.ForeignKey("profile.id"))
    profile = sqlalchemy_relationship("Profile", back_populates="pokemon_images")

    __mapper_args__ = {"eager_defaults": True}
