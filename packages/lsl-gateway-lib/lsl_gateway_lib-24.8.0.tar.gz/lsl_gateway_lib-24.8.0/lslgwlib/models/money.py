from pydantic import BaseModel, Field

from .avatar import Avatar


class Money(BaseModel):
    amount: int = Field(ge=0, le=0x7FFFFFFF)
    avatar: Avatar
