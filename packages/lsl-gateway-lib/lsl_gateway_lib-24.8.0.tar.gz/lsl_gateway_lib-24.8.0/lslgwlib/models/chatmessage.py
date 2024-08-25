from pydantic import BaseModel, Field, AliasChoices, field_validator
from uuid import UUID


from lslgwlib.enums import ChatChannel


# https://wiki.secondlife.com/wiki/Listen
class ChatMessage(BaseModel):
    """Message from chat model

    Event: listen(integer channel, string name, key id, string message)
    """

    channel: int = Field(default=ChatChannel.PUBLIC, ge=-0x80000000, le=0x7FFFFFFF)
    name: str = Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{1,63}$")
    id: UUID = Field(default=UUID(int=0))
    message: str = Field(
        min_length=1, max_length=1024, validation_alias=AliasChoices("msg", "message")
    )

    @field_validator("message")
    def msg_validator(cls, msg: str) -> str:
        if len(msg.encode("UTF-8")) > 1024:
            raise ValueError("max length of message is 1024 bytes")
        return msg
