from enum import IntEnum


# https://wiki.secondlife.com/wiki/LlGetInventoryType
class InvetoryType(IntEnum):
    ANY = -1  #       any inventory type
    TEXTURE = 0  #    texture
    SOUND = 1  #      sound
    LANDMARK = 3  #   landmark
    CLOTHING = 5  #   clothing
    OBJECT = 6  #     object
    NOTECARD = 7  #   notecard
    SCRIPT = 10  #    script
    BODYPART = 13  #  body part
    ANIMATION = 20  # animation
    GESTURE = 21  #   gesture
    SETTING = 56  #   setting
    MATERIAL = 57  #  material
