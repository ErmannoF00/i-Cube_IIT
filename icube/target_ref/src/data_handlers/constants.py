from enum import Enum
import string


class Hand(Enum):
    RIGHT = 0,
    LEFT = 1,
    BOTH = 2

    @staticmethod
    def parse(val):
        try:
            return Hand[str.upper(val)]
        except:
            return Hand.RIGHT

    def to_string(self):
        return {RIGHT: "right", LEFT: "left", BOTH: "both"}[self]


class Similarity(Enum):
    EQUAL = 1,
    DIFFERENT = 2

    @staticmethod
    def parse(val):
        try:
            return Similarity[str.upper(val)]
        except:
            return Similarity.EQUAL

    def to_string(self):
        return {EQUAL: "Equal", DIFFERENT: "Different"}[self]


class Phase(Enum):
    MEMO = 1,
    RECALL = 2

    @staticmethod
    def parse(val):
        try:
            return Phase[str.upper(val)]
        except:
            return Phase.MEMO

    def to_string(self):
        return {MEMO: "Memo", RECALL: "Recall"}[self]


class Condition(Enum):
    HAPTIC_HAPTIC = 1,
    HAPTIC_VISUAL = 2
    VISUAL_HAPTIC = 3,
    VISUAL_VISUAL = 4

    def to_string(self):
        return {HAPTIC_HAPTIC: "Haptic_haptic", HAPTIC_VISUAL: "Haptic_haptic",
                VISUAL_HAPTIC: "Visual_haptic", VISUAL_VISUAL: "Visual_visual"}[self]


class Icubetype(Enum):
    REFERENCE = 1,
    TARGET = 2

    @staticmethod
    def parse(val):
        try:
            return Icubetype[str.upper(val)]
        except:
            return Icubetype.REFERENCEù

    def to_string(self):
        return {REFERENCE: "Reference", TARGET: "Target"}[self]
