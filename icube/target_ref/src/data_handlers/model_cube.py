import string
from icube.target_ref.data_handlers.constants import Hand


class Subject:

    def __init__(self, subject_id=None, age=-1, hand=Hand.RIGHT):
        self.subject_id = subject_id
        self.age = age
        self.hand = hand

    def get_csv(self, sep=";"):
        return sep.join([
            str(self.subject_id),
            str(self.age),
            str(self.hand.name)
            ])


class Trial:

    def __init__(self, trial_id=None, trial_condition="", need_ans=False,
                 target_image="", ref_image="", similarity=""):
        self.trial_id = trial_id
        self.trial_condition = trial_condition
        self.need_ans = need_ans
        self.target_image = target_image
        self.ref_image = ref_image
        self.similarity = similarity


class CubeData:
    def __init__(self, subject_id=None, trial_id=None, phase=None,
                 quaternions=[], touches=[], accelerometer=[]):

        self.subject_id = subject_id
        self.trial_id = trial_id
        self.phase = phase
        self.quaternions = quaternions
        self.touches = touches
        self.accelerometer = accelerometer

    def get_csv(self, sep=";"):
        return sep.join([
            str(self.subject_id),
            str(self.trial_id),
            str(self.phase),
            str(self.quaternions),
            str(self.touches),
            str(self.accelerometer)
        ])


