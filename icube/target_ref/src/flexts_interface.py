from icube import flexts_device
from icube.icube_interface import ICubeInterfaceV3


class FlexTSInterface(ICubeInterfaceV3):
    def __init__(self, is_mocked=False):
        super().__init__(is_mocked)

    def init(self, name="flex-ts", serial_port=""):
        self.device = flexts_device.FlexTSDevice()
        return self.device.start_up(device_name=name, serial_port=serial_port)

    def read_touch_single(self, timeout=0.4, face=1):
        """
        @fn read_cells
        @brief It reads the cells of the icubes facets
        @return the retrieved cells
        """
        self.read_touch(timeout=timeout)

