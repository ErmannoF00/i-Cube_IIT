import sys

import argparse
import os
import configparser
import yaml

from icube.target_ref.guis.Main_gui import *
from icube.target_ref.data_handlers.data_collector import Datacollector

from icube.target_ref.src.icube_interface import ICubeInterfaceV3
from icube.target_ref.src.device_commands import ICubeVersion

from icube.target_ref.src.data_handlers.aggregator import CallbackAggregator, AggregateMode
from icube.target_ref.src.data_handlers.icube_movements_classifier import GraspDetector
from icube.target_ref.src.tactile.common import tactile_logging as log


DEFAULT_PATH = os.getenv("ICUBE_PATH", default="./icube/icube_ws")
DEFAULT_RESOURCE_PATH = os.getenv("ICUBE_PATH", default="./icube/icube_ws")


def load_trial(controller, resource_path=""):
    try:
        with open(f"{resource_path}/trials.yaml") as f:
            trials_config = yaml.load(f, Loader=yaml.FullLoader)

            for t in trials_config['trials']:
                for t_name, t_params in t.items():

                    trial_id = t_name
                    condition = t_params['condition']
                    need_ans = t_params['need_ans']
                    similarity = str(t_params['similarity'])
                    target_image = t_params['target_image']
                    reference_image = t_params['reference_image']
                    for k, _ in target_image.items():
                        target_image[k] = f"{resource_path}/{target_image[k]}"
                    for w, _ in reference_image.items():
                        reference_image[w] = f"{resource_path}/{reference_image[w]}"

                    controller.add_trial(
                        trial_id=trial_id,
                        trial_condition=condition,
                        need_ans=need_ans,
                        target_image=target_image,
                        ref_image=reference_image,
                        similarity=similarity
                    )

            # selected_block = 'block_A'

            for _, tg in trials_config['trials_groups']['block_groups'].items():
                controller.add_trial_group(sequential_group=tg)

    except FileNotFoundError:
        print(f"Error: File '{resource_path}/trials.yaml' not found.")
        return


# --------------------------------------------------------------------------------------------------------------


def parse_args():

    cube_reference_name = "REFERENCE"
    cube_target_name = "TARGET"
    reference_port = "/dev/ttyUSB0"
    target_port = "/dev/ttyUSB0"

    parser = argparse.ArgumentParser(
        prog="Haptic Exploration",
        description="Framework to collect data with the iCube"
    )

    parser.add_argument("-n_r", "--name_r", help="reference cube name", default=cube_reference_name)
    parser.add_argument("-n_t", "--name_t", help="target cube name", default=cube_target_name)
    parser.add_argument("-p_r", "--port_r", help="reference port", default=reference_port)
    parser.add_argument("-p_t", "--port_t", help="target port", default=target_port)
    parser.add_argument("-c_r", "--calibration_r", type=int, help="reference port", default=5)
    parser.add_argument("-c_t", "--calibration_t", type=int, help="target port", default=5)

    parser.add_argument("-e", "--exec-path", help="where to look for the executable", default=DEFAULT_PATH)
    parser.add_argument("-r", "--resource-path", help="where to look for assets and trials",
                        default=DEFAULT_RESOURCE_PATH)

    parser.add_argument("-d", "--detect-grabbing", action="store_true",
                        help="autonomously start/stop the data collection when the cube is grabbed/posed")

    parser.add_argument("-t", "--grab-tolerance", type=float, default=1.0,
                        help="tolerance on detecting grab actions, lower = more sensible")

    parser.add_argument("-i", "--init", action="store_true",
                        help="Init the current folder with assets and a trials boilerplate")

    parser.add_argument("--conf", help="load from a .ini file", default="")
    params = parser.parse_args()

    if params.conf != "":
        config_reader = configparser.ConfigParser()
        config_reader.read(params.conf)
        params.exec_path = bool(config_reader['PARAMS']['exec-path'])
        params.resource_path = bool(config_reader['PARAMS']['resource-path'])

        params.name_r = config_reader['PARAMS']['name_r']
        params.name_t = config_reader['PARAMS']['name_t']
        params.port_r = config_reader['PARAMS']['port_r']
        params.port_t = config_reader['PARAMS']['port_t']
        params.calibration_r = int(config_reader['PARAMS']['calibration_r'])
        params.calibration_t = int(config_reader['PARAMS']['calibration_t'])

    return params


# --------------------------------------------------------------------------------------------------------------

def main():

    params = parse_args()

    if params.init:
        import shutil
        log.info("Just Init the assets folder")
        shutil.copytree(f"{DEFAULT_PATH}/assets/logo_contact.png", './assets/logo_contact.png')
        shutil.copytree(f"{DEFAULT_PATH}/assets/logo_rbcs.png", './assets/logo_rbcs.png')
        shutil.copytree(f"{DEFAULT_PATH}/assets/logo_whisper.png", './assets/logo_whisper.png')
        log.info("Init Trials")
        shutil.copytree(f"{DEFAULT_PATH}/trials.yaml")
        sys.exit(0)

    controller = GuiController(resource_path=params.resource_path)

    controller.init_data_collector(storage_path="./data")

    if params.detect_grabbing:
        controller.init_handling_classifier(grab_tolerance=params.grab_tolerance)

    load_trial(controller=controller, resource_path=params.resource_path)

    controller.run()


# --------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
    sys.exit(0)
