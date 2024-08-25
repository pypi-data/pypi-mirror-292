from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from .avatar import Avatar
from .permissions import Permissions
from lslgwlib.enums import AttachPoint


class LinkSetInfo(BaseModel):
    id: UUID
    owner: Avatar
    lastOwnerId: UUID
    creatorId: UUID
    groupId: UUID
    name: str = Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{1,63}$")
    description: str = Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{0,127}$")
    attached: AttachPoint
    primsNum: int = Field(gt=0, le=255)
    inventoryNum: int = Field(ge=0, le=10000)
    createdAt: datetime
    rezzedAt: datetime
    scriptName: str = Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{1,63}$")
    permissions: Permissions
