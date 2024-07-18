import sys
import collections
import time
import random

from PyQt5.QtGui import *
from PyQt5.QtCore import QSize, Qt, pyqtSlot, QEvent, QObject
from PyQt5.QtGui import QPixmap, QIntValidator
from PyQt5.QtWidgets import *

from qt_material import apply_stylesheet

from icube.target_ref.data_handlers.CSVgenerator import CSVFile
from icube.target_ref.data_handlers.data_collector import Datacollector
from icube.target_ref.data_handlers.constants import *

from icube.target_ref.src.icube_interface import ICubeInterfaceV3 as ICubeInterface
from icube.target_ref.src.tactile.tactile_device import TactileDevice
from icube.target_ref.src.device_commands import ICubeVersion
from icube.target_ref.src.data_handlers.aggregator import CallbackAggregator, AggregateMode
from icube.target_ref.src.data_handlers.icube_movements_classifier import GraspDetector
from icube.target_ref.src.tactile.common import tactile_logging as log

from tobiipg2.TobiiInterface import Tobii


extra = {

    # Button colors
    'danger': '#dc3545',
    'warning': '#ffc107',
    'success': '#13191c',

    # Font
    'font_family': 'Roboto',
}

# Number of trials for each subject:
n_trials = 24
# Number of conditions --> groups
n_groups = 4

# START_INSTRUCTION_SPACE = "Press the SPACEBAR to START the trial"
# STOP_INSTRUCTION_SPACE = "Press the SPACEBAR to END the trial"
# START_INSTRUCTION_GRAB = "GRAB the cube to START the trial"
# STOP_INSTRUCTION_GRAB = "PLACE the cube to END the trial"


class DemographicsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)

        # Make the form
        self.edit_id = QLineEdit("SS0")
        self.edit_id.setStyleSheet("font-size: 14pt;")

        self.edit_age = QLineEdit("-1")
        self.edit_age.setValidator(QIntValidator())
        self.edit_age.setStyleSheet("font-size: 14pt;")

        self.combo_hand = QComboBox()
        self.combo_hand.addItems(["Right", "Left"])
        self.combo_hand.setStyleSheet("font-size: 14pt;")

        layout = QFormLayout()
        lbl_id = QLabel("Subject_id")
        lbl_id.setStyleSheet("font-size: 14pt")
        lbl_old = QLabel("How old are you?")
        lbl_old.setStyleSheet("font-size: 14pt;")
        lbl_hand = QLabel("Which is your main hand?")
        lbl_hand.setStyleSheet("font-size: 14pt;")
        layout.addRow(lbl_id, self.edit_id)
        layout.addRow(lbl_old, self.edit_age)
        layout.addRow(lbl_hand, self.combo_hand)
        form = QGroupBox()
        form.setLayout(layout)

        lbl_welcome = QLabel("<b>Please enter your demographics to start playing.</b>")
        # lbl_welcome.setWordWrap(True)
        lbl_welcome.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        lbl_welcome.setStyleSheet("font-size: 25pt;")
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        main_layout = QVBoxLayout()
        main_layout.addWidget(lbl_welcome)
        main_layout.addWidget(form)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)

    def set_submit_callback(self, callback):
        self.buttons.accepted.connect(callback)

    def set_esc_callback(self, callback):
        self.buttons.rejected.connect(callback)

    def get_demographics(self):
        return self.edit_id.text(), self.edit_age.text(), self.combo_hand.currentText()


class MultiImageH(QWidget):
    def __init__(self):
        super().__init__()
        self.h_layout = QHBoxLayout(self)

    def add_image(self, path, label="", w=50, h=50):
        # Single image view
        single_image = QLabel(self)
        single_image.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        single_image.setPixmap(QPixmap(path).scaled(
            QSize(w, h), aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation
        ))

        text = QLabel(label)
        text.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        text.setStyleSheet("font-size: 20pt; font-weight: bold;")

        vl = QVBoxLayout()
        vl.addWidget(single_image, 9)
        vl.addWidget(text, 1)

        self.h_layout.addLayout(vl)

    def add_images(self, images, w=50, h=50):
        wi = w
        hi = h
        if len(images) == 1:
            wi = 500
            hi = 500
        for lbl, image_path in images.items():
            self.add_image(image_path, lbl, wi, hi)

    def clear(self):
        self.__clear_layout(self.h_layout)

    def __clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.__clear_layout(item.layout())


