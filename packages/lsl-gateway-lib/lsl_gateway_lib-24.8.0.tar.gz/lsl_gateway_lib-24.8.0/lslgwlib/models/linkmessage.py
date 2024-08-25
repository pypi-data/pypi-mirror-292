from pydantic import BaseModel, Field, AliasChoices, field_validator
from uuid import UUID


from lslgwlib.enums import LinkNum


# https://wiki.secondlife.com/wiki/Link_message
# https://wiki.secondlife.com/wiki/LlMessageLinked
class LinkMessage(BaseModel):
    """Link message

    Event: link_message(integer sender_num, integer num, string str, key id)
    Function: llMessageLinked(integer link, integer num, string str, key id)
    """

    prim: int = Field(
        default=LinkNum.THIS,
        ge=LinkNum.THIS,
        le=255,
        validation_alias=AliasChoices(
            "prim",
            "prim_num",
            "sender",
            "sender_num",
            "link",
            "source",
            "from",
            "target",
            "to",
        ),
    )
    num: int = Field(default=0, ge=-0x80000000, le=0x7FFFFFFF)
    string: str = Field(default="", validation_alias=AliasChoices("string", "str"))
    id: str | UUID = Field(default="")

    @field_validator("id")
    def id_validator(cls, id: str | UUID) -> str | UUID:
        if isinstance(id, UUID):
            return id
        try:
            uuid = UUID(id)
        except Exception:
            return id
        else:
            return uuid
