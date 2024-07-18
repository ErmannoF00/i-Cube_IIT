#! /usr/bin/python

import traceback
import sys
import os
import errno
import builtins as __builtin__
import json

from icube.target_ref.src.tactile.common import constants as consts
from icube.target_ref.src.tactile.common import tactile_logging as log
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

# termocolor need install termocolor package
# sudo apt-get install python3-termcolor (for python3.x)
# sudo apt-get install python-termcolor  (for python 2.x)
# usage : print(colored('hello', 'red'), colored('world', 'green'))
#from termcolor import colored


def get_exception_message(exc):
    """
    @function get_exception_message
    It gets the exception message and returns a
    colored printable message
    """
    string = "Error: " + str(exc) + "\n" + log.get_debug_info()
    return json.dumps({"string": string})


def get_list_of_members(class_object):
    """
    @function get_list_of_members
    class_object the object of the class you want the members of
    """
    return [attr for attr in dir(class_object()) if not callable(getattr(class_object(), attr)) and not attr.startswith("__")]


def strip_last_character(string, character='\\'):
    """
    @function strip_last_character
    It removes the last character from the input string if the last character is
    the same as the one passed as input character.
    By default the input character is the \ backslash
    @param string the string to remove the character from
    @param character the character to remove from the input string
    @return the output string
    """
    try:
        return string.rstrip(character)

    except Exception as e:
        print(get_exception_message(e))
        log.exception(str(e) + ' ' + log.get_debug_info())

def create_folder_if_not_exists(path_file):
    """
    @function create_folder_if_not_exists
    The function checks if the folder exists, if it does not, it creates the missing file.
    @param path_file the path of the file which we need to create if it does not exist.
    """
    try:
        # create directory of not exist
        if not os.path.exists(os.path.dirname(path_file)):
            try:
                os.makedirs(os.path.dirname(path_file))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise Exception(u'Folder does not exists')
    except Exception as e:
        print(get_exception_message(e))
        log.exception(str(e) + ' ' + log.get_debug_info())

def print(*args):
    """
    @function print
    this method overrides the python print so that
    it prints with the format we want and also when we want.
    @param *args the arguments to print
    """

    if consts.print_for_debug:
        __builtin__.print(*args)

def print_json(string):
    """
    @function print_json
    this method takes a string as input and it creates a jon packet to send to
    the javascript counterpart to be printed.
    @param *args the arguments to send a json string
    """
    # list_strings = []
    # for arg in args:
    #     list_strings.append(arg)
    #
    # string = ' '.join(list_strings)
    #

    data = {}
    data['string'] = string
    # import json
    json_data = json.dumps(data)
    print(json_data)

def get_confirm_exercise_name(name):
    return ' '.join([u'Are you sure ',  name,  u' is correct?', u'Please confirm it'])

# def confirm_message_box(parent, question, caption="Yes or No?"):
#     """
#     @fn confirm_message_box
#     @brief Message box which asks to confirm your choice
#     @param question question to display
#     @param caption the caption on top of the window
#     """
#     dlg = wx.MessageDialog(parent, question, caption, wx.YES_NO | wx.ICON_QUESTION)
#     result = dlg.ShowModal() == wx.ID_YES
#     dlg.Destroy()
#     return result
#
#
# def info_message_box(parent, message, caption="Info:"):
#     """
#     @fn info_message_box
#     @brief Message box which displays info to the user
#     @param message message to display
#     @param caption the caption on top of the window
#     """
#     dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)
#     dlg.ShowModal()
#     dlg.Destroy()
#
#
# def warn_message_box(parent, message, caption="Warning:"):
#     """
#     @fn confirm_message_box
#     @brief Message box which displays warning to the user
#     @param message message to display
#     @param caption the caption on top of the window
#     """
#     dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_WARNING)
#     dlg.ShowModal()
#     dlg.Destroy()def confirm_message_box(parent, question, caption="Yes or No?"):
#     """
#     @fn confirm_message_box
#     @brief Message box which asks to confirm your choice
#     @param question question to display
#     @param caption the caption on top of the window
#     """
#     dlg = wx.MessageDialog(parent, question, caption, wx.YES_NO | wx.ICON_QUESTION)
#     result = dlg.ShowModal() == wx.ID_YES
#     dlg.Destroy()
#     return result
#
#
# def info_message_box(parent, message, caption="Info:"):
#     """
#     @fn info_message_box
#     @brief Message box which displays info to the user
#     @param message message to display
#     @param caption the caption on top of the window
#     """
#     dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)
#     dlg.ShowModal()
#     dlg.Destroy()
#
#
# def warn_message_box(parent, message, caption="Warning:"):
#     """
#     @fn confirm_message_box
#     @brief Message box which displays warning to the user
#     @param message message to display
#     @param caption the caption on top of the window
#     """
#     dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_WARNING)
#     dlg.ShowModal()
#     dlg.Destroy()

