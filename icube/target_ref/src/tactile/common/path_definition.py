import sys
import os


def add_path(file_path):

    from pathlib import Path
    abs_path = os.path.abspath(file_path)
    app_path = Path(abs_path).parent
    root_tactile = app_path.parent

    # insert all in the system paths.
    sys.path.insert(0, root_tactile)

    import tactile.common.device_info as device_info
    device_info.name = os.path.basename(app_path)
    device_info.path_app = app_path
    device_info.path_root = root_tactile
    device_info.folder_app = os.path.basename(app_path)
