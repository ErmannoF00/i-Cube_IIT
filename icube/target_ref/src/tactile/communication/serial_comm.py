#! /usr/bin/python

import serial
import serial.tools.list_ports
import binascii

from icube.target_ref.src.tactile.common import utilities as utils
from icube.target_ref.src.tactile.common import tactile_logging as log


class SerialComm:
    """
    @class SerialComm
    Class which deals with the communications with a standard serial port..
    Il it essentially a wrapper to pyserial
    """
    ser = None

    def configure_serial_port(self, serial_port=""):
        """
        @function configureSerialPort
        It configures the serial connection
        @param
        @return
        """
        try:

            # Get all the connected ports available
            ports = serial.tools.list_ports.comports()
            message = f"There are {len(ports)} available serial ports."
            if len(ports) == 0:
                raise Exception("No iCube connected!!")

            log.info(message)
            utils.print(message)

            for port in ports:
                # Check the port has the string ttyUSB in it.
                # if "ttyUSB" in port.device:

                try:
                    if serial_port != "":
                        if port.device == serial_port:
                            self.ser = serial.Serial(port=port.device, baudrate=250000, timeout=0.1,
                                                     bytesize=serial.EIGHTBITS,
                                                     parity=serial.PARITY_NONE,
                                                     stopbits=serial.STOPBITS_ONE)  # open serial port
                            if self.ser.is_open:
                                log.info(f"Succesfully connected to port {port.device}")
                                break
                    else:
                        log.info(f"Try {port.device}")
                        self.ser = serial.Serial(port=port.device, baudrate=250000, timeout=0.1,
                                                 bytesize=serial.EIGHTBITS,
                                                 parity=serial.PARITY_NONE,
                                                 stopbits=serial.STOPBITS_ONE)  # open serial port

                        if self.ser.is_open:
                            log.info(f"The port which connects to the device is {port.device}")
                            log.info("Next time please specify the port")
                            break

                except serial.SerialException as e:
                    print(utils.get_exception_message(e))
                    continue

        except Exception as e:
            print(utils.get_exception_message(e))
            log.exception(str(e) + ' ' + log.get_debug_info())
            return False
        return True

    def open_comm(self):
        """
        @function openComm
        Open the serial port to start communication
        @param
        @return
        """
        try:
            if self.ser is not None:
                self.ser.open()

        except Exception as e:
            print(utils.get_exception_message(e))
            log.exception(str(e) + ' ' + log.get_debug_info())

    def check_port_is_open(self):
        """
        @function checkPortIsOpen
        It call isOpen from the package serial to check s the serial port is open or not.
        It writes a comment after checking.
        @param
        @return
        """
        try:
            if self.ser is not None:
                if self.ser.isOpen():
                    utils.print("The serial port is open")
                    utils.print("Name: " + self.ser.name)
                else:
                    utils.print("The serial port is not open.")
            pass

        except Exception as e:
            print(utils.get_exception_message(e))
            log.exception(str(e) + ' ' + log.get_debug_info())

    def close_comm(self):
        """
        @function closeComm
        Closes the communication with the XBee
        @param
        @return
        """
        try:
            if self.ser is not None:
                self.ser.close()

        except Exception as e:
            print(utils.get_exception_message(e))
            log.exception(str(e) + ' ' + log.get_debug_info())

    def write_to(self, message):
        """
        @function writeTo
        It writes a message/character to the serial device
        Given the string in input it adds a carriage return character otherwise the message is not sent to TAMO
        @param string: the message/character to write
        @return
        """
        try:
            if self.ser is not None:
                self.ser.write(serial.to_bytes(message))
        except Exception as e:
            print(utils.get_exception_message(e))
            log.exception(str(e) + ' ' + log.get_debug_info())

    def read_from(self, num_bytes=1, end_msg=''):
        """
        @function readFrom
        Reads the output from the device
        @param
        @return the message just read.
        """
        try:
            if self.ser is not None:
                out = ''
                while self.ser.in_waiting > 0:
                    read_byte = self.ser.read(num_bytes)
                    read_string = binascii.hexlify(read_byte).decode('utf-8')
                    out += read_string
                    if len(read_byte) == num_bytes:
                        break

                if out != '':
                    return out
                else:
                    return None

        except Exception as e:
            print(utils.get_exception_message(e))
            log.exception(str(e) + ' ' + log.get_debug_info())

    def read_binary_from(self, num_bytes=1, end_msg=''):
        """
        @function read_binary_from
        Reads the output from the device
        @param
        @return the message just read.
        """
        try:
            if self.ser is not None:
                read_byte = None
                while self.ser.in_waiting > 0:
                    read_byte = self.ser.read(num_bytes)
                    if len(read_byte) == num_bytes:
                        break
                return read_byte
        except Exception as e:
            print(utils.get_exception_message(e))
            log.exception(str(e) + ' ' + log.get_debug_info())

    def empty_serial(self):
        """
        @function emptySerial
        It empties the buffer of the serial port
        @param
        @return
        """
        try:
            if self.ser is not None:
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()

        except Exception as e:
            print(utils.get_exception_message(e))
            log.exception(str(e) + ' ' + log.get_debug_info())
