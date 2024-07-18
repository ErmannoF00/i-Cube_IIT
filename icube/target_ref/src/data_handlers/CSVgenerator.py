from icube.target_ref.data_handlers.base import BaseDumper
from icube.target_ref.src.tactile.common import tactile_logging as log
from icube.target_ref.data_handlers.constants import *

import os
import pandas as pd


class CSVTable:
    """
    @package CSVTable
    @brief a class to model a csv table
    @author Dario Pasquali
    """

    def __init__(self, path, header, buffering=1):
        self.path = path
        self.header = header
        self.buffering = buffering
        self.file = None
        self.__create_or_open()

    def __create_or_open(self):
        need_init = not os.path.isfile(self.path)
        self.file = open(self.path, buffering=self.buffering, mode="a+")
        if need_init:
            self.write_line(self.header)
            self.file.flush()

    def write_line(self, txt):
        self.file.write(txt + "\n")

    def close(self):
        self.file.close()


def init_storage_path(storage_path=""):
    if not os.path.isdir(storage_path):
        os.makedirs(storage_path)


class CSVFile(BaseDumper):

    SEPARATOR = ";"
    SUBJECT_HEADER = SEPARATOR.join(['subject_id', 'age', 'hand'])
    CUBE_DATA_HEADER = SEPARATOR.join(['subject_id', 'trial_id', 'phase',
                                       'quaternions', 'touches', 'accelerometer'])
    TRIALS_HEADER = SEPARATOR.join(['subject_id', 'trial_id', 'condition', 'trial_start', 'trial_stop',
                                    'memo_start', 'memo_stop', 'recall_start', 'recall_stop',
                                    'similarity', 'answer'])

    def __init__(self, storage_path=""):
        self.storage_path = storage_path
        init_storage_path(storage_path)

        self.subjects_path = self.storage_path + "/subjects.csv"
        self.cube_data_path = self.storage_path + "/cube_data.csv"
        self.trial_path = self.storage_path + "/trials.csv"

        log.info("Opening the Subjects and Cube Data CSVs")
        self.subjects_file = CSVTable(path=self.subjects_path, header=self.SUBJECT_HEADER)
        self.cube_data_file = CSVTable(path=self.cube_data_path, header=self.CUBE_DATA_HEADER)
        self.trials_file = CSVTable(path=self.trial_path, header=self.TRIALS_HEADER)

    # def get_next_subject_id(self):
    #     """
    #     Return the next subject ID based on the stored subject.csv file.
    #     If not present it restarts from 0
    #     @return:
    #     """
    #     df = pd.read_csv(self.subjects_path, sep=self.SEPARATOR)
    #     if df.empty:
    #         return 0
    #     else:
    #         return df.subject_id.max() + 1
    def quit(self):
        """
        Graceful close
        @return:
        """
        log.info("Closing the files")
        self.subjects_file.close()
        self.cube_data_file.close()
        self.trials_file.close()

    def dump_subject(self, subject):
        """
        Store a new subject data
        @param subject: unique subject id
        @return:
        """
        super().dump_subject(subject)
        self.subjects_file.write_line(subject.get_csv())

    def dump_trial(self, subject_id=-1, trial_id=-1, trial_condition=Condition.HAPTIC_HAPTIC,
                   similarity=Similarity.EQUAL, t_start=None, t_stop=None, memo_start=None, memo_stop=None,
                   recall_start=None, recall_stop=None, answer=''):
        """
        Store a new trial data
        @param subject_id: unique subject id
        @param trial_id: unique trial id
        @param trial_condition: HAPTIC-HAPTIC/HAPTIC-VISUO/VISUO-HAPTIC/VISUO-VISUO
        @param similarity: EQUAL/DIFFERENT
        @param t_start: trial start
        @param t_stop: trial stop
        @param memo_start: memorization phase start
        @param memo_stop: memorization phase stop
        @param recall_start: recall phase start
        @param recall_stop: recall phase stop
        @param answer : subject answer
        @return:
        """
        super().dump_trial(subject_id, trial_id, trial_condition, t_start, t_stop, memo_start, memo_stop,
                           recall_start, recall_stop, similarity, answer)

        self.trials_file.write_line(
            self.SEPARATOR.join(
                str(x) for x in [subject_id, trial_id, trial_condition, t_start, t_stop,
                                 memo_start, memo_stop, recall_start, recall_stop, similarity, answer]))

    def dump_cube_data(self, cube_data):
        """
        Store a new iCube datapoint
        @param cube_data: (quaternions, touches, accelerations)
        @return:
        """
        super().dump_cube_data(cube_data)
        for data in cube_data:
            self.cube_data_file.write_line(data.get_csv())
        log.info('Cube data stored')
