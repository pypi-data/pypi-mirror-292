from pydantic import BaseModel, Field, model_validator
from typing import Pattern, Sequence
from datetime import datetime
from uuid import UUID
import re

from lslgwlib.enums import InvetoryType
from .permissions import Permissions


class InvetoryItem(BaseModel):
    """Invetory item model"""

    id: UUID
    type: InvetoryType
    name: str = Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{1,63}$")
    description: str = Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{0,127}$")
    creatorId: UUID
    permissions: Permissions
    acquireTime: datetime


class Invetory(BaseModel):
    """LSL linkset inventory model

    Fields:
    items -    list of inventory items (InvetoryItem model)
    filtered - indicates if inventory loaded by items type (not full representation)
    """

    items: list[InvetoryItem] = Field(max_length=10000)
    filtered: InvetoryType = Field(default=InvetoryType.ANY)

    @model_validator(mode="after")
    def check_filtered(self):
        if self.filtered != InvetoryType.ANY:
            if any(x.type != self.filtered for x in self.items):
                raise ValueError(
                    "Filtered Inventory must contains only items with same type"
                )
        return self

    def byName(self, name: str) -> InvetoryItem | None:
        """Get item by its name

        Arguments:
        name - string
        """
        for x in self.items:
            if x.name == name:
                return x
        return None

    def byNamePattern(self, pattern: str | Pattern) -> list[InvetoryItem]:
        """Get items by name part or regex

        Arguments:
        pattern - string part of name or regex
        """
        items = list()
        for x in self.items:
            if isinstance(pattern, Pattern) and re.match(pattern, x.name):
                items.append(x)
            if isinstance(pattern, str) and pattern in x.name:
                items.append(x)
        return items

    def byType(self, types: Sequence[InvetoryType]) -> list[InvetoryItem]:
        """Get items by types

        Arguments:
        types - sequence of types
        """
        if InvetoryType.ANY in types:
            return self.items
        for bytype in types:
            if self.filtered != InvetoryType.ANY and self.filtered != bytype:
                raise ValueError(
                    f"This Inventory instance loaded without {repr(bytype)}"
                )
        return list(filter(lambda x: (x.type in types), self.items))

    def names(self) -> list[str]:
        return list(map(lambda x: x.name, self.items))

    @property
    def textures(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.TEXTURE])

    @property
    def sounds(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.SOUND])

    @property
    def landmarks(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.LANDMARK])

    @property
    def clothings(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.CLOTHING])

    @property
    def objects(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.OBJECT])

    @property
    def notecards(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.NOTECARD])

    @property
    def scripts(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.SCRIPT])

    @property
    def bodyparts(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.BODYPART])

    @property
    def animations(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.ANIMATION])

    @property
    def gestures(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.GESTURE])

    @property
    def settings(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.SETTING])

    @property
    def materials(self) -> list[InvetoryItem]:
        return self.byType([InvetoryType.MATERIAL])
