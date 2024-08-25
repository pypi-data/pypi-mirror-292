from pydantic import BaseModel, Field, AliasChoices
from datetime import datetime
from uuid import UUID


class PrimInfo(BaseModel):
    # id calculates on client side
    id: UUID
    creatorId: UUID
    name: str = Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{1,63}$")
    description: str = Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{0,127}$")
    faces: int = Field(
        default=1,
        gt=0,
        le=9,
        validation_alias=AliasChoices("faces", "faces_num", "sides", "sides_num"),
    )
    createdAt: datetime
