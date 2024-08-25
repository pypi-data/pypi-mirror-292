from pydantic import BaseModel, Field, field_validator

from lslgwlib.enums import PermValue


class Permission(BaseModel):
    perms: int = Field(ge=0, le=0x7FFFFFFF)

    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            super().__init__(perms=args[0])
        else:
            super().__init__(**kwargs)

    @field_validator("perms")
    def perms_validator(cls, perms: int):
        if (
            perms & PermValue.COPY
            and perms & PermValue.MODIFY
            and perms & PermValue.MOVE
            and perms & PermValue.TRANSFER
        ):
            return PermValue.ALL
        match perms:
            case PermValue.COPY:
                return PermValue.COPY
            case PermValue.MODIFY:
                return PermValue.MODIFY
            case PermValue.MOVE:
                return PermValue.MOVE
            case PermValue.TRANSFER:
                return PermValue.TRANSFER
            case PermValue.NONE:
                return PermValue.NONE
        return perms

    @property
    def ALL(self) -> bool:
        return self.perms == PermValue.ALL

    @property
    def COPY(self) -> bool:
        return bool(self.perms & PermValue.COPY)

    @property
    def MODIFY(self) -> bool:
        return bool(self.perms & PermValue.MODIFY)

    @property
    def MOVE(self) -> bool:
        return bool(self.perms & PermValue.MOVE)

    @property
    def TRANSFER(self) -> bool:
        return bool(self.perms & PermValue.TRANSFER)


class Permissions(BaseModel):
    base: Permission
    owner: Permission
    group: Permission
    everyone: Permission
    next: Permission

    def __init__(self, *args, **kwargs) -> None:
        if len(args) == 5:
            super().__init__(
                base=Permission(args[0]),
                owner=Permission(args[1]),
                group=Permission(args[2]),
                everyone=Permission(args[3]),
                next=Permission(args[4]),
            )
        else:
            super().__init__(**kwargs)
