from icube.target_ref.src.device_commands import DeviceCommands, ICubeVersion
from icube.target_ref.src.tactile.common import tactile_logging as log
from icube.target_ref.src.tactile.tactile_device import TactileDevice, TactileDeviceV4


class ICubeV3(TactileDevice):

    def __init__(self):
        """
        @fn Constructor
        @brief It opens the serial communication.
        """
        super().__init__()
        self.cmd = DeviceCommands(ICubeVersion.V3)

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
            ping_message = [self.cmd.start, self.cmd.ping, self.cmd.zero, self.cmd.stop]

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
            battery_message = [self.cmd.start, self.cmd.battery, self.cmd.zero, self.cmd.stop]
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
            firmware_message = [self.cmd.start, self.cmd.get_fwm_version, self.cmd.zero, self.cmd.stop]
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
            calibration_message = [self.cmd.start, self.cmd.read_bno, self.cmd.zero, self.cmd.stop]
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
            read_bno_message = [self.cmd.start, self.cmd.read_bno, self.cmd.quat, self.cmd.stop]
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
            ask_msg = [self.cmd.start, self.cmd.touch_mpx, self.cmd.zero, self.cmd.stop]
            touch_message = self.get_touch_message(ask_msg, self.cmd.msg_length.reply_mpx, timeout)

            # print(f"the touch message is {touch_message}")

            if not touch_message or len(touch_message) != self.cmd.msg_length.reply_mpx:
                return None

            # The following two lines are to remove the start and stop characters from the message
            touch_message = touch_message[1:]
            touch_message = touch_message[:-1]

            binary_message = list(map(lambda x: "{0:08b}".format(x)[::-1], touch_message))

            facets = list()
            facets.append(''.join([binary_message[11], binary_message[10]]))
            facets.append(''.join([binary_message[3], binary_message[2]]))
            facets.append(''.join([binary_message[5], binary_message[4]]))
            facets.append(''.join([binary_message[9], binary_message[8]]))
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
            ask_msg = [self.cmd.start, self.cmd.read_bno, self.cmd.accel, self.cmd.stop]

            accelerometer_message = self.get_accelerometer_message(ask_msg, self.cmd.msg_length.reply_accel, timeout)

            # print(f"the accelerometer message is {accelerometer_message}")

            if not accelerometer_message or len(accelerometer_message) != self.cmd.msg_length.reply_accel:
                return None

            accelerations = self.parse_accelerometer_message(accelerometer_message)

            return accelerations

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []


