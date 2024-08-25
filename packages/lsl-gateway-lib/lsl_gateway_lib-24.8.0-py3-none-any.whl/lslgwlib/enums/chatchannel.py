from enum import IntEnum


# https://wiki.secondlife.com/wiki/Listen
# https://wiki.secondlife.com/wiki/LlSay
class ChatChannel(IntEnum):
    PUBLIC = 0  #         Chat channel that broadcasts to all nearby users
    DEBUG = 0x7FFFFFFF  # Chat channel reserved for script debugging and error messages
