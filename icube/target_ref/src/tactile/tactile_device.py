import codecs
import time

from icube.target_ref.src.tactile.common import tactile_logging as log
from icube.target_ref.src.tactile.common import utilities as utils
from icube.target_ref.src.tactile.common.constants import Acceleration_limits as al
from icube.target_ref.src.tactile.communication.serial_comm import SerialComm


class TactileDevice:

    def __init__(self):
        """
        @fn Constructor
        @brief It opens the serial communication.
        """
        self.device_name = ''
        self.device_online = True
        self.serial_communication = SerialComm()
        # define the process to communicate through yarp
        self.yarp_connection = None

    def start_up(self, device_name, serial_port=""):
        """
        The method starts up the device. It initialises it and returns true if the initialisation was successful.
        @param device_name the name of the device. used for printing useful information
        @return True if successful
        """
        try:
            self.device_name = device_name

            log.info(f"Opening the communication with the {self.device_name} ... ")

            if not self.open_communication(serial_port):
                return False

            self.serial_communication.empty_serial()

            log.info(f"The communication was open, trying to connect to the {self.device_name} ... ")
            if not self.is_device_connected():
                log.info(f"It seems the {self.device_name} is not connected. Check that the {self.device_name} "
                         f"is turned on and fully charged.")
                self.device_online = False

            else:  # the device is connected and ready to start
                log.info(f"The {self.device_name} is connected and ready to start.")

            if self.device_online:
                if not self.check_battery():
                    return False

                if not self.check_firmware():
                    return False

            return True

        except Exception as e:
            print(utils.get_exception_message(e))
            log.exception(str(e) + ' ' + log.get_debug_info())

    def open_communication(self, serial_port=""):
        """
        @fn open_communication
        @brief It starts the communication with the Xbee and sends messages to the tamo device.
        """
        try:
            if not self.serial_communication.configure_serial_port(serial_port):
                raise Exception("Connection Error")

            # close previously open communications.
            self.serial_communication.close_comm()
            self.serial_communication.check_port_is_open()

            # open the communication
            self.serial_communication.open_comm()
            self.serial_communication.check_port_is_open()
            return True

        except Exception as e:
            print(utils.get_exception_message(e))
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

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
            raise NotImplemented("The method has not been implemented!")
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def send_ping_message(self, ping_message, length_reply_ping, cmd_reply_ping, timeout=10):
        """
        The method sends the ping message to the serial port and waits for the reply
        @param ping_message the ping message to send
        @param length_reply_ping the length of the reply to the ping message
        @param cmd_reply_ping the command which identifies the reply to the ping.
        @param timeout max time cycling before returned a not connection variable
        @return True is successfully connected, False otherwise.
        """
        try:
            time.sleep(2)
            timer_start = time.time()
            time_passed = 0

            while time_passed < timeout:

                self.serial_communication.empty_serial()
                time_passed = time.time() - timer_start
                self.serial_communication.write_to(ping_message)
                time.sleep(0.1)
                output = self.serial_communication.read_from(num_bytes=length_reply_ping)
                # output = self.serial_communication.read_from(num_bytes=64)

                if not output:
                    continue

                try:
                    hex_value = format(cmd_reply_ping, 'x')  # this converts to hexadecimal string without the 0x prefix.
                except ValueError:
                    # It would be an ASCII value
                    hex_value = cmd_reply_ping

                print(f"is {hex_value} in {output}?")
                if hex_value in output:
                    log.info(f"{self.device_name} connected")
                    return True

            log.info(f"{self.device_name} not found")
            return False
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def check_battery(self, timeout=2):
        """
        @fn check_battery
        @brief The method asks the  voltage reading for the device battery
        It checks the voltage, it prints the read voltage and returns False if the device is not sufficiently charged.
        @param timeout max time cycling before returned a not connection variable
        @return True if it is charged, False otherwise
        """
        try:
            raise NotImplemented("The method has not been implmented!")

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def send_battery_message(self, battery_message, length_reply_battery, cmd_reply_battery, timeout=2):
        """
        The method asks the  voltage reading for the device battery
        It checks the voltage, it prints the read voltage and returns False if the device is not sufficiently charged.
        @param battery_message the message to get the battry value to send
        @param the length of the reply to the battery message
        @param the command of the reply battery
        @param timeout max time cycling before returned a not connection variable
        @return True if it is charged, False otherwise
        """
        try:
            timer_start = time.time()
            time_passed = 0

            while time_passed < timeout:

                self.serial_communication.empty_serial()
                time_passed = time.time() - timer_start

                self.serial_communication.write_to(battery_message)
                time.sleep(0.1)
                # output = self.serial_communication.read_from(num_bytes=cmd.msg_length.reply_battery)
                battery_rx = self.serial_communication.read_binary_from(num_bytes=length_reply_battery)
                if battery_rx is not None:
                    battery_rx = list(battery_rx)
                else:
                    continue

                dec_value = int(cmd_reply_battery)  # this converts to hexadecimal string without the 0x prefix.
                if dec_value in battery_rx:
                    xx = chr(battery_rx[1])
                    yy = chr(battery_rx[3])

                    voltage = float(f"{xx}.{yy}")
                    log.info(f"current battery voltage = {voltage}")

                    if voltage > 3.1:
                        log.info("battery ok")
                        return True
                    else:
                        log.info("the battery needs to be charged")
                        return False

            log.info(f"{self.device_name} not found")
            return False
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def check_firmware(self, timeout=2):
        """
        The method checks the firmware uploaded into the device.
        It compares the received firmware with the version stred in the code.
        If different it returns false.
        @param timeout max time cycling before returned a not connection variable
        @return True is connection, False otherwise.
        """
        try:
            raise NotImplemented("The method has not been implemented")
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def send_firmware_message(self, firmware_message, length_reply_firmware, timeout=2):
        """
        The message sends the message to the serial to get the info on the firmware
        @param firmware_message the message to send to the serial
        @param length_reply_firmware the length of the reply to the firmware message
        @param timeout max time cycling before returned a not connection variable
        @return the version of the firmware we were asking for
        """
        try:
            timer_start = time.time()
            time_passed = 0

            while time_passed < timeout:

                self.serial_communication.empty_serial()
                time_passed = time.time() - timer_start

                self.serial_communication.write_to(firmware_message)
                time.sleep(0.1)
                firmware_version = self.serial_communication.read_binary_from(num_bytes=length_reply_firmware)
                if firmware_version is not None:
                    firmware_version = list(firmware_version)
                else:
                    continue
                return int(chr(firmware_version[1]))

            log.info(f"{self.device_name} not found")
            return None

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
            raise NotImplemented("The method has not been implementd!")
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def send_calibration_message(self, calibration_message, length_calibration_reply, timeout=2):
        """
        The method send a libration message to the device and check if it is currently calibrated or not.
        @param calibration_message the message to check if it is calibrated to send to the serial port.
        @param length_calibration_reply the length of the reply to the calibration message
        @param timeout max time cycling before returned a not connection variable
        @return True if it is calibrated, false otherwise.
        """
        try:
            timer_start = time.time()
            time_passed = 0

            while time_passed < timeout:

                self.serial_communication.empty_serial()
                time_passed = time.time() - timer_start

                self.serial_communication.write_to(calibration_message)
                time.sleep(0.1)
                calibration_output = self.serial_communication.read_binary_from(
                    num_bytes=length_calibration_reply)
                if calibration_output is not None:
                    calibration_string = str(calibration_output)

                    ## Extracting the value for the calibration
                    temp = "Sys: "
                    if temp in calibration_string:
                        sys = calibration_string[calibration_string.find(temp) + len(temp)]
                    else:
                        continue
                    temp = "Gyro: "
                    if temp in calibration_string:
                        gyro = calibration_string[calibration_string.find(temp) + len(temp)]
                    else:
                        continue
                    temp = "Accel: "
                    if temp in calibration_string:
                        accel = calibration_string[calibration_string.find(temp) + len(temp)]
                    else:
                        continue
                    temp = "Mag: "
                    if temp in calibration_string:
                        mag = calibration_string[calibration_string.find(temp) + len(temp)]
                    else:
                        continue

                    calibration_output_list = list(calibration_output)
                else:
                    continue
                calibration_value = calibration_output_list[10:].count(51)
                calibrated = calibration_value == 3

                output_values = f"sys = {sys}, gyro = {gyro}, accel = {accel}, mag = {mag}"
                if calibrated:
                    log.info(f"the {self.device_name} is calibrated, {output_values}")
                else:
                    log.info(f"the {self.device_name} is NOT calibrated, {output_values}")

                return calibrated
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def read_quaternions(self):
        """
        The method returns the quaternions which are provided by the device.
        @return the quaternions retrieved.
        """
        try:
            raise NotImplemented("The method has not been implemented!")
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def get_quaternion_string(self, read_bno_message, length_reply_quaternions, timeout=0.4):
        """
        The method sends the message to receive the quaternion messages and reads
        @param read_bno_message the message to ask for the quaternions
        @param length_reply_quaternions the length of the reply message
        @return The string received from teh serial port.
        """
        try:
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(read_bno_message)

            q_string = None

            t_end = time.time() + timeout
            while time.time() < t_end:
                time.sleep(0.01)
                q_string = self.serial_communication.read_from(num_bytes=length_reply_quaternions)
                if q_string:
                    break
            return q_string
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return ''

    def parse_quaternion_string(self, quaternion_string):
        """
        The method takes the quaternion message in input and parses teh message to retrieve the four quaternions
        @param quaternion_string the string with embedded the quaternions
        @return the list with the quaternions.
        """
        try:
            if not quaternion_string:
                return []

            if quaternion_string == 'NOK':
                return []

            ascii_code = str(codecs.decode(quaternion_string, "hex"))

            if ascii_code[2] == 'W' and \
                ascii_code[10] == 'X' and \
                ascii_code[18] == 'Y' and \
                ascii_code[26] == 'Z':

                w = float(ascii_code[3:10])
                x = float(ascii_code[11:18])
                y = float(ascii_code[19:26])
                z = float(ascii_code[27:34])

                return [w, x, y, z]
            else:
                print("missed 1!!")
                return []

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def read_touch(self, timeout=0.4):
        """
        @fn read_touch
        @brief The method returns a list of the pressed cells for each facet of the device.
        The list of the facets are ordered from the first side to the last side, according to
        the standard used for the device (see documentaion).
        Each element of the list is a binary string where there is a one where the cell has been presed, and zero
        when the cell is not pressed.
        The cells on each side are read from left to right and then from top to bottom.
        @return the list of device facets and each facet is a string of a binary number,
        with zero where the cell is not touched, and one where the cell has been touched.
        """
        try:
            raise NotImplemented("The method has not been implemented!")

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def get_touch_message(self, touch_message, length_reply_mpx, timeout=0.4):
        """
        The method calls the serial to read the message of the facets touches
        @param touch_message the message to send to the serial to be able to read the touch message.
        @param length_reply_mpx the length of the reply message to the touch
        @param timeout the waiting time for the reply.
        @return the message of the touched cells
        """
        try:
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(touch_message)
            touch_message_bytes = None

            t_end = time.time() + timeout
            while time.time() < t_end:
                time.sleep(0.01)
                touch_message_bytes = self.serial_communication.read_binary_from(num_bytes=length_reply_mpx)
                if touch_message_bytes:
                    break

            if not touch_message_bytes:
                # print("NOK!")
                return None

            touch_message = list(touch_message_bytes)

            if touch_message[-1] != 250:  # Otherwise cannot find the the end message character.
                return None

            return touch_message

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def read_accelerometer(self, timeout=0.4):
        """
        The method returns a list of the accelerometer values from the cube.
            ...
        @return the list of accelerometer values
        """
        try:
            raise NotImplemented("The method has not been implemented!")
        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def get_accelerometer_message(self, ask_message, length_reply_accel, timeout=0.4):
        """
        The method calls the serial to read the message of the accelerometer
        @param ask_message the message to send to the serial to be able to read the accelerometer message.
        @param length_reply_accel the length of the reply message to the accelerometer
        @param timeout the waiting time for the reply.
        @return the message of the accelerometer values
        """
        try:
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(ask_message)
            accelerometer_message_bytes = None

            t_end = time.time() + timeout
            while time.time() < t_end:
                time.sleep(0.01)
                accelerometer_message_bytes = self.serial_communication.read_binary_from(num_bytes=length_reply_accel)
                if accelerometer_message_bytes:
                    break

            if not accelerometer_message_bytes:
                # print("NOK!")
                return None

            accelerometer_message = list(accelerometer_message_bytes)

            # accelerometer_message = [243, 88, 48, 46, 48, 48, 89, 45, 48, 46, 48, 50, 90, 45, 48, 46, 48, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 250]

            if accelerometer_message[-1] != 250:  # Otherwise cannot find the the end message character.
                return []
            else:
                return accelerometer_message

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def parse_accelerometer_message(self, accelerometer_message):
        """
        The method takes in input the accelerometer message, it parses it and returns a list of the accelerometer values
        where position 0 is for value x, position 1 is for value y, position 2 is for value z
        @param accelerometer_message the message received.
        @return the list with the accelerometer values
        """
        try:
            accelerations = []

            x_pos = accelerometer_message.index(al.acc_x_digit)
            y_pos = accelerometer_message.index(al.acc_y_digit)
            z_pos = accelerometer_message.index(al.acc_z_digit)
            end_pos = accelerometer_message.index(al.acc_end_digit)

            x_value = accelerometer_message[x_pos+1:y_pos]
            y_value = accelerometer_message[y_pos+1:z_pos]
            z_value = accelerometer_message[z_pos+1:end_pos]

            x_value_str = ''.join(chr(i) for i in x_value)
            y_value_str = ''.join(chr(i) for i in y_value)
            z_value_str = ''.join(chr(i) for i in z_value)

            try:
                accelerations.append(float(x_value_str))
                accelerations.append(float(y_value_str))
                accelerations.append(float(z_value_str))

            except ValueError as v:
                print(utils.get_exception_message(v))
                log.exception(str(v) + ' ' + log.get_debug_info())
                return []

            return accelerations

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []


