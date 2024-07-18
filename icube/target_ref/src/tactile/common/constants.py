#! /usr/bin/python3

print_for_debug = True  # When True it will print on screen debug information.

separation_character = u'\t'

# firmware parameters
use_firmware_03 = True
use_tracking_mode = False

# choice of language
language = 'it'

# parameters of calibration
calibrate = False
restartCalibration = False

# plot 3D object
plot = False

# rendering constants
size_status = 10

class Acceleration_limits:
    acc_x_digit = 88
    acc_y_digit = 89
    acc_z_digit = 90
    acc_end_digit = 0

class Debug:
    active = False

    figure = 'circle'
    # None
    # 'circle'
    # 'horizontal-cylinder'
    # 'vertical-cylinder'
    # 'horizontal-ellipse'
    # 'vertical-ellipse'
    # 'ziggurat'
