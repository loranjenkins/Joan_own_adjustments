import os
import time

from PyQt5 import uic, QtWidgets

from modules.hardwaremanager.action.hardwaremanagersettings import SensoDriveSettings
from modules.hardwaremanager.action.inputclasses.PCANBasic import *
from modules.hardwaremanager.action.inputclasses.baseinput import BaseInput
from modules.joanmodules import JOANModules

INITIALIZATION_MESSAGE_ID = 0x200
INITIALIZATION_MESSAGE_LENGTH = 8

STEERINGWHEEL_MESSAGE_ID = 0x201
STEERINGWHEEL_MESSAGE_LENGTH = 8

PEDAL_MESSAGE_ID = 0x20C
PEDAL_MESSAGE_LENGTH = 2


class SensoDriveSettingsDialog(QtWidgets.QDialog):
    def __init__(self, sensodrive_settings, parent=None):
        super().__init__(parent)
        self.sensodrive_settings = sensodrive_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/sensodrive_settings_ui.ui"), self)

        self.button_box_settings.button(self.button_box_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)
        self._display_values()
        # self.show()

    def accept(self):
        self.sensodrive_settings.endstops = self.spin_endstop_position.value()
        self.sensodrive_settings.torque_limit_between_endstops = self.spin_torque_limit_between_endstops.value()
        self.sensodrive_settings.torque_limit_beyond_endstops = self.spin_torque_limit_beyond_endstops.value()
        self.sensodrive_settings.friction = self.spin_friction.value()
        self.sensodrive_settings.damping = self.spin_damping.value()
        self.sensodrive_settings.spring_stiffness = self.spin_spring_stiffness.value()

        super().accept()

    def _display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.sensodrive_settings

        self.spin_endstop_position.setValue(settings_to_display.endstops)
        self.spin_torque_limit_between_endstops.setValue(settings_to_display.torque_limit_between_endstops)
        self.spin_torque_limit_beyond_endstops.setValue(settings_to_display.torque_limit_beyond_endstops)
        self.spin_friction.setValue(settings_to_display.friction)
        self.spin_damping.setValue(settings_to_display.damping)
        self.spin_spring_stiffness.setValue(settings_to_display.spring_stiffness)

    def _set_default_values(self):
        self._display_values(SensoDriveSettings())


