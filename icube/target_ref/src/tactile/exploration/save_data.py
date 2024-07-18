import datetime
from icube.target_ref.src.tactile.common.paths import Paths as paths
import os.path
from os.path import join as join_path


class SaveData:
    """
    @class SaveData
    @brief class to store the data of the experiment in a txt file
    """
    file = None

    def __init__(self, subject_data, path=paths.data):

        date_string = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")

        filename = f"{subject_data['name']}_{subject_data['date_of_birth']}_{date_string}.csv"

        self.filename = os.path.join(path, filename)

        # create the file
        self.write_data("")

    def write_data(self, data):
        with open(self.filename, 'w+') as self.file:
            for d in data:
                self.file.write(d)

