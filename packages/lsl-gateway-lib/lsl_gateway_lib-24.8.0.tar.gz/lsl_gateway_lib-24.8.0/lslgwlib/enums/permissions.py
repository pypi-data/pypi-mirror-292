from enum import IntEnum


# https://wiki.secondlife.com/wiki/LlGetInventoryPermMask


class PermMask(IntEnum):
    BASE = 0  #     The base permissions
    OWNER = 1  #    Current owner permissions
    GROUP = 2  #    Active group permissions
    EVERYONE = 3  # Permissions everyone has
    NEXT = 4  #     Permissions the next owner will have


class PermValue(IntEnum):
    ALL = 0x7FFFFFFF  #      Move/Modify/Copy/Transfer permissions
    COPY = 0x00008000  #     Copy permission
    MODIFY = 0x00004000  #   Modify permission
    MOVE = 0x00080000  #     Move permission
    TRANSFER = 0x00002000  # Transfer permission
    NONE = 0  #              No one permission
