import time

from icube.target_ref.data_handlers.base import BaseDumper
from icube.target_ref.data_handlers.CSVgenerator import CSVFile
from icube.target_ref.data_handlers.constants import *
from icube.target_ref.data_handlers.model_cube import *
from icube.target_ref.src.tactile.common import tactile_logging as log


class Datacollector(BaseDumper):

    def __init__(self, persistence=None):
        super().__init__()
        self.subjects = {}
        self.trials = {}
        self.tested_cube = None
        self.cube_data = []
        self.phase = None
        self.similarity = None
        self.current_subject = None
        self.current_trial = None
        self.cube_data_id = 0
        self.persistence = persistence
        self.t_start = None
        self.t_stop = None
        self.memo_start = None
        self.memo_stop = None
        self.recall_start = None
        self.recall_stop = None
        # self.next_subject_id = self.persistence.get_next_subject_id()
        self.recording = False

    def add_subject(self, subject_id=0, age=0, hand=Hand.RIGHT):

        subject = Subject(subject_id=subject_id, age=age, hand=hand)
        self.subjects[subject_id] = subject

        # self.subjects[self.next_subject_id] = subject
        self.current_subject = subject
        log.info(f"Added new Subject, ID: {subject_id}")
        self.persistence.dump_subject(subject)
        # self.next_subject_id += 1
        return subject

    def add_trial(self, trial_id="", trial_condition="", need_ans=True, target_image="", ref_image="", similarity=""):
        trial = Trial(trial_id=trial_id, trial_condition=trial_condition, need_ans=need_ans,
                      target_image=target_image, ref_image=ref_image, similarity=similarity)
        log.info(f"Added new trial {trial_id}")
        self.trials[trial_id] = trial
        return trial

    def stop_trial(self, answer=""):

        log.info(f"Stop collecting data for trial {self.current_trial.trial_id}")
        self.t_stop = time.time()
        self.persistence.dump_trial(subject_id=self.current_subject.subject_id,
                                    trial_id=self.current_trial.trial_id,
                                    trial_condition=self.current_trial.trial_condition,
                                    t_start=self.t_start,
                                    t_stop=self.t_stop,
                                    memo_start=self.memo_start,
                                    memo_stop=self.memo_stop,
                                    recall_start=self.recall_start,
                                    recall_stop=self.recall_stop,
                                    similarity=self.current_trial.similarity,
                                    answer=answer)

        self.persistence.dump_cube_data(self.cube_data)
        self.cube_data = []

    def start_memo(self, trial_id):

        if self.recording:
            log.error(f"Still running {self.current_trial.trial_id}.")
            return

        self.phase = Phase.MEMO
        self.t_start = time.time()
        self.memo_start = time.time()
        self.current_trial = self.trials[trial_id]
        self.cube_data_id = 0
        self.recording = True
        log.info(f"Start collecting data for Memo phase of {trial_id}")

    def stop_memo(self):

        if not self.recording:
            log.error("No trial right now")
            return

        log.info(f"Stop collecting data from Memorization phase of trial {self.current_trial.trial_id}")
        self.recording = False
        self.memo_stop = time.time()
        self.persistence.dump_cube_data(self.cube_data)
        self.cube_data = []

    def start_recall(self, trial_id):

        if self.recording:
            log.error(f"Still running {self.current_trial.trial_id}.")
            return

        self.phase = Phase.RECALL
        self.recall_start = time.time()
        log.info(f"Start collecting data for Recall phase of {trial_id}")
        self.recording = True

    def stop_recall(self):

        if not self.recording:
            log.error("No trial right now")
            return

        log.info(f"Stop collecting data from Recall phase of trial {self.current_trial.trial_id}")
        self.recording = False
        self.recall_stop = time.time()
        self.persistence.dump_cube_data(self.cube_data)
        self.cube_data = []

    def push_data(self, quaternions=[], touches=[], accelerometer=[]):

        if self.recording:
            data = CubeData(
                subject_id=self.current_subject.subject_id,
                trial_id=self.current_trial.trial_id,
                phase=self.phase,
                quaternions=quaternions,
                touches=touches,
                accelerometer=accelerometer
            )
            self.cube_data.append(data)
            self.cube_data_id += 1

    def quit(self):
        self.persistence.quit()



