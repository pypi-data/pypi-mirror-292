from pydantic import BaseModel, Field, field_validator, AliasChoices

from .avatar import Avatar


class Touch(BaseModel):
    prim: int = Field(
        default=0, ge=0, le=255, validation_alias=AliasChoices("prim", "prim_num")
    )
    face: int = Field(
        default=0, ge=0, le=9, validation_alias=AliasChoices("face", "side")
    )
    avatar: Avatar
    startST: tuple[float, float]
    endST: tuple[float, float]
    startUV: tuple[float, float]
    endUV: tuple[float, float]

    @field_validator("startST")
    def startST_validator(cls, coords: tuple[float, float]):
        if coords[0] < 0 or coords[1] < 0:
            raise ValueError("Touch.startST must contains positive values")
        if coords[0] > 1 or coords[1] > 1:
            raise ValueError("Touch.startST must contains values less than 1")
        return coords

    @field_validator("endST")
    def endST_validator(cls, coords: tuple[float, float]):
        if coords[0] < 0 or coords[1] < 0:
            raise ValueError("Touch.endST must contains positive values")
        if coords[0] > 1 or coords[1] > 1:
            raise ValueError("Touch.endST must contains values less than 1")
        return coords

    @field_validator("startUV")
    def startUV_validator(cls, coords: tuple[float, float]):
        if coords[0] < 0 or coords[1] < 0:
            raise ValueError("Touch.startUV must contains positive values")
        if coords[0] > 1 or coords[1] > 1:
            raise ValueError("Touch.startUV must contains values less than 1")
        return coords

    @field_validator("endUV")
    def endUV_validator(cls, coords: tuple[float, float]):
        if coords[0] < 0 or coords[1] < 0:
            raise ValueError("Touch.endUV must contains positive values")
        if coords[0] > 1 or coords[1] > 1:
            raise ValueError("Touch.endUV must contains values less than 1")
        return coords