class JOAN_SensoDrive(BaseInput):
    def __init__(self, hardware_manager_action, sensodrive_tab, nr_of_sensodrives, settings: SensoDriveSettings):
        super().__init__(hardware_manager_action)

        self.currentInput = 'SensoDrive'
        self._sensodrive_tab = sensodrive_tab
        self.settings = settings
        self.sensodrive_running = False

        # Create PCAN object
        self.PCAN_object = PCANBasic()
        self.pcan_initialization_result = None
        self.steering_wheel_parameters = {}
        self._current_state_hex = 0x00
        self._error_state = [0x00, 0x00]
        self._pcan_error = False

        if nr_of_sensodrives == 0:
            self._pcan_channel = PCAN_USBBUS1
        elif nr_of_sensodrives == 1:
            self._pcan_channel = PCAN_USBBUS2

        #  hook up buttons
        self._sensodrive_tab.btn_settings.clicked.connect(self._open_settings_dialog)
        self._sensodrive_tab.btn_settings.clicked.connect(self._open_settings_from_button)
        self._sensodrive_tab.btn_visualization.setEnabled(False)
        self._sensodrive_tab.btn_remove_hardware.clicked.connect(self.remove_func)
        self._sensodrive_tab.btn_on_off.clicked.connect(self.on_off)
        self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: orange")
        self._sensodrive_tab.btn_on_off.setText('Off')
        self._sensodrive_tab.btn_on_off.setEnabled(True)

        # Initialize message structures
        self.steering_wheel_message = TPCANMsg()
        self.state_message = TPCANMsg()
        self.pedal_message = TPCANMsg()
        self.sensodrive_initialization_message = TPCANMsg()
        self.state_change_message = TPCANMsg()

        self.state_change_message.ID = INITIALIZATION_MESSAGE_ID
        self.state_change_message.LEN = INITIALIZATION_MESSAGE_LENGTH
        self.state_change_message.TYPE = PCAN_MESSAGE_STANDARD
        # mode of operation
        self.state_change_message.DATA[0] = 0x11
        self.state_change_message.DATA[1] = 0x00
        # Endstop position
        self.state_change_message.DATA[2] = 0xB4
        self.state_change_message.DATA[3] = 0x00
        # Torque beyond endstops:
        self.state_change_message.DATA[6] = 0x14
        self.state_change_message.DATA[7] = 0x14

        self.settings_dialog = SensoDriveSettingsDialog(self.settings)
        self.settings_dialog.accepted.connect(self.update_settings)

        self.steering_wheel_parameters['torque'] = 0  # (You dont want to start to turn the wheel at startup)
        self.steering_wheel_parameters['friction'] = self.settings.friction
        self.steering_wheel_parameters['damping'] = self.settings.damping
        self.steering_wheel_parameters['spring_stiffness'] = self.settings.spring_stiffness




    def update_settings(self):
        self.endstops_bytes = int.to_bytes(self.settings.endstops, 2, byteorder='little', signed=True)
        self.torque_limit_between_endstops_bytes = int.to_bytes(self.settings.torque_limit_between_endstops, 1,
                                                                byteorder='little', signed=False)
        self.torque_limit_beyond_endstops_bytes = int.to_bytes(self.settings.torque_limit_beyond_endstops, 1,
                                                               byteorder='little', signed=False)

        self.steering_wheel_parameters['friction'] = self.settings.friction
        self.steering_wheel_parameters['damping'] = self.settings.damping
        self.steering_wheel_parameters['spring_stiffness'] = self.settings.spring_stiffness

        # mode of operation
        self.sensodrive_initialization_message.DATA[0] = 0x10
        # reserved
        self.sensodrive_initialization_message.DATA[1] = 0
        # Endstop position
        self.sensodrive_initialization_message.DATA[2] = self.endstops_bytes[0]
        self.sensodrive_initialization_message.DATA[3] = self.endstops_bytes[1]
        # reserved
        self.sensodrive_initialization_message.DATA[4] = 0
        self.sensodrive_initialization_message.DATA[5] = 0
        # Torque between endstops:
        self.sensodrive_initialization_message.DATA[6] = self.torque_limit_between_endstops_bytes[0]
        # Torque beyond endstops:
        self.sensodrive_initialization_message.DATA[7] = self.torque_limit_beyond_endstops_bytes[0]

        try:
            self.PCAN_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
            time.sleep(0.02)
            # read the response just to clear out the buffer (we will not do anything with the data)
            self.response = self.PCAN_object.Read(self._pcan_channel)
        except Exception as inst:
            print(inst, 'probably not initialized yet')

    def initialize(self):
        # Convert integers to bytes:
        self.endstops_bytes = int.to_bytes(self.settings.endstops, 2, byteorder='little', signed=True)
        self.torque_limit_between_endstops_bytes = int.to_bytes(self.settings.torque_limit_between_endstops, 1,
                                                                byteorder='little', signed=False)
        self.torque_limit_beyond_endstops_bytes = int.to_bytes(self.settings.torque_limit_beyond_endstops, 1,
                                                               byteorder='little', signed=False)

        if self.pcan_initialization_result is None:
            self.pcan_initialization_result = self.PCAN_object.Initialize(
                self._pcan_channel, PCAN_BAUD_1M)

        # We need to have our init message here as well
        self.sensodrive_initialization_message.ID = INITIALIZATION_MESSAGE_ID
        self.sensodrive_initialization_message.LEN = INITIALIZATION_MESSAGE_LENGTH
        self.sensodrive_initialization_message.TYPE = PCAN_MESSAGE_STANDARD
        # mode of operation
        self.sensodrive_initialization_message.DATA[0] = 0x11
        # reserved
        self.sensodrive_initialization_message.DATA[1] = 0
        # Endstop position
        self.sensodrive_initialization_message.DATA[2] = self.endstops_bytes[0]
        self.sensodrive_initialization_message.DATA[3] = self.endstops_bytes[1]
        # reserved
        self.sensodrive_initialization_message.DATA[4] = 0
        self.sensodrive_initialization_message.DATA[5] = 0
        # Torque between endstops:
        self.sensodrive_initialization_message.DATA[6] = self.torque_limit_between_endstops_bytes[0]
        # Torque beyond endstops:
        self.sensodrive_initialization_message.DATA[7] = self.torque_limit_beyond_endstops_bytes[0]

        self.PCAN_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
        time.sleep(0.02)
        self.response = self.PCAN_object.Read(self._pcan_channel)

        self.state_message = self.sensodrive_initialization_message
        self.state_message.DATA[0] = 0x11

        # Set the data structure for the steeringwheel message with the just applied values
        self.steering_wheel_parameters['torque'] = 0  # (You dont want to start to turn the wheel at startup)
        self.steering_wheel_parameters['friction'] = self.settings.friction
        self.steering_wheel_parameters['damping'] = self.settings.damping
        self.steering_wheel_parameters['spring_stiffness'] = self.settings.spring_stiffness
        print('initializing SensoDrive')

        self.PCAN_object.Write(self._pcan_channel, self.sensodrive_initialization_message)
        time.sleep(0.02)
        response = self.PCAN_object.Read(self._pcan_channel)
        #
        self.state_message = self.sensodrive_initialization_message
        self.state_message.DATA[0] = 0x11

        if self.pcan_initialization_result != PCAN_ERROR_OK:
            answer = QtWidgets.QMessageBox.warning(self, 'Warning',
                                                   (self.PCAN_object.GetErrorText(
                                                       self.pcan_initialization_result)[
                                                        1].decode("utf-8") \
                                                    + ". Do you want to continue?"),
                                                   buttons=QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            if answer == QtWidgets.QMessageBox.Cancel:
                return
            if answer == QtWidgets.QMessageBox.Ok:
                self._pcan_error = True
        else:
            self._pcan_error = False

    def _toggle_on_off(self, connected):
        # self._sensodrive_tab.btn_on_off.setEnabled(connected)
        if connected == False:
            try:
                self.on_to_off()
            except:
                pass

    def _open_settings_from_button(self):
        if self.settings_dialog:
            self.settings_dialog.show()

    def _open_settings_dialog(self):
        pass

    def remove_func(self):
        try:
            self.PCAN_object.Uninitialize(self._pcan_channel)
        except:
            pass
        self.remove_tab(self._sensodrive_tab)

    def disable_remove_button(self):
        if self._sensodrive_tab.btn_remove_hardware.isEnabled() is True:
            self._sensodrive_tab.btn_remove_hardware.setEnabled(False)
        else:
            pass

    def enable_remove_button(self):
        if self._sensodrive_tab.btn_remove_hardware.isEnabled() is False:
            self._sensodrive_tab.btn_remove_hardware.setEnabled(True)
        else:
            pass

    def on_off(self):
        if self._pcan_error:
            answer = QtWidgets.QMessageBox.warning(self._sensodrive_tab, 'Warning',
                                                   "The PCAN connection was not initialized properly, please reopen settings menu to try and reinitialize.",
                                                   buttons=QtWidgets.QMessageBox.Ok)
            if answer == QtWidgets.QMessageBox.Ok:
                self._pcan_error = True
        else:
            if (self._current_state_hex == 0x10):
                self.off_to_on(self.sensodrive_initialization_message)

            elif (self._current_state_hex == 0x14):
                self.on_to_off(self.sensodrive_initialization_message)

            elif (self._current_state_hex == 0x18):
                self.clear_error(self.sensodrive_initialization_message)

    def off_to_on(self, message):
        print('off to on')
        message.DATA[0] = 0x10
        self.PCAN_object.Write(self._pcan_channel, message)
        time.sleep(0.02)

        message.DATA[0] = 0x12
        self.PCAN_object.Write(self._pcan_channel, message)
        time.sleep(0.02)

        message.DATA[0] = 0x14
        self.PCAN_object.Write(self._pcan_channel, message)
        self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: lightgreen")
        self._sensodrive_tab.btn_on_off.setText('On')

    def on_to_off(self, message):
        print('on to off')
        message.DATA[0] = 0x12
        self.PCAN_object.Write(self._pcan_channel, message)
        time.sleep(0.02)
        message.DATA[0] = 0x10
        self.PCAN_object.Write(self._pcan_channel, message)
        time.sleep(0.02)
        self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: orange")
        self._sensodrive_tab.btn_on_off.setText('Off')

    def clear_error(self, message):
        print('clear error')
        message.DATA[0] = 0x1F
        self.PCAN_object.Write(self._pcan_channel, message)
        time.sleep(0.02)
        self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: orange")
        self._sensodrive_tab.btn_on_off.setText('Off')

    def process(self):
        # Reverse
        self._data['Reverse'] = 0
        # Handbrake
        self._data['Handbrake'] = 0

        # check whether we have a sw_controller that should be updated
        self._steering_wheel_control_data = self._action.read_news(JOANModules.STEERING_WHEEL_CONTROL)
        self._carla_interface_data = self._action.read_news(JOANModules.AGENT_MANAGER)
        try:
            self.steering_wheel_parameters['torque'] = self._steering_wheel_control_data[self._carla_interface_data['agents']['Car 1']['vehicle_object'].selected_sw_controller][
                'sw_torque']
        except:
            self.steering_wheel_parameters['torque'] = 0

        # request and set steering wheel data
        self.write_message_steering_wheel(self.PCAN_object, self.steering_wheel_message, self.steering_wheel_parameters)
        received = self.PCAN_object.Read(self._pcan_channel)

        # request state data
        self.PCAN_object.Write(self._pcan_channel, self.state_message)
        received2 = self.PCAN_object.Read(self._pcan_channel)

        # request pedal data
        self.write_message_pedals(self.PCAN_object, self.pedal_message)
        received3 = self.PCAN_object.Read(self._pcan_channel)

        if (received[0] or received2[0] or received3[0] == PCAN_ERROR_OK):
            if (received[1].ID == 0x211):
                Increments = int.from_bytes(received[1].DATA[0:4], byteorder='little', signed=True)
                Angle = round(Increments * 0.009, 4)
                # Steering:
                self._data['SteeringInput'] = Angle
            elif (received[1].ID == 0x210):
                self._current_state_hex = received[1].DATA[0]
                self._error_state[0] = received[1].DATA[2]
                self._error_state[1] = received[1].DATA[3]
            elif (received[1].ID == 0x21C):
                self._data['ThrottleInput'] = (int.from_bytes(received[1].DATA[2:4],
                                                              byteorder='little') - 1100) / 2460 * 100
                self._data['BrakeInput'] = (int.from_bytes(received[1].DATA[4:6], byteorder='little') - 1) / 500 * 100

            if (received2[1].ID == 0x211):
                Increments = int.from_bytes(received2[1].DATA[0:4], byteorder='little', signed=True)
                Angle = round(Increments * 0.009, 4)
                # Steering:
                self._data['SteeringInput'] = Angle
            elif (received2[1].ID == 0x210):
                self._current_state_hex = received2[1].DATA[0]
                self._error_state[0] = received2[1].DATA[2]
                self._error_state[1] = received2[1].DATA[3]
            elif (received2[1].ID == 0x21C):
                self._data['ThrottleInput'] = (int.from_bytes(received2[1].DATA[2:4],
                                                              byteorder='little') - 1100) / 2460 * 100
                self._data['BrakeInput'] = (int.from_bytes(received2[1].DATA[4:6], byteorder='little') - 1) / 500 * 100
                # self._data['Clut'] = int.from_bytes(result[1].DATA[6:], byteorder = 'little')

            if (received3[1].ID == 0x211):
                Increments = int.from_bytes(received3[1].DATA[0:4], byteorder='little', signed=True)
                Angle = round(Increments * 0.009, 4)
                # Steering:
                self._data['SteeringInput'] = Angle
            elif (received3[1].ID == 0x210):
                self._current_state_hex = received3[1].DATA[0]
                self._error_state[0] = received3[1].DATA[2]
                self._error_state[1] = received3[1].DATA[3]
            elif (received3[1].ID == 0x21C):
                self._data['ThrottleInput'] = (int.from_bytes(received3[1].DATA[2:4],
                                                              byteorder='little') - 1100) / 2460 * 100
                self._data['BrakeInput'] = (int.from_bytes(received3[1].DATA[4:6], byteorder='little') - 1) / 500 * 100

        if (self._current_state_hex == 0x18):
            self._sensodrive_tab.btn_on_off.setStyleSheet("background-color: red")
            self._sensodrive_tab.btn_on_off.setText('Clear Error')

        # writing the spring stiffness in news because we need this parameter in the 'steeringwheelcontrol' module :)
        self._data['spring_stiffness'] = self.steering_wheel_parameters['spring_stiffness']

        return self._data

    def write_message_pedals(self, pcan_object, pcanmessage):
        pcanmessage.ID = 0x20C
        pcanmessage.LEN = 1
        pcanmessage.MSGTYPE = PCAN_MESSAGE_STANDARD

        pcanmessage.DATA[0] = 0x1

        if not self._pcan_error:
            self.PCAN_object.Write(self._pcan_channel, pcanmessage)

    def write_message_steering_wheel(self, pcan_object, pcanmessage, data):
        torque_bytes = int.to_bytes(data['torque'], 2, byteorder='little', signed=True)
        friction_bytes = int.to_bytes(data['friction'], 2, byteorder='little', signed=True)
        damping_bytes = int.to_bytes(data['damping'], 2, byteorder='little', signed=True)
        spring_stiffness_bytes = int.to_bytes(data['spring_stiffness'], 2, byteorder='little', signed=True)

        pcanmessage.ID = STEERINGWHEEL_MESSAGE_ID
        pcanmessage.LEN = STEERINGWHEEL_MESSAGE_LENGTH
        pcanmessage.TYPE = PCAN_MESSAGE_STANDARD
        pcanmessage.DATA[0] = torque_bytes[0]
        pcanmessage.DATA[1] = torque_bytes[1]
        pcanmessage.DATA[2] = friction_bytes[0]
        pcanmessage.DATA[3] = friction_bytes[1]
        pcanmessage.DATA[4] = damping_bytes[0]
        pcanmessage.DATA[5] = damping_bytes[1]
        pcanmessage.DATA[6] = spring_stiffness_bytes[0]
        pcanmessage.DATA[7] = spring_stiffness_bytes[1]

        if not self._pcan_error:
            pcan_object.Write(self._pcan_channel, pcanmessage)
