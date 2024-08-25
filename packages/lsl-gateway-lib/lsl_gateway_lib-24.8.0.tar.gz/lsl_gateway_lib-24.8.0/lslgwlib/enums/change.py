from enum import IntEnum


# https://wiki.secondlife.com/wiki/Changed
class Change(IntEnum):
    INVENTORY = 0x001  #        Prim inventory has changed
    COLOR = 0x002  #            Prim color or alpha parameters have changed
    SHAPE = 0x004  #            Prim shape has changed
    SCALE = 0x008  #            Prim scale has changed
    TEXTURE = 0x010  #          Prim texture parameters have changed
    LINK = 0x020  #             The number of prims or avatars seated on the object have changed
    ALLOWED_DROP = 0x040  #     A user has added inventory to the prim
    OWNER = 0x080  #            The object has changed owners
    REGION = 0x100  #           The object has changed region
    TELEPORT = 0x200  #         The avatar has teleported
    REGION_START = 0x400  #     The region this object is in has just come online
    MEDIA = 0x800  #            Prim Media has changed
    RENDER_MATERIAL = 0x1000  # Render Material has changed