class LineSep(QFrame):
    # a simple Vertical line
    def __init__(self, direction="h"):
        super(LineSep, self).__init__()
        if direction == "h":
            self.setFrameShape(self.HLine | self.Sunken)
        else:
            self.setFrameShape(self.VLine | self.Sunken)


class ConditionPopUp(QDialog):
    def __init__(self, parent=None):

        super().__init__(parent)

        self.condition = None
        self.setMinimumWidth(500)
        layout = QVBoxLayout()

        self.lbl_instructions = QLabel(f"<b>New condition: {self.condition}.</b>")
        self.lbl_instructions.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.lbl_instructions.setStyleSheet("font-size: 20pt;")
        self.lbl_instructions.setWordWrap(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        layout.addWidget(self.lbl_instructions, 9)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def set_condition(self, condition):
        self.condition = condition
        self.lbl_instructions.setText(f"<b>New condition: {self.condition}.</b>")

    def set_esc_callback(self, callback):
        self.buttons.accepted.connect(callback)


class GoodbyeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumWidth(500)
        layout = QVBoxLayout()

        lbl_instructions = QLabel("<b>Thank you for playing!</b>")
        lbl_instructions.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        lbl_instructions.setStyleSheet("font-size: 20pt;")
        lbl_instructions.setWordWrap(True)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(lbl_instructions, 9)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def set_submit_callback(self, callback):
        self.buttons.accepted.connect(callback)

    def set_esc_callback(self, callback):
        self.buttons.rejected.connect(callback)


class GuiController:

    def __init__(self, resource_path=""):

        self.app = QApplication(sys.argv)
        apply_stylesheet(self.app, theme='light_blue.xml', invert_secondary=True, extra=extra)

        self.gui = TRICubeGui(resource_path=resource_path)

        self.callbacks_aggregator = CallbackAggregator(aggr_mode=AggregateMode.SYNC)
        self.data_collector = None
        self.randomizer = random.Random(time.time())
        self.tobii = Tobii()
        self.cube_reference = None
        self.cube_target = None

        self.cube_ref_init = False
        self.cube_tar_init = False

        self.trials = {}
        # self.blocks = []
        self.trials_groups = []
        self.used_groups = []
        self.trial_sequence = []
        self.handling_classifier = None
        self.next_trial_id = 0

        self.start_t_time = None
        self.start_memo_time = None
        self.start_recall_time = None
        self.stop_t_time = None

        # Bind the callbacks
        self.gui.ext_submit_demographics_callback = self.add_subject
        self.gui.ext_submit_answer_callback = self.load_answer

        self.gui.ext_skip_condition_callback = self.skip_condition
        self.gui.ext_init_cubes_button_callback = self.init_cubes
        self.gui.ext_calibrate_ref_button_callback = self.calibration_cube
        self.gui.ext_calibrate_tar_button_callback = self.calibration_cube
        self.gui.ext_init_tobii_button_callback = self.init_connect_tobii

        self.gui.ext_start_ref_button_callback = self.start_streaming_cube
        self.gui.ext_stop_ref_button_callback = self.stop_streaming_cube
        self.gui.ext_start_tar_button_callback = self.start_streaming_cube
        self.gui.ext_stop_tar_button_callback = self.stop_streaming_cube

        self.gui.ext_start_memo_button_callback = self.start_memo
        self.gui.ext_stop_memo_button_callback = self.stop_memo
        self.gui.ext_start_recall_button_callback = self.start_recall
        self.gui.ext_stop_recall_button_callback = self.stop_recall

        self.gui.ext_next_trial_sequence_callback = self.next_trial_sequence

        self.gui.ext_start_record_tobii_button_callback = self.tobii.start_recording
        self.gui.ext_stop_record_tobii_button_callback = self.tobii.stop_recording
        self.gui.ext_annotate_tobii_callback = self.tobii.send_event
        self.gui.ext_disconnect_tobii_callback = self.tobii.disconnect

    def init_cubes(self, serial_port_reference="", serial_port_target="", fake_it=False):

        """
        @A brief code to initialize the cubes, check the connection, if not connected it quits the app
        @and then renders randomly the first trial
        @param serial_port_reference: Reference cube connection port
        @param serial_port_target: Target cube connection port
        @param fake_it
        @return:
        """

        self.cube_reference = ICubeInterface(is_mocked=fake_it)
        self.cube_target = ICubeInterface(is_mocked=fake_it)

        self.cube_reference.init(name="REFERENCE", serial_port=serial_port_reference)
        self.cube_target.init(name="TARGET", serial_port=serial_port_target)

        ref_ok = self.cube_reference.device.is_device_connected(timeout=2)
        target_ok = self.cube_target.device.is_device_connected(timeout=2)

        if not (ref_ok and target_ok):
            self.app.quit()

        self.cube_reference.bind_callback(self.data_collector.push_data)
        self.cube_target.bind_callback(self.data_collector.push_data)

        if not self.trial_sequence:
            self.next_trial_sequence()
            self.randomizer.shuffle(self.trial_sequence)
            self.next_trial_id = self.trial_sequence.pop(0)
            # self.next_trial_id = random.randrange(len(self.trial_sequence))
            # (_, self.next_trial_id) = enumerate(self.next_trial)

        """
        else:
            if self.next_trial_id >= len(self.trial_sequence):
                self.next_trial_sequence()
                self.randomizer.shuffle(self.trial_sequence)
                self.next_trial_id = self.trial_sequence.pop(0)
                # self.next_trial_id = random.randrange(len(self.trial_sequence))
                # (_, self.next_trial_id) = enumerate(self.next_trial)
                return None
                """

        # Render the first trial
        trial_id = self.next_trial_id
        self.gui.render_trial(trial=self.trials[trial_id])

    def calibration_cube(self, cube_type=Icubetype, calibration_time=10):
        """
        @param: cube_type = REFERENCE / TARGET
        @return:
        """

        if cube_type == Icubetype.REFERENCE:
            self.cube_reference.calibrate(max_time=calibration_time)
        else:
            self.cube_target.calibrate(max_time=calibration_time)

    def init_connect_tobii(self, connection="", frequency=50):
        """
        @param connection: ethernet / wireless
        @param frequency: acquisition frames frequency
        @return: get_rtsp_url() method return the RTSP streaming url
        """

        self.tobii.connect(connection=connection.lower(), frequency=frequency)
        return self.tobii.get_rtsp_url()

    def init_data_collector(self, storage_path="data"):
        """
        Initialize the CSV data dumper and binds the callback
        @param storage_path:
        @return:
        """
        data_dumper = CSVFile(storage_path=storage_path)
        self.data_collector = Datacollector(persistence=data_dumper)
        # self.callbacks_aggregator.add_callback(self.data_collector.push_data)

    def init_handling_classifier(self, grab_tolerance=1):
        """
        Init the detection of grasp from the participants
        @param grab_tolerance: How much be tolerant on accelerations
        @return:
        """
        self.handling_classifier = GraspDetector(grab_tolerance=grab_tolerance)
        self.handling_classifier.set_on_grab_callback(self.__fake_spacebar)
        self.handling_classifier.set_on_pose_callback(self.__fake_spacebar)
        self.callbacks_aggregator.add_callback(self.handling_classifier.handle)

    def __fake_spacebar(self):
        """
        Fake a SPACEBAR press, to start and stop the data collection
        @return:
        """
        press("space")

    def start_streaming_cube(self, cube_type=Icubetype.REFERENCE, streaming_timeout=0.4):
        """
        @param cube_type: REFERENCE / TARGET
        @param streaming_timeout: Accepted timeout before the streaming start
        @return:
        """

        if cube_type == Icubetype.REFERENCE:
            self.cube_reference.start_streaming(timeout=streaming_timeout)
        else:
            self.cube_target.start_streaming(timeout=streaming_timeout)

    def stop_streaming_cube(self, cube_type=Icubetype.REFERENCE):
        """
        @param cube_type: REFERENCE / TARGET
        @return:
        """

        if cube_type == Icubetype.REFERENCE:
            self.cube_reference.stop_streaming()
        else:
            self.cube_target.stop_streaming()

    def add_subject(self, subject_id="", age_i=0, hand_i=Hand.RIGHT):
        """
        Add a new subject to the internal model
        @param subject_id: subject_id
        @param age_i:  subject age
        @param hand_i: subject dominant hand (right, left)
        @return:
        """
        age = int(age_i)
        hand = Hand.parse(hand_i)

        subject = self.data_collector.add_subject(subject_id=subject_id, age=age, hand=hand)
        return subject

    def add_trial(self, trial_id="", trial_condition="", need_ans=False,
                  target_image="", ref_image="", similarity=""):
        """
        Add a new trial to the internal model
        @param trial_id:   unique trial id
        @param trial_condition: HAPTIC-HAPTIC / HAPTIC-VISUO / VISUO-HAPTIC / VISUO-VISUO
        @param need_ans: True to open a dialog asking for an answer
        @param target_image: image of the target cube
        @param ref_image: image of the reference cube
        @param similarity: E/D
        @return:
        """
        trial = self.data_collector.add_trial(trial_id=trial_id, trial_condition=trial_condition, need_ans=need_ans,
                                              target_image=target_image, ref_image=ref_image, similarity=similarity)
        self.trials[trial_id] = trial

    def add_trial_group(self, sequential_group):
        """
        Add a new sequence of trials
        @param sequential_group:
        @return:
        """
        self.trials_groups.append(sequential_group)

    def next_trial_sequence(self):
        """
        Fetches the next trials sequence
        @return:
        """
        if len(self.trials_groups) == 0:
            self.trials_groups = self.used_groups

        next_group_id = self.randomizer.randrange(len(self.trials_groups))
        self.trial_sequence = self.trials_groups.pop(next_group_id)
        self.used_groups.append(self.trial_sequence)

    def start_memo(self):
        """
        Start next memorization phase
        """

        # for trial, value in self.trials.items():
        #     if value == self.next_trial_id:
        #         self.trial_random = self.trials.pop(trial)
        #         trial_id = self.trial_random[value]
        #         self.gui.render_trial(trial=self.trials[trial_id])
        #         break

        trial_id = self.next_trial_id
        self.data_collector.start_memo(trial_id)
        self.gui.phase_render(self.data_collector)

    def start_recall(self):
        """
        Start next recall phase
        """

        # trial_id = self.trial_sequence[self.next_trial_id]
        self.data_collector.start_recall(self.next_trial_id)
        self.gui.phase_render(self.data_collector)

    def stop_memo(self):

        self.data_collector.stop_memo()

    def stop_recall(self):

        self.data_collector.stop_recall()

    def load_answer(self, answer):
        """
        Stop the trial and load subject answer, which should be EQUAL or DIFFERENT
        @param answer: participant's answer
        """
        # self.next_trial_id += 1
        self.randomizer.shuffle(self.trial_sequence)
        self.next_trial_id = self.trial_sequence.pop(0)
        self.data_collector.stop_trial(answer)

        # trial_id = self.trial_sequence[self.next_trial_id]
        self.gui.render_trial(trial=self.trials[self.next_trial_id])

    def skip_condition(self):

        if len(self.trials_groups) == 0:
            self.trials_groups = self.used_groups

        self.randomizer.shuffle(self.trials_groups)
        self.trial_sequence = self.trials_groups.pop(0)
        self.used_groups.append(self.trial_sequence)

        self.randomizer.shuffle(self.trial_sequence)
        self.next_trial_id = self.trial_sequence.pop(0)
        self.gui.render_trial(trial=self.trials[self.next_trial_id])

    def close(self):
        """
        Gracefully close the communication
        @return:
        """
        self.data_collector.quit()
        self.tobii.disconnect()
        """        
        self.cube_reference.stop_streaming()
        self.cube_target.stop_streaming()
        """

    def run(self):

        return self.app.exec()


class TRICubeGui(QMainWindow):

    def __init__(self, resource_path=" ", *args, **kwargs):
        super(TRICubeGui, self).__init__(*args, **kwargs)

        # INTERNAL STATE
        self.ref_streamed = False
        self.tar_streamed = False
        self.memo_started = False
        self.recall_started = False

        self.sense_keyboard = False

        self.tobii_connected = False
        self.tobii_recording = False

        self.target_images = {}
        self.reference_images = {}
        self.current_phase = None
        self.current_condition = None
        self.current_subject = -1
        self.current_trial = -1
        self.trials_list = []
        self.answer_needed = False

        self.counter = 1

        # EXTERNAL CALLBACKS
        self.ext_submit_demographics_callback = None
        self.ext_submit_answer_callback = None

        self.ext_init_cubes_button_callback = None
        self.ext_calibrate_ref_button_callback = None
        self.ext_calibrate_tar_button_callback = None
        self.ext_init_tobii_button_callback = None

        self.ext_start_ref_button_callback = None
        self.ext_stop_ref_button_callback = None
        self.ext_start_tar_button_callback = None
        self.ext_stop_tar_button_callback = None

        self.ext_start_memo_button_callback = None
        self.ext_stop_memo_button_callback = None
        self.ext_start_recall_button_callback = None
        self.ext_stop_recall_button_callback = None

        self.ext_next_trial_sequence_callback = None
        self.ext_skip_condition_callback = None

        self.ext_start_record_tobii_button_callback = None
        self.ext_stop_record_tobii_button_callback = None
        self.ext_annotate_tobii_callback = None
        self.ext_disconnect_tobii_callback = None

    # --------------------------------------------------------------------------------------------------------------

        # Window
        self.setWindowTitle("Haptic Exploration")

        # Frame
        self.main_frame = QFrame(self)

    # --------------------------------------------------------------------------------------------------------------

        # Init Cubes
        self.init_cubes_btn = QPushButton()
        self.init_cubes_btn.setText("INIT CUBES")
        self.init_cubes_btn.setStyleSheet('font-size: 14pt;')
        self.init_cubes_btn.clicked.connect(self.init_cubes_callback)
        self.init_cubes_btn.setFocusPolicy(Qt.NoFocus)
        self.init_cubes_btn.setProperty('class', 'success')

        # Calibration CUBES
        self.calibrate_REF_btn = QPushButton()
        self.calibrate_REF_btn.setText("CALIBRATION REFERENCE")
        self.calibrate_REF_btn.setStyleSheet('font-size: 14pt;')
        self.calibrate_REF_btn.clicked.connect(self.calibration_REF_callback)
        self.calibrate_REF_btn.setFocusPolicy(Qt.NoFocus)
        self.calibrate_REF_btn.setProperty('class', 'success')
        self.calibrate_REF_btn.setEnabled(False)

        self.calibrate_TAR_btn = QPushButton()
        self.calibrate_TAR_btn.setText("CALIBRATION TARGET")
        self.calibrate_TAR_btn.setStyleSheet('font-size: 14pt;')
        self.calibrate_TAR_btn.clicked.connect(self.calibration_TAR_callback)
        self.calibrate_TAR_btn.setFocusPolicy(Qt.NoFocus)
        self.calibrate_TAR_btn.setProperty('class', 'success')
        self.calibrate_TAR_btn.setEnabled(False)

        # Connect and Disconnect TOBII
        self.drop_connection_type = QComboBox()
        self.drop_connection_type.addItems(["Ethernet", "dhcp", "Wireless", "Discover"])
        self.drop_connection_type.setStyleSheet('font-size: 14pt;')

        self.text_frequency = QLineEdit()
        self.text_frequency.setValidator(QIntValidator(0, 100))
        self.text_frequency.setStyleSheet('font-size: 14pt;')
        self.text_frequency.setPlaceholderText("Frequency")
        self.text_frequency.setProperty('class', 'success')

        self.init_tobii_btn = QPushButton()
        self.init_tobii_btn.setText("INIT TOBII")
        self.init_tobii_btn.setStyleSheet('font-size: 14pt;')
        self.init_tobii_btn.clicked.connect(self.init_tobii_callback)
        self.init_tobii_btn.setFocusPolicy(Qt.NoFocus)
        self.init_tobii_btn.setProperty('class', 'success')

        # START-STOP MEMORIZATION
        self.memo_start_stop_btn = QPushButton()
        self.memo_start_stop_btn.setText("START MEMO")
        self.memo_start_stop_btn.setStyleSheet('font-size: 14pt;')
        self.memo_start_stop_btn.clicked.connect(self.memo_start_stop_callback)
        self.memo_start_stop_btn.setFocusPolicy(Qt.NoFocus)
        self.memo_start_stop_btn.setProperty('class', 'success')
        self.memo_start_stop_btn.setEnabled(False)

        # START-STOP RECALL
        self.recall_start_stop_btn = QPushButton()
        self.recall_start_stop_btn.setText("START RECALL")
        self.recall_start_stop_btn.setStyleSheet('font-size: 14pt;')
        self.recall_start_stop_btn.clicked.connect(self.recall_start_stop_callback)
        self.recall_start_stop_btn.setFocusPolicy(Qt.NoFocus)
        self.recall_start_stop_btn.setProperty('class', 'success')
        self.recall_start_stop_btn.setEnabled(False)

        # ANSWER
        self.answer_insertion = QComboBox()
        self.answer_insertion.addItems(["EQUAL", "DIFFERENT"])
        self.answer_insertion.setStyleSheet('font-size: 14pt;')
        self.answer_insertion.activated.connect(self.submit_answer_callback)
        self.answer_insertion.setEnabled(False)

        # Skip Condition
        self.skip_condition_btn = QPushButton()
        self.skip_condition_btn.setText("SKIP")
        self.skip_condition_btn.setStyleSheet('font-size: 14pt;')
        self.skip_condition_btn.clicked.connect(self.skip_condition_callback)
        self.skip_condition_btn.setFocusPolicy(Qt.NoFocus)
        self.skip_condition_btn.setProperty('class', 'success')
        self.skip_condition_btn.setEnabled(False)

        # Record TOBII
        # self.record_tobii_btn = QPushButton()
        # self.record_tobii_btn.setText("RECORD TOBII")
        # self.record_tobii_btn.setStyleSheet('font-size: 14pt;')
        # self.record_tobii_btn.clicked.connect(self.record_tobii_callback)
        # self.record_tobii_btn.setFocusPolicy(Qt.NoFocus)
        # self.record_tobii_btn.setProperty('class', 'success')
        # self.record_tobii_btn.setEnabled(False)

    # --------------------------------------------------------------------------------------------------------------

        # Footer Layout
        self.footer_layout = QHBoxLayout()
        logo_rbcs = QLabel(self)
        logo_rbcs.setPixmap(QPixmap(f'{resource_path}/assets/logo_rbcs.png').scaled(
            QSize(40, 40), aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation
        ))
        logo_contact = QLabel(self)
        logo_contact.setPixmap(QPixmap(f'{resource_path}/assets/logo_contact.png').scaled(
            QSize(50, 50), aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation
        ))
        logo_whisper = QLabel(self)
        logo_whisper.setPixmap(QPixmap(f'{resource_path}/assets/logo_whisper.png').scaled(
            QSize(50, 50), aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation
        ))

        self.lbl_log = QLabel(self)
        self.lbl_log.setText(f"Subject: {self.current_subject} - Trial: {self.current_trial} - "
                             f"Phase: {self.current_phase}")
        self.lbl_log.setWordWrap(True)
        self.lbl_log.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_log.setStyleSheet(
            "font-size: 12pt; font-weight: bold;")

        self.footer_layout.addWidget(self.lbl_log, 15, alignment=Qt.AlignBottom)
        self.footer_layout.addWidget(logo_rbcs, 1, alignment=Qt.AlignBottom)
        self.footer_layout.addWidget(logo_contact, 1, alignment=Qt.AlignBottom)
        self.footer_layout.addWidget(logo_whisper, 1, alignment=Qt.AlignBottom)

        # Buttons Layout
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(self.drop_connection_type, )
        self.buttons_layout.addWidget(self.text_frequency, )
        self.buttons_layout.addWidget(self.init_tobii_btn, )
        # self.buttons_layout.addWidget(self.record_tobii_btn, )
        self.buttons_layout.addWidget(self.init_cubes_btn, )
        self.buttons_layout.addWidget(self.skip_condition_btn, )

        self.buttons_layout.addWidget(LineSep("h"), )

        self.buttons_layout.addWidget(self.calibrate_REF_btn, )
        self.buttons_layout.addWidget(self.calibrate_TAR_btn, )
        self.buttons_layout.addWidget(self.memo_start_stop_btn, )
        self.buttons_layout.addWidget(self.recall_start_stop_btn, )

        self.buttons_layout.addWidget(LineSep("h"), )

        self.buttons_layout.addWidget(self.answer_insertion, )

        # Images Layout
        self.body_layout = QVBoxLayout()

        self.multi_images = MultiImageH()

        self.body_layout.addWidget(self.multi_images, 15, alignment=Qt.AlignBottom)

        # Main Layout
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout, 1)
        self.layout.addWidget(LineSep("v"), )
        self.layout.addLayout(self.body_layout, 15)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.layout, 15)
        self.main_layout.addLayout(self.footer_layout, 1)

        self.main_frame.setLayout(self.main_layout)
        self.setCentralWidget(self.main_frame)

        self.show()

        # Demographics
        self.demographics_dialog = DemographicsDialog()
        self.demographics_dialog.set_submit_callback(self.submit_demographics_callback)
        self.demographics_dialog.set_esc_callback(self.demographics_dialog.close)

        # Change of condition pop-up
        self.condition_popup = ConditionPopUp()
        self.condition_popup.set_esc_callback(self.condition_popup.close)

        # Goodbye
        self.goodbye_dialog = GoodbyeDialog()
        self.goodbye_dialog.set_submit_callback(self.new_subject_callback)
        self.goodbye_dialog.set_esc_callback(self.exit_game_callback)

    # --------------------------------------------------------------------------------------------------------------
    def init_cubes_callback(self):

        self.init_cubes_btn.setEnabled(False)
        self.ext_init_cubes_button_callback(serial_port_reference="COM8", serial_port_target="COM7") # Check and change COM PORT if necessary.
        self.calibrate_REF_btn.setEnabled(True)

    def calibration_REF_callback(self):

        self.ext_calibrate_ref_button_callback(cube_type=Icubetype.REFERENCE, calibration_time=10)
        self.calibrate_REF_btn.setEnabled(False)
        self.calibrate_TAR_btn.setEnabled(True)

    def calibration_TAR_callback(self):

        self.ext_calibrate_tar_button_callback(cube_type=Icubetype.TARGET, calibration_time=10)
        self.calibrate_TAR_btn.setEnabled(False)
        self.recall_start_stop_btn.setEnabled(False)
        # self.memo_start_stop_btn.setEnabled(True)
        self.skip_condition_btn.setEnabled(True)
        self.demographics_dialog.show()

    def init_tobii_callback(self):

        if not self.tobii_connected:
            print("Tobii connection")
            self.tobii_connected = True
            self.init_tobii_btn.setText("Disconnect Tobii")
            self.init_tobii_btn.setProperty('class', 'danger')
            connection_method = self.drop_connection_type.currentText()
            frequency = self.text_frequency.text()
            if frequency == '':
                frequency = 50
            else:
                frequency = int(frequency)

            self.ext_init_tobii_button_callback(connection=connection_method, frequency=frequency)
            # self.record_tobii_btn.setEnabled(True)

        else:
            print("Disconnect")
            self.tobii_connected = False
            self.init_tobii_btn.setText("Connect Tobii")
            self.init_tobii_btn.setProperty('class', 'success')
            self.ext_disconnect_tobii_callback()

    def record_tobii_callback(self):

        if not self.tobii_recording:
            self.tobii_recording = True
            self.ext_start_record_tobii_button_callback()
            self.record_tobii_btn.setText("STOP Tobii Recording")
            self.record_tobii_btn.setProperty('class', 'success')
        else:
            self.tobii_recording = False
            self.ext_stop_record_tobii_button_callback()
            self.record_tobii_btn.setText('START Tobii Recording')
            self.record_tobii_btn.setProperty('class', 'success')

    def memo_start_stop_callback(self):

        if not self.memo_started:
            self.memo_started = True
            self.ref_streamed = True
            self.memo_start_stop_btn.setText("STOP MEMO")
            self.memo_start_stop_btn.setProperty('class', 'danger')
            self.ext_start_ref_button_callback(cube_type=Icubetype.REFERENCE)
            self.ext_start_memo_button_callback()
            self.ext_annotate_tobii_callback(ev_type="Start Memo", value=self.current_trial)

        else:
            self.memo_started = False
            self.ref_streamed = False
            self.memo_start_stop_btn.setText("START MEMO")
            self.memo_start_stop_btn.setProperty('class', 'danger')
            self.ext_stop_memo_button_callback()
            self.ext_stop_ref_button_callback(cube_type=Icubetype.REFERENCE)
            self.recall_start_stop_btn.setEnabled(True)
            self.answer_insertion.setEnabled(False)
            self.memo_start_stop_btn.setEnabled(False)
            self.ext_annotate_tobii_callback(ev_type="Stop Memo", value=self.current_trial)

    def recall_start_stop_callback(self):

        if not self.recall_started:
            self.recall_started = True
            self.tar_streamed = True
            self.recall_start_stop_btn.setText("STOP RECALL")
            self.recall_start_stop_btn.setProperty('class', 'danger')
            self.ext_start_tar_button_callback(cube_type=Icubetype.TARGET)
            self.ext_start_recall_button_callback()
            self.ext_annotate_tobii_callback(ev_type="Start Recall", value=self.current_trial)

        else:
            self.recall_started = False
            self.tar_streamed = False
            self.recall_start_stop_btn.setText("START RECALL")
            self.recall_start_stop_btn.setProperty('class', 'danger')
            self.ext_stop_recall_button_callback()
            self.ext_stop_tar_button_callback(cube_type=Icubetype.TARGET)
            self.ext_annotate_tobii_callback(ev_type="Stop Recall", value=self.current_trial)
            self.answer_insertion.setEnabled(True)
            self.recall_start_stop_btn.setEnabled(False)

    def submit_answer_callback(self):

        self.counter += 1

        self.answer_insertion.setEnabled(False)
        self.multi_images.clear()
        ans = self.answer_insertion.currentText()
        self.ext_submit_answer_callback(ans)
        self.memo_start_stop_btn.setEnabled(True)

        if self.counter % (n_trials/n_groups) == 0:
            self.ext_next_trial_sequence_callback()

        if len(self.trials_list) > 0 and len(self.trials_list) % n_trials == 0:
            self.goodbye_dialog.show()

        if self.condition_popup.condition != self.current_condition:
            self.condition_popup.set_condition(self.current_condition)
            self.condition_popup.show()

    def skip_condition_callback(self):

        self.multi_images.clear()
        self.memo_start_stop_btn.setEnabled(True)
        self.ext_skip_condition_callback()

        if self.condition_popup.condition != self.current_condition:
            self.condition_popup.set_condition(self.current_condition)
            self.condition_popup.show()

    # --------------------------------------------------------------------------------------------------------------
    @pyqtSlot()
    def submit_demographics_callback(self):
        subject, age, hand = self.demographics_dialog.get_demographics()
        subj = self.ext_submit_demographics_callback(subject, age, hand)
        if subj is not None:
            self.__blur_remove()
            self.demographics_dialog.close()
            self.current_subject = subj.subject_id
            self.lbl_log.setText(f"Subject: {self.current_subject} - Trial: {self.current_trial} - Phase: "
                                 f"{self.current_phase}")

        if self.condition_popup.condition != self.current_condition:
            self.condition_popup.set_condition(self.current_condition)
            self.condition_popup.show()

        self.memo_start_stop_btn.setEnabled(True)

    @pyqtSlot()
    def new_subject_callback(self):
        self.goodbye_dialog.hide()
        self.demographics_dialog.show()

    @pyqtSlot()
    def exit_game_callback(self):
        self.goodbye_dialog.close()
        self.close()

    def __blur_apply(self):
        # Blur the Background
        p_blur = QGraphicsBlurEffect()
        p_blur.setBlurRadius(10)
        p_blur.setBlurHints(QGraphicsBlurEffect.QualityHint)
        self.main_frame.setGraphicsEffect(p_blur)

    def __blur_remove(self):
        self.main_frame.setGraphicsEffect(None)

    def render_trial(self, trial):

        self.current_trial = trial.trial_id
        self.current_condition = trial.trial_condition
        self.lbl_log.setText(f"Subject: {self.current_subject} - Trial: {self.current_trial} - Condition: "
                             f"{self.current_condition}")

        self.trials_list.append(self.current_trial)

        self.__render_multi_images(trial.ref_image)
        self.__render_multi_images(trial.target_image)

        self.answer_needed = trial.need_ans
        self.sense_keyboard = True

    def phase_render(self, data):

        self.current_phase = data.phase
        self.lbl_log.setText(f"Subject: {self.current_subject} - Trial: {self.current_trial} - Condition: "
                             f"{self.current_condition} - {self.current_phase}")

    def __render_multi_images(self, images, w=200, h=200):

        self.multi_images.add_images(images, w, h)
        self.multi_images.show()
