import math
import os
import keyboard

from PyQt5 import QtWidgets, QtGui, uic
from modules.hardwaremanager.hardwaremanager_inputtypes import HardwareInputTypes


class JOANKeyboardProcess:
    """
    Main class for the Keyboard input in a seperate multiprocess, this will loop!. Make sure that the things you do
    in this class are serializable, else it will fail.
    """

    def __init__(self, settings, shared_variables):
        self.settings = settings

        self.shared_variables = shared_variables

        # Initialize needed variables:
        self._throttle = False
        self._brake = False
        self._steer_left = False
        self._steer_right = False
        self._handbrake = False
        self._reverse = False
        self._data = {}

        keyboard.hook(self.key_event, False)

    def key_event(self, key):
        """
        Distinguishes which key (that has been set before) is pressed and sets a boolean for the appropriate action.
        :param key:
        :return:
        """
        boolean_key_press_value = key.event_type == keyboard.KEY_DOWN
        int_key_identifier = QtGui.QKeySequence(key.name)[0]

        if int_key_identifier == self.settings.throttle_key:
            self._throttle = boolean_key_press_value
        elif int_key_identifier == self.settings.brake_key:
            self._brake = boolean_key_press_value
        elif int_key_identifier == self.settings.steer_left_key:
            self._steer_left = boolean_key_press_value
            if boolean_key_press_value:
                self._steer_right = False
        elif int_key_identifier == self.settings.steer_right_key:
            self._steer_right = boolean_key_press_value
            if boolean_key_press_value:
                self._steer_left = False
        elif int_key_identifier == self.settings.handbrake_key:
            self._handbrake = boolean_key_press_value
        elif int_key_identifier == self.settings.reverse_key and boolean_key_press_value:
            self._reverse = not self._reverse

    def do(self):
        """
        Processes all the inputs of the keyboard input and writes them to self._data which is then written to the news
        in the action class
        :return: self._data a dictionary containing :
            self.shared_variables.brake = self.brake
            self.shared_variables.throttle = self.throttle
            self.shared_variables.steering_angle = self.steer
            self.shared_variables.handbrake = self.handbrake
            self.shared_variables.reverse = self.reverse
        """

        brake_temp = self.shared_variables.brake
        throttle_temp = self.shared_variables.throttle
        steer_temp = self.shared_variables.steering_angle

        # Throttle:
        if self._throttle and throttle_temp < 1:
            throttle_temp = throttle_temp + (0.05 * self.settings.throttle_sensitivity / 100)
        elif throttle_temp > 0 and not self._throttle:
            throttle_temp = throttle_temp - (0.05 * self.settings.throttle_sensitivity / 100)
        elif throttle_temp < 0:
            throttle_temp = 0
        elif throttle_temp > 1:
            throttle_temp = 1

        # Brake:
        if self._brake and brake_temp < 1:
            brake_temp = brake_temp + (0.05 * self.settings.brake_sensitivity / 100)
        elif brake_temp > 0 and not self._brake:
            brake_temp = brake_temp - (0.05 * self.settings.brake_sensitivity / 100)
        elif brake_temp < 0:
            brake_temp = 0
        elif brake_temp > 1:
            brake_temp = 1

        # Steering:
        if self._steer_left and self.settings.max_steer >= steer_temp >= self.settings.min_steer:
            steer_temp -= (self.settings.steer_sensitivity / 2500)
        elif self._steer_right and self.settings.min_steer <= steer_temp <= self.settings.max_steer:
            steer_temp += (self.settings.steer_sensitivity / 2500)

        if steer_temp > 0 and self.settings.auto_center:
            steer_temp -= .25 * (self.settings.steer_sensitivity / 2500)
        elif steer_temp < 0 and self.settings.auto_center:
            steer_temp += .25 * (self.settings.steer_sensitivity / 2500)

        if abs(steer_temp) < 0.5 * self.settings.steer_sensitivity / 2500:
            steer_temp = 0

        # Reverse
        reverse_temp = self._reverse
        handbrake_temp = self._handbrake

        # Set the shared variables again:
        self.shared_variables.brake = brake_temp
        self.shared_variables.throttle = throttle_temp
        self.shared_variables.steering_angle = steer_temp
        self.shared_variables.handbrake = handbrake_temp
        self.shared_variables.reverse = reverse_temp


class KeyBoardSettings:
    """
    Default keyboardinput settings that will load whenever a keyboardinput class is created.
    """

    def __init__(self, identifier=''):
        self.steer_left_key = QtGui.QKeySequence('a')[0]
        self.steer_right_key = QtGui.QKeySequence('d')[0]
        self.throttle_key = QtGui.QKeySequence('w')[0]
        self.brake_key = QtGui.QKeySequence('s')[0]
        self.reverse_key = QtGui.QKeySequence('r')[0]
        self.handbrake_key = QtGui.QKeySequence('space')[0]
        self.identifier = identifier
        self.input_type = HardwareInputTypes.KEYBOARD.value

        # Steering Range
        self.min_steer = - 0.5 * math.pi
        self.max_steer = 0.5 * math.pi

        # Check auto center
        self.auto_center = True

        # Sensitivities
        self.steer_sensitivity = float(50.0)
        self.throttle_sensitivity = float(50.0)
        self.brake_sensitivity = float(50.0)

    def as_dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.identifier)

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)


