from enum import IntEnum


# https://wiki.secondlife.com/wiki/Category:LSL_Integer/link
class LinkNum(IntEnum):
    UNLINKED = 0  #      only one prim object, and there are no avatars seated upon it
    ROOT = 1  #          sends to the root prim in a multi-prim linked set
    SET = -1  #          sends to all prims
    ALL_OTHERS = -2  #   sends to all other prims
    ALL_CHILDREN = -3  # sends to all children, (everything but the root)
    THIS = -4  #         sends to the prim the script is in
