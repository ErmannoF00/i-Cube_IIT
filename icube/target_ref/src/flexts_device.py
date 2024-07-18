from icube.device_commands import DeviceCommands, ICubeVersion
from icube.tactile.common import tactile_logging as log
from icube.tactile.tactile_device import TactileDevice


class FlexTSDevice(TactileDevice):

    def __init__(self):
        """
        @fn Constructor
        @brief It opens the serial communication.
        """
        super().__init__()
        self.cmd = DeviceCommands(ICubeVersion.FlexTS)

    def is_device_connected(self, timeout=10):
        """
        @fn is_device_connected
        @brief The method checks if the device is connected. It does this by sending a ping message
        If the reply ping message is not received before the timeout is expired False is returned, otherwise
        True is returned.
        @param timeout max time cycling before returned a not connection variable
        @return True if it is connected, False otherwise.
        """
        try:
            ping_message = [self.cmd.start, self.cmd.peripheral_number, self.cmd.device_id,
                            self.cmd.ping, self.cmd.zero, self.cmd.zero, self.cmd.zero, self.cmd.stop]

            import codecs
            hex_value = format(self.cmd.device_id, 'x')
            cmd_device_id = codecs.encode(hex_value.encode(), "hex")
            cmd_device_id = str(cmd_device_id.decode("utf-8"))

            return self.send_ping_message(ping_message=ping_message,
                                          length_reply_ping=self.cmd.msg_length.reply_ping,
                                          cmd_reply_ping=self.cmd.ping_reply,
                                          timeout=timeout)
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def check_battery(self, timeout=2):
        """
        The method asks the  voltage reading for the device battery
        It checks the voltage, it prints the read voltage and returns False if the device is not sufficiently charged.
        @param timeout max time cycling before returned a not connection variable
        @return True if it is charged, False otherwise
        """
        try:
            battery_message = [self.cmd.start, self.cmd.peripheral_number, self.cmd.device_id,
                               self.cmd.battery, self.cmd.zero, self.cmd.zero, self.cmd.zero, self.cmd.stop]
            return self.send_battery_message(battery_message,
                                             self.cmd.msg_length.reply_battery,
                                             self.cmd.battery_reply,
                                             timeout)
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def check_firmware(self, timeout=2):
        """
        @fn check_firmware
        @brief The method checks the firmware uploaded into the device.
        It compares the received firmware with the version stred in the code.
        If different it returns false.
        @param timeout max time cycling before returned a not connection variable
        @return True is connection, False otherwise.
        """
        try:
            firmware_message = [self.cmd.start, self.cmd.peripheral_number, self.cmd.device_id,
                                self.cmd.get_fwm_version, self.cmd.zero, self.cmd.zero, self.cmd.zero, self.cmd.stop]

            firmware = self.send_firmware_message(firmware_message, self.cmd.msg_length.reply_get_fw, timeout)
            correct_firmware_version = self.cmd.firmware_reply

            if firmware == correct_firmware_version:
                log.info(f"the firmware version uploaded into the {self.device_name} is {firmware}, and it is correct!")
                return True
            else:
                log.info(f"firmware version not correct! It should be {correct_firmware_version}")
                return False

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def check_calibration(self, timeout=2):
        """
        @fn check_calibration
        @brief The method checks if the cbe is calibrated.
        It compares the received firmware with the version stred in the code.
        If different it returns false.
        @param timeout max time cycling before returned a not connection variable
        @return True is connection, False otherwise.
        """
        try:
            calibration_message = [self.cmd.start, self.cmd.peripheral_number, self.cmd.device_id,
                                self.cmd.read_bno, self.cmd.zero, self.cmd.zero, self.cmd.zero, self.cmd.stop]

            return self.send_calibration_message(calibration_message, self.cmd.msg_length.reply_calibration, timeout)

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def read_quaternions(self, timeout=0.4):
        """
        The method returns the quaternions which are provided by the device
        @param timeout max time cycling before returned a no quaternions available
        @return the quaternions retrieved.
        """
        try:
            read_bno_message = [self.cmd.start, self.cmd.peripheral_number, self.cmd.device_id,
                                self.cmd.read_bno, self.cmd.quat, self.cmd.zero, self.cmd.zero, self.cmd.stop]

            q_string = self.get_quaternion_string(read_bno_message, self.cmd.msg_length.reply_bno, timeout)
            #            print(f"the message for {q_id} quaternion is {q_string}")
            quaternions = self.parse_quaternion_string(q_string)
            return quaternions

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def read_touch(self, timeout=0.4):
        """
        @fn read_touch
        @brief The method returns a list of the pressed cells for each facet of the icube.
        The list of the facets are ordered from the first side to the last side, according to
        the standard used for the icube (see documentaion).
        Each element of the list is a binary string where there is a one where the cell has been presed, and zero
        when the cell is not pressed.
        The cells on each side are read from left to right and then from top to bottom.
        @return the list of cube facets and each facet is a string of a binary number,
        with zero where the cell is not touched, and one where the cell has been touched.
        """
        try:
            ask_msg = [self.cmd.start, self.cmd.peripheral_number, self.cmd.device_id,
                                self.cmd.touch_mpx, self.cmd.zero, self.cmd.zero, self.cmd.zero, self.cmd.stop]

            touch_message = self.get_touch_message(ask_msg, self.cmd.msg_length.reply_mpx, timeout)

            # print(f"the touch message is {touch_message}")

            if not touch_message or len(touch_message) != self.cmd.msg_length.reply_mpx:
                return None

            # The following two lines are to remove the start and stop characters from the message
            touch_message = touch_message[1:]
            touch_message = touch_message[:-1]

            binary_message = list(map(lambda x: "{0:08b}".format(x)[::-1], touch_message))

            facets = list()
            facets.append(''.join([binary_message[3], binary_message[2]]))
            facets.append(''.join([binary_message[5], binary_message[4]]))
            facets.append(''.join([binary_message[1], binary_message[0]]))
            facets.append(''.join([binary_message[7], binary_message[6]]))

            return facets

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def read_accelerometer(self, timeout=0.4):
        """
        The method returns a list of the accelerometer values from the icube.
            ...
        @return the list of accelerometer values
        """
        try:
            ask_msg = [self.cmd.start, self.cmd.peripheral_number, self.cmd.device_id,
                                self.cmd.read_bno, self.cmd.accel, self.cmd.zero, self.cmd.zero, self.cmd.stop]

            accelerometer_message = self.get_accelerometer_message(ask_msg, self.cmd.msg_length.reply_accel, timeout)

            # print(f"the accelerometer message is {accelerometer_message}")

            if not accelerometer_message or len(accelerometer_message) != self.cmd.msg_length.reply_accel:
                return None

            accelerations = self.parse_accelerometer_message(accelerometer_message)

            return accelerations

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []
