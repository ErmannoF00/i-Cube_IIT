"""
@package BaseDumper
@brief a base class to standardize the implementation of data dumpers
@author Dario Pasquali
"""

from icube.target_ref.src.tactile.common import tactile_logging as log


class BaseDumper:

    def dump_subject(self, subject):

        log.info(f"Store subject {subject.subject_id}")
        pass

    def get_next_subject_id(self):
        pass

    def dump_cube_data(self, cube_data):

        log.info(f"Store Cube Data")
        pass

    def dump_trial(self, subject_id, trial_id, trial_condition, t_start, t_stop, memo_start, memo_stop,
                   recall_start, recall_stop, similarity, answer):

        log.info(f"Store Trial {trial_id} for Subject {subject_id}")
        pass

    def quit(self):

        pass
