from enum import IntEnum


# https://wiki.secondlife.com/wiki/LlGetAttached
class AttachPoint(IntEnum):
    NONE = 0
    HEAD = 2  #           Skull                head
    NOSE = 17  #          Nose                 nose
    MOUTH = 11  #         Mouth                mouth
    FACE_TONGUE = 52  #   Tongue               tongue
    CHIN = 12  #          Chin                 chin
    FACE_JAW = 47  #      Jaw                  jaw
    LEAR = 13  #          Left Ear             left ear
    REAR = 14  #          Right Ear            right ear
    FACE_LEAR = 48  #     Alt Left Ear         left ear (extended)
    FACE_REAR = 49  #     Alt Right Ear        right ear (extended)
    LEYE = 15  #          Left Eye             left eye
    REYE = 16  #          Right Eye            right eye
    FACE_LEYE = 50  #     Alt Left Eye         left eye (extended)
    FACE_REYE = 51  #     Alt Right Eye        right eye (extended)
    NECK = 39  #          Neck                 neck
    LSHOULDER = 3  #      Left Shoulder        left shoulder
    RSHOULDER = 4  #      Right Shoulder       right shoulder
    LUARM = 20  #         L Upper Arm          left upper arm
    RUARM = 18  #         R Upper Arm          right upper arm
    LLARM = 21  #         L Lower Arm          left lower arm
    RLARM = 19  #         R Lower Arm          right lower arm
    LHAND = 5  #          Left Hand            left hand
    RHAND = 6  #          Right Hand           right hand
    LHAND_RING1 = 41  #   Left Ring Finger     left ring finger
    RHAND_RING1 = 42  #   Right Ring Finger    right ring finger
    LWING = 45  #         Left Wing            left wing
    RWING = 46  #         Right Wing           right wing
    CHEST = 1  #          Chest                chest/sternum
    LEFT_PEC = 29  #      Left Pec             left pectoral
    RIGHT_PEC = 30  #     Right Pec            right pectoral
    BELLY = 28  #         Stomach              belly/stomach/tummy
    BACK = 9  #           Spine                back
    TAIL_BASE = 43  #     Tail Base            tail base
    TAIL_TIP = 44  #      Tail Tip             tail tip
    AVATAR_CENTER = 40  # Avatar Center        avatar center/root
    PELVIS = 10  #        Pelvis               pelvis
    GROIN = 53  #         Groin                groin
    LHIP = 25  #          Left Hip             left hip
    RHIP = 22  #          Right Hip            right hip
    LULEG = 26  #         L Upper Leg          left upper leg
    RULEG = 23  #         R Upper Leg          right upper leg
    RLLEG = 24  #         R Lower Leg          right lower leg
    LLLEG = 27  #         L Lower Leg          left lower leg
    LFOOT = 7  #          Left Foot            left foot
    RFOOT = 8  #          Right Foot           right foot
    HIND_LFOOT = 54  #    Left Hind Foot       left hind foot
    HIND_RFOOT = 55  #    Right Hind Foot      right hind foot

    HUD_CENTER_2 = 31  #     HUD Center 2
    HUD_TOP_RIGHT = 32  #    HUD Top Right
    HUD_TOP_CENTER = 33  #   HUD Top
    HUD_TOP_LEFT = 34  #     HUD Top Left
    HUD_CENTER_1 = 35  #     HUD Center
    HUD_BOTTOM_LEFT = 36  #  HUD Bottom Left
    HUD_BOTTOM = 37  #       HUD Bottom
    HUD_BOTTOM_RIGHT = 38  # HUD Bottom Right
