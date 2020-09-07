import math
import multiprocessing as mp
import os
import time

from PyQt5 import uic, QtWidgets

from modules.hardwaremanager.action.hardwaremanagersettings import SensoDriveSettings
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.hardwaremanager.action.inputclasses.joan_sensodrive_communication import SensoDriveComm
from modules.hardwaremanager.action.inputclasses.joan_sensodrive_shared_values import SensoDriveSharedValues
from modules.joanmodules import JOANModules
from core.statesenum import State


class SensoDriveSettingsDialog(QtWidgets.QDialog):
    """
    Class for the settings Dialog of a SensoDrive, this class should pop up whenever it is asked by the user or when
    creating the joystick class for the first time. NOTE: it should not show whenever settings are loaded by .json file.
    """

    def __init__(self, sensodrive_settings, parent=None):
        super().__init__(parent)
        self.sensodrive_settings = sensodrive_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/sensodrive_settings_ui.ui"), self)

        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)

        self.btn_apply.clicked.connect(self.update_parameters)

        self._display_values()

    def update_parameters(self):
        """
        Updates the parameters without closing the dialog
        """
        self.sensodrive_settings.endstops = self.spin_endstop_position.value()
        self.sensodrive_settings.torque_limit_between_endstops = self.spin_torque_limit_between_endstops.value()
        self.sensodrive_settings.torque_limit_beyond_endstops = self.spin_torque_limit_beyond_endstops.value()
        self.sensodrive_settings.friction = self.spin_friction.value()
        self.sensodrive_settings.damping = self.spin_damping.value()
        self.sensodrive_settings.spring_stiffness = self.spin_spring_stiffness.value()

    def accept(self):
        """
        Accepts the settings of the sensodrive and saves them internally.
        :return:
        """
        self.sensodrive_settings.endstops = self.spin_endstop_position.value()
        self.sensodrive_settings.torque_limit_between_endstops = self.spin_torque_limit_between_endstops.value()
        self.sensodrive_settings.torque_limit_beyond_endstops = self.spin_torque_limit_beyond_endstops.value()
        self.sensodrive_settings.friction = self.spin_friction.value()
        self.sensodrive_settings.damping = self.spin_damping.value()
        self.sensodrive_settings.spring_stiffness = self.spin_spring_stiffness.value()

        super().accept()

    def _display_values(self, settings_to_display=None):
        """
        Displays the currently used settings in the settings dialog.
        :param settings_to_display:
        :return:
        """
        if not settings_to_display:
            settings_to_display = self.sensodrive_settings

        self.spin_endstop_position.setValue(settings_to_display.endstops)
        self.spin_torque_limit_between_endstops.setValue(settings_to_display.torque_limit_between_endstops)
        self.spin_torque_limit_beyond_endstops.setValue(settings_to_display.torque_limit_beyond_endstops)
        self.spin_friction.setValue(settings_to_display.friction)
        self.spin_damping.setValue(settings_to_display.damping)
        self.spin_spring_stiffness.setValue(settings_to_display.spring_stiffness)

    def _set_default_values(self):
        """
        Sets the settings as they are described in Hardwaremanagersettings ->SensodriveSettings().
        :return:
        """
        self._display_values(SensoDriveSettings())


