from enum import Enum


# circular imports
class MatchType(Enum):
    COORD = "XY"
    RENDER = "R"
    ANNOTATION = "A"