class TactileDeviceV4(TactileDevice):
    
    def __init__(self):
        super().__init__()
        
    def read_all_touches(self, timeout=0.4):
        """
        @fn read_all_touches
        @brief The method is used when all the faces are read all at once, no need to request the touches for N times.
        The list of the facets are ordered from the first side to the last side, according to
        the standard used for the device (see documentation).
        Each element of the list is a binary string where there is a one where the cell has been pressed, and zero
        when the cell is not pressed.
        The cells on each side are read from left to right and then from top to bottom.
        @return the list of device facets and each facet is a string of a binary number,
        with zero where the cell is not touched, and one where the cell has been touched.
        """
        try:
            raise NotImplemented("The method has not been implemented!")

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def update_touches(self, write_message, timeout=0.02):
        """
        The method is used to register the new values of the facets.
        @param write_message the message to send to the serial to be able to write the touch values.
        @param timeout the waiting time for the reply.
        """
        try:
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(write_message)
            time.sleep(timeout)
            return True

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def get_single_touch_messages(self, touch_message, length_reply_mpx, timeout=0.4):
        """
        The method calls the serial to read state of a single face
        @param touch_message the message to send to the serial to read a single face touch.
        @param length_reply_mpx the length of the reply message of the touch
        @param timeout the waiting time for the reply.
        @return the message of the touched cells
        """

        try:
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(touch_message)
            touch_message_bytes = None

            t_end = time.time() + timeout
            while time.time() < t_end:
                time.sleep(0.01)
                touch_message_bytes = self.serial_communication.read_binary_from(num_bytes=length_reply_mpx)
                if touch_message_bytes:
                    break

            if not touch_message_bytes:
                return None

            touch_message = list(touch_message_bytes)
            return touch_message

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def get_all_touch_messages(self, touch_message, length_reply_mpx, timeout=0.4):
        """
        The method calls the serial to read the message of the facets touches
        @param touch_message the message to send to the serial to be able to read the touch message.
        @param length_reply_mpx the length of the reply message to the touch
        @param timeout the waiting time for the reply.
        @return the message of the touched cells
        """
        try:
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(touch_message)
            touch_message_bytes = None

            t_end = time.time() + timeout
            while time.time() < t_end:
                time.sleep(0.01)
                touch_message_bytes = self.serial_communication.read_binary_from(num_bytes=length_reply_mpx)  #length_reply_mpx)
                if touch_message_bytes:
                    break

            if not touch_message_bytes:
                return None

            touch_message = list(touch_message_bytes)
            return touch_message

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return []

    def send_vibromotor_message(self, send_msg, timeout=0.05):
        """
        The method sends the messaqge to to make the icube vibrate.
        @param vibro_message the message to send
        """
        try:
            time.sleep(timeout)
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(send_msg)
            return True

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def set_vibromotor_duration_message(self, duration_msg, timeout=0.05):
        """
        The method sends the messaqe to set the duration of the vibration
        @param duration_msg the message to send
        """
        try:
            time.sleep(timeout)
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(duration_msg)
            return True

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def set_vibromotor_duty_message(self, duty_msg, timeout=0.05):
        """
        The method sends the message to set the duty of the vibration
        @param duty_msg the message to send
        """
        try:
            time.sleep(timeout)
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(duty_msg)
            return True

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def set_play_audio_message(self, play_audio_msg, timeout=0.05):
        """
        The method sends the message to splay the audio files
        @param play_audio_msg the message to send
        """
        try:
            time.sleep(timeout)
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(play_audio_msg)
            return True

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False

    def set_volume_audio_message(self, set_volume_msg, timeout=0.05):
        """
        The method sends the message to set the dvolume to play the audio files
        @param set_volume_msg the message to send
        """
        try:
            time.sleep(timeout)
            self.serial_communication.empty_serial()
            self.serial_communication.write_to(set_volume_msg)
            return True

        except Exception as e:
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False





