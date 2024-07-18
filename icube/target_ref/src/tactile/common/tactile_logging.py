#!/usr/bin/env python
# -*- coding: iso8859-15 -*-
#-*-coding:utf-8-*-

"""
@package logging
File for logging
It can display a different message according to the type.
It could be info, warning, error or exception.
@author Goccia and Zenzeri
@date 10/02/2014
@copyright Istituto Italiano di Tecnologia (iit) 2014
"""
import logging.config
import traceback
import sys
import os.path
from icube.target_ref.src.tactile.common.paths import Paths as paths
import icube.target_ref.src.tactile.common.device_info as device_info


def initLogger():
    """
    @function initLogger
    It initialises the file logger.
    """
    dictLogConfig = {
        "version": 1,
        "handlers": {
                    "rotHandler": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "formatter": "myFormatter",
                        "filename": os.path.join(paths.logs, f"{device_info.name}.log"),
                        "maxBytes":  500000,
                        "backupCount": 10,
                        }
                    },
        "loggers": {
            "wristbotDash": {
                "handlers": ["rotHandler"],
                "level": "INFO",
                }
            },

        "formatters": {
            "myFormatter": {
                "format": "%(asctime)s-%(levelname)s- %(message)s"
                }
            }
        }

    logging.config.dictConfig(dictLogConfig)
    return logging.getLogger("wristbotDash")

def info(message):
    """
    @function info
    Different message in case of an info message.
    """
    logger = initLogger()
    logger.info(message)
    print(f"info: {message}")

def warning(message):
    """
    @function warning
    Different message in case of a warning message.
    """
    logger = initLogger()
    logger.warning(message)
    print(f"warning: {message}")

def error(message):
    """
    @function error
    Different message in case of an error message.
    """
    logger = initLogger()
    logger.error(message)
    print(f"error: {message}")

def exception(message):
    """
    @function exception
    Different message in case of an exception message.
    """
    logger = initLogger()
    logger.exception(message)
    print(f"exception: {message}")

def get_debug_info():
    """
    @function get_debug_info
    This method returns the string with the information of what
    caused the exception to be raised.

    @return string the value with the debug info to write on the log file
    """
    string = ""
    for frame in traceback.extract_tb(sys.exc_info()[2]):

        file_name, line_no, function, text = frame

        if file_name is None:
            file_name = ''
        if line_no is None:
            line_no = ''
        if function is None:
            function = ''
        if text is None:
            text = ''

        string += " in file: " + str(file_name) + \
                  " line no: " + str(line_no) +  \
                  " function: " + function + \
                  " text: " + text + "\n"

    return string
