import sys
import threading
import time

from scipy.spatial.transform import Rotation as rotation

from icube.target_ref.src import icube_device
from icube.target_ref.src.device_commands import ICubeVersion
from icube.target_ref.src.tactile.common import tactile_logging as log


def ICubeInterface(version=ICubeVersion.V3, is_mocked=False):
    if version == ICubeVersion.V3:
        return ICubeInterfaceV3(is_mocked)
    else:
        return ICubeInterfaceV4(is_mocked)


class ICubeInterfaceV3:
    def __init__(self, is_mocked=False):
        # iCube handling
        self.device = None

        # Data Grabber
        self.icube_grabber_thread = None
        self.timeout = 0.4
        self.on_data_callback = None

        self.is_mocked = is_mocked

    def bind_callback(self, callback):
        self.on_data_callback = callback

    def init(self, name="icube", serial_port=""):
        self.device = icube_device.ICubeV3()
        return self.device.start_up(device_name=name, serial_port=serial_port)

    def calibrate(self, max_time=30):
        log.info("Please rotate the iCube of 90 degrees in different direction each 3 SECONDS")
        log.info("Keep doing it until all the sensors are = 3")
        i = 0
        while not self.device.check_calibration() and i < max_time:
            i += 1
            time.sleep(1)
            log.info(str(i))

        log.info("Calibration Done!")

    def start_streaming(self, timeout=0.4):

        log.info(f"Init streaming from the {self.device.device_name}")
        self.fsm_running = True

        # Allow for mocked data streaming
        grabber_method = self.__grabber
        if self.is_mocked:
            grabber_method = self.__mocked_grabber

        self.icube_grabber_thread = threading.Thread(
            target=grabber_method,
            args=(
                self.device,
                lambda: self.timeout,
                lambda q, t, a: self.on_data_callback(q, t, a),
                lambda: self.fsm_running
            )
        )
        self.icube_grabber_thread.start()
        log.info("Streaming started")

    def stop_streaming(self):
        self.fsm_running = False
        self.icube_grabber_thread.join()
        log.info("Streaming stopped")

    def grab(self, timeout=0.4):
        quaternions, rotation_matrix = self.read_quaternions(timeout)
        touches = self.read_touch(timeout)
        accelerometer = self.read_accelerometer(timeout)
        return quaternions, touches, accelerometer, rotation_matrix

    def __grabber(self, device, timeout, callback, running_condition):
        touches = []
        quaternions = []
        accelerometer = []

        while running_condition():
            quaternions, touches, accelerometer, _ = self.grab(timeout())
            callback(quaternions, touches, accelerometer)

    def __mocked_grabber(self, device, timeout, callback, running_condition):
        while running_condition():
            callback([], [], [])

    def read_quaternions(self, timeout=0.4):
        """
        It reads the quaternions from the icube
        @return the retrieved quaternions
        """
        quaternions = self.device.read_quaternions(timeout=timeout)
        if not quaternions or all(q == 0 for q in quaternions):
            quaternions = []
            rotation_matrix = None
        else:
            rotation_instance = rotation.from_quat(quaternions)
            rotation_matrix = rotation_instance.as_matrix()

        return quaternions, rotation_matrix

    def read_touch(self, timeout=0.4):
        """
        @fn read_cells
        @brief It reads the cells of the icubes facets
        @return the retrieved cells
        """
        return self.device.read_touch(timeout=timeout)

    def read_touch_single(self, timeout=0.4, face=1):
        """
        @fn read_cells
        @brief It reads the cells of the icubes facets
        @return the retrieved cells
        """
        return self.device.read_touch_single(timeout=timeout, face=face)

    def read_accelerometer(self, timeout=0.4):
        """
         It reads the values of the accelerometer from the icube.
        @return the retrieved cells
        """
        accelerometer = self.device.read_accelerometer(timeout=timeout)

        if not accelerometer:
            return []

        return accelerometer


class ICubeInterfaceV4(ICubeInterfaceV3):

    def __init__(self, is_mocked=False):
        super().__init__(is_mocked)

    def init(self, name="icube", serial_port=""):
        self.device = icube_device.ICubeV4()
        return self.device.start_up(device_name=name, serial_port=serial_port)

    def set_vibration_duration(self, duration):
        self.device.set_vibration_duration(duration)

    def set_vibration_duty(self, duty):
        self.device.set_vibration_duty(duty)

    def vibrate(self):
        self.device.send_vibration()

    def set_audio_volume(self, value):
        self.device.set_audio_volume(value)

    def play_sound(self, sound_id):
        self.device.send_play_audio(sound_id)
