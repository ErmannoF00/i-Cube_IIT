import os
import os.path

from icube.target_ref.src.tactile.common import device_info


def create_folder_if_not_exist(path):
    """
    It checks if the folder in path passed as input exists, and if so, it creates the folder
    @param path the path to check if it exists
    @return Nothing
    """
    ## Create directory if doesn't exist
    if not os.path.exists(path):
        print(f"Created the folder in the path {path}")
        os.mkdir(path)


class File:
    db_file = "explorations.sqlite"
    extraction_path = "extraction_path.config"


class Folders:
    """
    @class Folders
    @brief container for the name of the folders in the code
    """
    common = "common"

    if device_info.name:
        device = device_info.folder_app
    else:
        device = "device"

    data = 'saved_data'
    logs = "logs"
    database = 'database'


class Paths:
    """
    @class Paths
    @brief container for the most used paths in the code.
    """
    file = None
    all_code = device_info.path_root
    device_code = os.path.join(all_code, Folders.device)
    data = os.path.join(device_code, Folders.data)
    logs = os.path.join(device_code, Folders.logs)
    database = os.path.join(data, File.db_file)
    extraction_path_file = os.path.join(data, File.extraction_path)

    ## Create data directory if doesn't exist
    # create_folder_if_not_exist(data)
    create_folder_if_not_exist(logs)