class KeyBoardSettingsDialog(QtWidgets.QDialog):
    """
    Class for the settings Dialog of a keyboardinput, this class should pop up whenever it is asked by the user or when
    creating the joystick class for the first time. NOTE: it should not show whenever settings are loaded by .json file.
    """

    def __init__(self, module_manager=None, settings=None, parent=None):
        """
        Initializes the settings dialog with the appropriate keyboardinput settings
        :param settings:
        :param parent:
        """
        super().__init__(parent)
        self.module_manager = module_manager
        self.keyboard_settings = settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/keyboard_settings_ui.ui"), self)

        self.slider_steer_sensitivity.valueChanged.connect(
            lambda new_value: self.label_steer_sensitivity.setText(str(new_value)))
        self.slider_throttle_sensitivity.valueChanged.connect(
            lambda new_value: self.label_throttle_sensitivity.setText(str(new_value)))
        self.slider_brake_sensitivity.valueChanged.connect(
            lambda new_value: self.label_brake_sensitivity.setText(str(new_value)))

        self._set_key_counter = 0

        self.btn_set_keys.clicked.connect(self._start_key_setting_sequence)
        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)

        self.set_key_sequence_labels = [self.label_steer_left, self.label_steer_right, self.label_throttle,
                                        self.label_brake, self.label_reverse,
                                        self.label_handbrake]

        self.display_values()

    def accept(self):
        """
        Accepts the selected settings and saves them internally.
        NOTE: will return an error if trying to set 2 buttons for the same functionality
        :return:
        """
        all_desired_keys = [self.label_steer_left.text(), self.label_steer_right.text(), self.label_throttle.text(),
                            self.label_brake.text(),
                            self.label_reverse.text(), self.label_handbrake.text()]
        if len(all_desired_keys) != len(set(all_desired_keys)):
            answer = QtWidgets.QMessageBox.warning(self, 'Warning',
                                                   'So are trying to set the same key for two command, this may lead '
                                                   'to undesired behavior. Are you sure?',
                                                   buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if answer == QtWidgets.QMessageBox.Cancel:
                return

        self.keyboard_settings.min_steer = self.spin_box_min_steer.value()
        self.keyboard_settings.max_steer = self.spin_box_max_steer.value()
        self.keyboard_settings.auto_center = self.checkbox_autocenter.isChecked()
        self.keyboard_settings.steer_sensitivity = self.slider_steer_sensitivity.value()
        self.keyboard_settings.brake_sensitivity = self.slider_brake_sensitivity.value()
        self.keyboard_settings.throttle_sensitivity = self.slider_throttle_sensitivity.value()

        self.keyboard_settings.steer_left_key = QtGui.QKeySequence(self.label_steer_left.text())[0]
        self.keyboard_settings.steer_right_key = QtGui.QKeySequence(self.label_steer_right.text())[0]
        self.keyboard_settings.throttle_key = QtGui.QKeySequence(self.label_throttle.text())[0]
        self.keyboard_settings.brake_key = QtGui.QKeySequence(self.label_brake.text())[0]
        self.keyboard_settings.reverse_key = QtGui.QKeySequence(self.label_reverse.text())[0]
        self.keyboard_settings.handbrake_key = QtGui.QKeySequence(self.label_handbrake.text())[0]
        super().accept()

    def display_values(self, settings=None):
        """
        Displays the settings that are currently being used (internally)
        :param settings:
        :return:
        """
        if not settings:
            settings = self.keyboard_settings

        self.label_steer_left.setText(QtGui.QKeySequence(settings.steer_left_key).toString())
        self.label_steer_right.setText(QtGui.QKeySequence(settings.steer_right_key).toString())
        self.label_throttle.setText(QtGui.QKeySequence(settings.throttle_key).toString())
        self.label_brake.setText(QtGui.QKeySequence(settings.brake_key).toString())
        self.label_reverse.setText(QtGui.QKeySequence(settings.reverse_key).toString())
        self.label_handbrake.setText(QtGui.QKeySequence(settings.handbrake_key).toString())

        self.spin_box_min_steer.setValue(settings.min_steer)
        self.spin_box_max_steer.setValue(settings.max_steer)

        self.checkbox_autocenter.setChecked(settings.auto_center)

        self.slider_steer_sensitivity.setValue(settings.steer_sensitivity)
        self.slider_throttle_sensitivity.setValue(settings.throttle_sensitivity)
        self.slider_brake_sensitivity.setValue(settings.brake_sensitivity)

    def _set_default_values(self):
        """
        Sets the settings as they are described in 'hardwarempSettings => KeyboardSettings)
        :return:
        """
        self.display_values(HardwareInputTypes.KEYBOARD.settings(self.keyboard_settings.identifier))

    def _start_key_setting_sequence(self):
        """
        Starts the sequence that will run through the different available inputs.
        :return:
        """
        self.btn_set_keys.setStyleSheet("background-color: lightgreen")
        self.btn_set_keys.clearFocus()
        self.button_box_settings.setEnabled(False)
        self.btn_set_keys.setEnabled(False)
        self._set_key_counter = 0
        self.set_key_sequence_labels[self._set_key_counter].setStyleSheet("background-color: lightgreen")

    def keyPressEvent(self, event):
        """
        Overwrites the built in 'keyPressEvent' function of PyQt with this function. Checks which key is pressed
        and handles it accordingly.
        :param event:
        :return:
        """
        if self.btn_set_keys.isChecked():
            try:
                self.set_key_sequence_labels[self._set_key_counter].setText(QtGui.QKeySequence(event.key()).toString())
                self.set_key_sequence_labels[self._set_key_counter].setStyleSheet("background-color: none")
                self.set_key_sequence_labels[self._set_key_counter + 1].setStyleSheet("background-color: lightgreen")
                self._set_key_counter += 1
            except IndexError:  # reached the last key
                self.btn_set_keys.setChecked(False)
                self.btn_set_keys.setStyleSheet("background-color: none")
                self._set_key_counter = 0
                self.button_box_settings.setEnabled(True)
                self.btn_set_keys.setEnabled(True)