class JOANSensoDrive(BaseInput):
    """
    Main class for the SensoDrive input, inherits from BaseInput (as it should!)
    """

    def __init__(self, hardware_manager_action, nr_of_sensodrives, settings: SensoDriveSettings, name=''):
        """
        Initializes the class, also uses some more parameters to keep track of how many sensodrives are connected
        :param hardware_manager_action:
        :param sensodrive_tab:
        :param nr_of_sensodrives:
        :param settings:
        """
        super().__init__(hardware_manager_action, name='')
        self.module_action = hardware_manager_action
        # Create the shared variables class
        self.sensodrive_shared_values = SensoDriveSharedValues()

        self.sensodrive_shared_values.sensodrive_ID = nr_of_sensodrives

        # Torque safety variables
        self.counter = 0
        self.old_requested_torque = 0
        self.safety_checked_torque = 0
        self.t1 = 0
        self.torque_rate = 0

        self.currentInput = 'SensoDrive'
        self.settings = settings
        self.sensodrive_running = False

        self.settings_dialog = None

        # prepare for SensoDriveComm object (multiprocess)
        self.sensodrive_shared_values.torque = self.settings.torque
        self.sensodrive_shared_values.friction = self.settings.friction
        self.sensodrive_shared_values.damping = self.settings.damping
        self.sensodrive_shared_values.spring_stiffness = self.settings.spring_stiffness

        self.sensodrive_shared_values.endstops = self.settings.endstops
        self.sensodrive_shared_values.torque_limit_between_endstops = self.settings.torque_limit_between_endstops
        self.sensodrive_shared_values.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops

        self.init_event = mp.Event()
        self.close_event = mp.Event()
        self.toggle_sensodrive_motor_event = mp.Event()
        self.update_shared_values_from_settings_event = mp.Event()
        self.shutoff_event = mp.Event()

        # create SensoDriveComm object
        self.sensodrive_communication_process = SensoDriveComm(self.sensodrive_shared_values, self.init_event,
                                                               self.toggle_sensodrive_motor_event, self.close_event,
                                                               self.update_shared_values_from_settings_event,
                                                               self.shutoff_event)

        self._open_settings_dialog()

    def connect_widget(self, widget):
        self._tab_widget = widget

        #  hook up buttons
        self._tab_widget.btn_settings.clicked.connect(self._open_settings_dialog)
        self._tab_widget.btn_settings.clicked.connect(self._open_settings_from_button)
        self._tab_widget.btn_visualization.setEnabled(False)
        self._tab_widget.btn_remove_hardware.clicked.connect(self.remove_device)
        self._tab_widget.btn_on_off.clicked.connect(self.toggle_on_off)
        self._tab_widget.btn_on_off.setStyleSheet("background-color: orange")
        self._tab_widget.btn_on_off.setText('Off')
        self._tab_widget.btn_on_off.setEnabled(True)

    def update_shared_values_from_settings(self):
        """
        Updates the settings that are saved internally. NOTE: this is different than with other input modules because
        we want to be ablte to set friction, damping and spring stiffnes parameters without closing the dialog window.
        :return:
        """
        self.sensodrive_shared_values.endstops = self.settings.endstops
        self.sensodrive_shared_values.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops
        self.sensodrive_shared_values.torque_limit_between_endstops = self.settings.torque_limit_between_endstops

        self.sensodrive_shared_values.friction = self.settings.friction
        self.sensodrive_shared_values.damping = self.settings.damping
        self.sensodrive_shared_values.spring_stiffness = self.settings.spring_stiffness

        self.update_shared_values_from_settings_event.set()

    def initialize(self):
        """
        Initializes the sensodrive by sending several PCAN messages which will get the sensodrive in the appropriate
        state.
        :return:
        """

        # self.sensodrive_communication_process.initialize()

        if not self.sensodrive_communication_process.is_alive():
            self.init_event.set()
            self.sensodrive_communication_process.start()
            self.counter = 0

    def _toggle_on_off(self, connected):
        """
        Toggles the sensodrive actuator on and off by cycling through different PCANmessages
        :param connected:
        :return:
        """
        if connected == False:
            try:
                self.on_to_off()
            except:
                pass

    def _open_settings_from_button(self):
        """
        Opens and shows the settings dialog from the button on the tab
        :return:
        """
        if self.settings_dialog:
            self.settings_dialog.show()

    def _open_settings_dialog(self):
        """
        Not used for this input
        """
        self.settings_dialog = SensoDriveSettingsDialog(self.settings)

    def remove_device(self):
        """
        Removes the sensodrive from the widget and settings
        NOTE: calls 'self.remove_tab' which is a function of the BaseInput class, if you do not do this the tab will not
        actually disappear from the module.
        :return:
        """
        if self.module_action.state_machine.current_state != State.IDLE:
            self.close_event.set()
            while self.close_event.is_set():
                pass
            self.sensodrive_communication_process.terminate()

        self.module_action.remove_input_device(self.name)

    def disable_remove_button(self):
        """
        Disables the sensodrive Remove button, (useful for example when you dont want to be able to remove an input when the
        simulator is running)
        :return:
        """
        if self._tab_widget.btn_remove_hardware.isEnabled() is True:
            self._tab_widget.btn_remove_hardware.setEnabled(False)
        else:
            pass

    def enable_remove_button(self):
        """
        Enables the sensodrive remove button.
        :return:
        """
        if self._tab_widget.btn_remove_hardware.isEnabled() is False:
            self._tab_widget.btn_remove_hardware.setEnabled(True)
        else:
            pass

    def toggle_on_off(self):
        """
        If a PCAN dongle is connected and working will check what state the sensodrive is in and take the appropriate action
        (0x10 is ready, 0x14 is on and 0x18 is error)
        :return:
        """
        self.toggle_sensodrive_motor_event.set()
        # give the seperate core time to handle the signal
        if self.module_action.state_machine.current_state != State.RUNNING:
            time.sleep(0.02)

        if self.sensodrive_shared_values.sensodrive_motorstate == 0x10:
            self._tab_widget.btn_on_off.setStyleSheet("background-color: orange")
            self._tab_widget.btn_on_off.setText('Off')
        elif self.sensodrive_shared_values.sensodrive_motorstate == 0x14:
            self._tab_widget.btn_on_off.setStyleSheet("background-color: lightgreen")
            self._tab_widget.btn_on_off.setText('On')
        elif self.sensodrive_shared_values.sensodrive_motorstate == 0x18:
            self._tab_widget.btn_on_off.setStyleSheet("background-color: red")
            self._tab_widget.btn_on_off.setText('Clear Error')

    def shut_off_sensodrive(self):
        self.shutoff_event.set()

    def do(self):
        """
        Basically acts as a portal of variables to the seperate sensodrive communication core. You can send info to this
        core using the shared variables in 'SensoDriveSharedValues' Class. NOTE THAT YOU SHOULD ONLY SET VARIABLES
        ON 1 SIDE!! Do not overwrite variables, if you want to send signals for events to the seperate core please use
        the multiprocessing.Events structure.
        :return: self._data a dictionary containing :
            self._data['SteeringInput'] = self.sensodrive_shared_values.steering_angle
            self._data['BrakeInput'] = self.sensodrive_shared_values.brake
            self._data['ThrottleInput'] = self.sensodrive_shared_values.throttle
            self._data['Handbrake'] = 0
            self._data['Reverse'] = 0
            self._data['requested_torque'] = requested_torque_by_controller
            self._data['checked_torque'] = self.safety_checked_torque
            self._data['torque_rate'] = self.torque_rate
        """
        # check on the motordrive status and change button appearance
        if self.sensodrive_shared_values.sensodrive_motorstate == 0x10:
            self._tab_widget.btn_on_off.setStyleSheet("background-color: orange")
            self._tab_widget.btn_on_off.setText('Off')
        elif self.sensodrive_shared_values.sensodrive_motorstate == 0x14:
            self._tab_widget.btn_on_off.setStyleSheet("background-color: lightgreen")
            self._tab_widget.btn_on_off.setText('On')
        elif self.sensodrive_shared_values.sensodrive_motorstate == 0x18:
            self._tab_widget.btn_on_off.setStyleSheet("background-color: red")
            self._tab_widget.btn_on_off.setText('Clear Error')

        # check whether we have a sw_controller that should be updated
        self._steering_wheel_control_data = self.module_action.read_news(JOANModules.STEERING_WHEEL_CONTROL)
        self._carla_interface_data = self.module_action.read_news(JOANModules.CARLA_INTERFACE)

        try:
            requested_torque_by_controller = self._steering_wheel_control_data[
                self._carla_interface_data['ego_agents']['Vehicle 1']['vehicle_object'].selected_sw_controller][
                'sw_torque']
            desired_steering_angle = self._steering_wheel_control_data[
                self._carla_interface_data['ego_agents']['Vehicle 1']['vehicle_object'].selected_sw_controller][
                'sw_angle_desired_degrees']
        except KeyError:
            requested_torque_by_controller = 0
            desired_steering_angle = 360

        self.counter = self.counter + 1

        if self.counter == 5:
            [self.safety_checked_torque, self.torque_rate] = self.torque_check(
                requested_torque=requested_torque_by_controller, t1=self.t1, torque_limit_mnm=20000,
                torque_rate_limit_nms=150)
            self.t1 = int(round(time.time() * 1000))
            self.counter = 0

        # Write away torque parameters and torque checks
        self._data['requested_torque'] = requested_torque_by_controller
        self._data['checked_torque'] = self.safety_checked_torque
        self._data['torque_rate'] = self.torque_rate
        self._data['measured_torque'] = self.sensodrive_shared_values.measured_torque

        # Handle all shared parameters with the seperate sensodrive communication core
        # Get parameters
        self._data['SteeringInput'] = self.sensodrive_shared_values.steering_angle
        self._data['BrakeInput'] = self.sensodrive_shared_values.brake
        self._data['ThrottleInput'] = self.sensodrive_shared_values.throttle
        self._data['Handbrake'] = 0
        self._data['Reverse'] = 0

        # Set parameters
        if desired_steering_angle <= 0:
            temp = desired_steering_angle - 12
        elif desired_steering_angle > 0:
            temp = desired_steering_angle + 12
        extra_endstop = math.ceil(abs(temp))

        # print(extra_endstop)
        self.sensodrive_shared_values.torque = self.safety_checked_torque
        self.sensodrive_shared_values.friction = self.settings.friction
        self.sensodrive_shared_values.damping = self.settings.damping
        # UNCOMMENT THIS IF YOU WANT VARIABLE ENDSTOPS
        # if abs(self.sensodrive_shared_values.steering_angle) < extra_endstop - 2:
        #     self.sensodrive_shared_values.endstops = extra_endstop
        self.sensodrive_shared_values.endstops = self.settings.endstops
        self.sensodrive_shared_values.torque_limit_between_endstops = self.settings.torque_limit_between_endstops
        self.sensodrive_shared_values.torque_limit_beyond_endstops = self.settings.torque_limit_beyond_endstops
        self.sensodrive_shared_values.spring_stiffness = self.settings.spring_stiffness

        # Lastly we also need to write the spring stiffness in data for controller purposes
        self._data['spring_stiffness'] = self.sensodrive_shared_values.spring_stiffness

        return self._data

    def process(self):
        """
        TODO: hack, rename core everywhere in do?
        """
        return self.do()

    def torque_check(self, requested_torque, t1, torque_rate_limit_nms, torque_limit_mnm):
        """
        Checks the torque in 2 ways, one the max capped torque
        And the torque rate.
        If the max torque is too high it will cap, if the torque_rate is too high the motor will shut off
        """
        t2 = int(round(time.time() * 1000))

        torque_rate = (self.old_requested_torque - requested_torque) / ((t2 - t1) * 1000) * 1000  # Nm/s

        if abs(torque_rate) > torque_rate_limit_nms:
            print('TORQUE RATE TOO HIGH! TURNING OFF SENSODRIVE')
            self.shut_off_sensodrive()

        if requested_torque > torque_limit_mnm:
            checked_torque = torque_limit_mnm
        elif requested_torque < -torque_limit_mnm:
            checked_torque = -torque_limit_mnm
        else:
            checked_torque = requested_torque

        # update torque for torque rate calc
        self.old_requested_torque = requested_torque

        return [checked_torque, torque_rate]