class ICubeV4(TactileDeviceV4):
    num_facets = 6
    n_pads_per_facet = 16  # the number of the cube sides
    n_touches_values = num_facets * n_pads_per_facet  # by 2 because each touch value is made of 2 integers in the received packet.

    def __init__(self, group=0x50, device_id=1):
        super().__init__()

        self.cmd = DeviceCommands(ICubeVersion.V4)
        self.touches = [0 for _ in range(self.num_facets * self.n_pads_per_facet)]
        self.group = group
        self.device_id = device_id

    def is_device_connected(self, timeout=10):
        try:
            ping_message = [self.cmd.start, self.group, self.device_id, self.cmd.ping, self.cmd.zero, self.cmd.stop]
            return self.send_ping_message(ping_message=ping_message,
                                          length_reply_ping=self.cmd.msg_length.reply_ping,
                                          cmd_reply_ping=1,
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
            battery_message = [self.cmd.start, self.group, self.device_id, self.cmd.battery, self.cmd.zero,
                               self.cmd.stop]
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
            firmware_message = [self.cmd.start, self.group, self.device_id, self.cmd.get_fwm_version, self.cmd.zero,
                                self.cmd.stop]
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

    def read_touch(self, timeout=0.4):
        return self.read_all_touches(timeout=timeout)

    def read_touch_single(self, timeout=0.4, face=1):
        ask_msg = [self.cmd.start,
                   self.group, self.device_id,
                   self.cmd.touch_mpx, face,
                   self.cmd.stop]

        self.update_touches(ask_msg)
        single_touch_message = self.get_single_touch_messages(ask_msg, self.cmd.msg_length.reply_mpx_single, timeout)
        return single_touch_message

    def read_all_touches(self, timeout=0.4):
        """
        @fn read_all_touches
        @brief The method returns a list of the pressed cells for each facet of the icube.
        The list of the facets are ordered from the first side to the last side, according to
        the standard used for the icube (see documentation).
        Each element of the list is a binary string where there is a one where the cell has been presed, and zero
        when the cell is not pressed.
        The cells on each side are read from left to right and then from top to bottom.
        @return the list of cube facets and each facet is a string of a binary number,
        with zero where the cell is not touched, and one where the cell has been touched.
        """
        facets = []
        facets_string = ['0' * 16 for i in range(6)]
        try:
            ask_msg = [self.cmd.start,
                       self.group, self.device_id,
                       self.cmd.touch_mpx, self.cmd.register_facets,
                       self.cmd.stop]
            self.update_touches(ask_msg)

            ask_msg = [self.cmd.start,
                       self.group, self.device_id,
                       self.cmd.touch_mpx, self.cmd.send_facets,
                       self.cmd.stop]
            touch_messages = self.get_all_touch_messages(ask_msg, self.cmd.msg_length.reply_mpx, timeout)

            drop_payload = False
            face = []
            for tm in touch_messages:
                if tm == self.cmd.start_reply:
                    face = []
                    drop_payload = False
                elif tm == self.cmd.stop_reply:
                    facets.append(face)
                    drop_payload = True
                else:
                    if not drop_payload:
                        face.append(tm)

            facets_string = [''.join(['1' if x > 0 else '0' for x in face]) for face in facets]
            return facets, facets_string

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return facets,

    def read_accelerometer(self, timeout=0.4):
        """
        The method returns a list of the accelerometer values from the icube.
            ...
        @return the list of accelerometer values
        """
        try:
            ask_msg = [self.cmd.start, self.group, self.device_id, self.cmd.read_bno, self.cmd.accel, self.cmd.stop]
            accelerometer_message = self.get_accelerometer_message(ask_msg, self.cmd.msg_length.reply_accel, timeout)

            if not accelerometer_message or len(accelerometer_message) != self.cmd.msg_length.reply_accel:
                return None

            accelerations = self.parse_accelerometer_message(accelerometer_message)
            return accelerations

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def read_quaternions(self, timeout=0.4):
        """
        The method returns the quaternions which are provided by the device
        @param timeout max time cycling before returned a no quaternions available
        @return the quaternions retrieved.
        """
        try:
            read_bno_message = [self.cmd.start, self.group, self.device_id, self.cmd.read_bno, self.cmd.quat,
                                self.cmd.stop]
            q_string = self.get_quaternion_string(read_bno_message, self.cmd.msg_length.reply_bno, timeout)
            quaternions = self.parse_quaternion_string(q_string)
            return quaternions
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def send_vibration(self):
        """
        The method sends the message for vibrating the icube
        """
        try:
            set_msg = [self.cmd.start, self.group, self.device_id, self.cmd.activate_vibro, 0x00, self.cmd.stop]
            self.send_vibromotor_message(set_msg)

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return None

    def set_vibration_duration(self, duration):
        """
        The method sends the message to set the duration of the icube vibration
        """
        try:
            time_msg = [self.cmd.start, self.group, self.device_id, self.cmd.time_vibro, duration, self.cmd.stop]
            self.set_vibromotor_duration_message(time_msg)

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return None

    def set_vibration_duty(self, duty):
        """
        The method sends the message to set the duty of the icube vibration
        """
        try:
            duty_msg = [self.cmd.start, self.group, self.device_id, self.cmd.duty_vibro, duty, self.cmd.stop]
            self.set_vibromotor_duty_message(duty_msg)

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return None

    def set_audio_volume(self, value):
        """
        The method sends the message to set the volume of the audio file to play
        @param value the value of the volume of the audio file.
        """
        try:
            set_volume_msg = [self.cmd.start, self.group, self.device_id, self.cmd.volume, value, self.cmd.stop]
            self.set_volume_audio_message(set_volume_msg)
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return None

    def send_play_audio(self, sound_id):
        """
        The method sends the message to play the audio file.
        """
        try:
            play_audio_msg = [self.cmd.start, self.group, self.device_id, self.cmd.play_audio, sound_id, self.cmd.stop]
            self.set_play_audio_message(play_audio_msg)

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return None
