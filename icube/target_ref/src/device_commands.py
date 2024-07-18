""""
@file device_commands
@brief commands defined for the device iCube version 3.0
"""
import enum


class ICubeVersion(enum.Enum):
    V3 = {'version': 3, 'ping_reply': 0x81, 'get_fwm_version': 0x13, 'reply_get_fw': 3, 'reply_mpx': 14, 'reply_mpx_single': 3}
    # 1B for each of the 16 pads + 2 (start, end) = 18 Bytes for each face
    # 18 B x 6 faces = 108 Bytes
    # V4 = {'version': 4, 'ping_reply': 0x31, 'reply_get_fw': 1, 'reply_mpx': 108}
    V4 = {'version': 4, 'ping_reply': 0x31, 'get_fwm_version': 0x13, 'reply_get_fw': 1, 'reply_mpx': 198, 'reply_mpx_single': 18} # 34

    FlexTS = {'version': 1, 'get_fwm_version': 0x14, 'ping_reply': None, 'reply_mpx': 14, 'reply_get_fw': 1, 'reply_mpx_single': None} # ping_reply is the ASCII of the device id number

    def __getitem__(self, item):
        return self.value[item]


class MsgLength:
    def __init__(self, version):
        self.reply_ping = 3
        self.reply_battery = 5
        self.reply_get_fw = 3
        self.reply_bno = 32
        self.reply_mpx = version['reply_mpx']
        self.reply_calibration = 29
        self.reply_accel = 32
        self.reply_mpx_single = version['reply_mpx_single']


class DeviceCommands:
    """
    @class DeviceCommands
    @brief class with the commands used to communicate with the device.
    """

    def __init__(self, version):
        self.start = 0xf5
        self.stop = 0xf0
        self.broadcast = 0xff  # this message is generated if the pad has all the cells covered at the same time.

        self.zero = 0x00  # used to transmit a message to the cube
        self.ping = 0x01  # use to verify the device is connected and active.
        self.quat = 0x01  # used for getting the first set of the quaternions.
        self.accel = 0x02  # used for getting the second set of the quaternions.
        self.battery = 0x10  # used to read the voltage of the battery supply
        self.get_fwm_version = version['get_fwm_version']  # used to read the version of the NTS firmware
        self.touch_mpx = 0x15  # used to read the pads
        self.read_bno = 0x16  # used to ask the reading of the MEMS G.A.M.

        if version == ICubeVersion.V4:
            # v4 commands
            self.register_facets = 0x07  # used to record the facets, the old facets are overwritten
            self.send_facets = 0x08  # used for getting the data from all the 6 touch boards (from register_facets)
            self.activate_vibro = 0x40  # activates the vibro-motor with the energy set by the command 0x41 and duration by 0x42
            self.duty_vibro = 0x41  # sets the vibro-motor supply tension
            self.time_vibro = 0x42  # sets the time the vibro-motor will be active
            self.play_audio = 0x20  # used for playing the selected audio file.
            self.volume = 0x21  # sets the volume to play the audio files.

        if version == ICubeVersion.FlexTS:
            self.peripheral_number = 0x10  # tHe number of the peripheral which is the usb receiver.
            self.device_id = 0x01  # to define. Now it is possible to manage up to 32 FexTs with the same peripheral.
            self.shutdown = 0x77  # The command turn the device off # | START | 0x10 |  ID  |  0x77 | 0x00 | 0x00 | 0x00 |  END |

        # TODO check with Antonio, sono invertiti nella documentazione
        self.start_reply = 0xf3
        self.stop_reply = 0xfa
        self.ping_reply = version['ping_reply']  # 0x31(v3) / 0x81(v4) TODO fix in the documentation
        self.battery_reply = 0x2e
        self.firmware_reply = version['reply_get_fw']

        self.msg_length = MsgLength(version)