def remove_special_character_from_string(input_string):
    """
    @function remove_special_character_from_string
    This method all the special characeter from the input string.
    @param input_string the string to remove the characters from.
    """
    input_string = input_string.replace(":", "")
    input_string = input_string.replace("/", "")
    input_string = input_string.replace("!", "")
    input_string = input_string.replace("*", "")
    input_string = input_string.replace("^", "")
    input_string = input_string.replace("&", "")
    input_string = input_string.replace("(", "")
    input_string = input_string.replace(")", "")
    input_string = input_string.replace("%", "")
    input_string = input_string.replace("-", "")
    input_string = input_string.replace("+", "")
    input_string = input_string.replace("=", "")
    input_string = input_string.replace("{", "")
    input_string = input_string.replace("}", "")
    input_string = input_string.replace("[", "")
    input_string = input_string.replace("]", "")
    input_string = input_string.replace(";", "")
    input_string = input_string.replace("@", "")
    input_string = input_string.replace("~", "")
    input_string = input_string.replace("#", "")
    input_string = input_string.replace("<", "")
    input_string = input_string.replace(">", "")
    input_string = input_string.replace(",", "")
    input_string = input_string.replace(".", "")
    input_string = input_string.replace("?", "")
    input_string = input_string.replace("/", "")
    input_string = input_string.replace("`", "")
    input_string = input_string.replace("|", "")
    input_string = input_string.replace("|", "")
    input_string = input_string.replace("'", "")

    return input_string


def replace(file_path, old_string, new_string):
    """
    Method used to replace a string in a file.

    It will replace the string in memory,
    delete the old file and create a new file with the changed string.
    The string will be replaced with the new_string.
    The old_string is the string which will be substituted,
    @param file_path the path where the file is stored
    @param old_string the string to replace
    @param new_string the new string to replace to.
    """
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(old_string, new_string))
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)


################################################
##########  COLORS WITH THE CONSOLE ############
################################################
console_white_blue_background = '0;97;44'
console_white_green_background = '0;97;42'

# Drawn in colors and bold.
# example:
# c(u'The working path is: ', red)
####
# with 107 you have white a background color.
# The problem raises if you are running from the terminal, in this case it would be ideal to have a black background.
# Then changes it to 49, The default background color
####
class Colors:
    background_black = '49'
    background_white = '107'
    background_color = background_white

    red = '1;31;' + background_color     # red = '1;31;49'
    green= '1;32;' + background_color    # green= '1;32;49'
    yellow = '1;33;' + background_color  # yellow = '1;33;49'
    blue = '1;34;' + background_color    # blue = '1;34;49'
    magenta = '1;35;' + background_color # magenta = '1;35;49'
    cyan = '1;36;' + background_color    # cyan = '1;36;49'


def get_colored_string(text, color):
    """
    The method returns a string which, when printed, is displayes with the color specified by the input variable (color) on the console.
    @param text the text to print
    @param color the color to print
    @return the formatted string to print.
    """
    # http://misc.flogisoft.com/bash/tip_colors_and_formatting
    # or
    # https://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
    #
    # for the list of colors.
    # the last 2 digits are the background, 48 is white background.
    string_to_print = '\x1b[' + color + 'm' + text + '\x1b[0m'
    return string_to_print
