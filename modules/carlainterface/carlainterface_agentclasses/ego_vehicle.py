from PyQt5 import uic, QtWidgets
import os
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
import random, os, sys, glob
import math
#TODO Maybe check this again, however it should not even start when it cant find the library the first time
import time
sys.path.append(glob.glob('carla_pythonapi/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
import carla

class EgoVehicleSettingsDialog(QtWidgets.QDialog):
    def __init__(self, ego_vehicle_settings, parent = None):
        super().__init__(parent)
        self.settings = ego_vehicle_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/ego_vehicle_settings_ui.ui"), self)

        self.button_box_egovehicle_settings.button(self.button_box_egovehicle_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)
        self.display_values()

    def update_parameters(self):
        self.settings.velocity = self.spin_velocity.value()
        self.settings.selected_input = self.combo_input.currentText()
        self.settings.selected_controller = self.combo_sw_controller.currentText()
        self.settings.selected_car = self.combo_car_type.currentText()
        self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()
        self.settings.set_velocity = self.check_box_set_vel.isChecked()
        self.display_values()

    def accept(self):
        self.settings.velocity = self.spin_velocity.value()
        self.settings.selected_input = self.combo_input.currentText()
        self.settings.selected_controller = self.combo_sw_controller.currentText()
        self.settings.selected_car = self.combo_car_type.currentText()
        self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()
        self.settings.set_velocity = self.check_box_set_vel.isChecked()
        super().accept()

    def display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.settings

        idx_controller = self.combo_sw_controller.findText(settings_to_display.selected_controller)
        self.combo_sw_controller.setCurrentIndex(idx_controller)

        idx_input = self.combo_input.findText(settings_to_display.selected_input)
        self.combo_input.setCurrentIndex(idx_input)

        idx_car = self.combo_car_type.findText(settings_to_display.selected_car)
        self.combo_car_type.setCurrentIndex(idx_car)

        self.combo_spawnpoints.setCurrentText(settings_to_display.selected_spawnpoint)

        self.spin_velocity.setValue(settings_to_display.velocity)
        self.check_box_set_vel.setChecked(settings_to_display.set_velocity)

    def _set_default_values(self):
        self.display_values(AgentTypes.EGO_VEHICLE.settings())

class EgoVehicleMP:
    def __init__(self, carla_mp, settings, shared_variables,):
        self.settings = settings
        self.shared_variables = shared_variables
        self.carlainterface_mp = carla_mp

        self._control = carla.VehicleControl()
        self._BP = random.choice(self.carlainterface_mp.vehicle_blueprint_library.filter("vehicle." + self.settings.selected_car))
        self._control = carla.VehicleControl()
        torque_curve = []
        gears = []

        torque_curve.append(carla.Vector2D(x=0, y=600))
        torque_curve.append(carla.Vector2D(x=14000, y=600))
        gears.append(carla.GearPhysicsControl(ratio=7.73, down_ratio=0.5, up_ratio=1))

        self.spawned_vehicle = self.carlainterface_mp.world.spawn_actor(self._BP, self.carlainterface_mp.spawn_point_objects[
            self.carlainterface_mp.spawn_points.index(self.settings.selected_spawnpoint)])
        physics = self.spawned_vehicle.get_physics_control()
        physics.torque_curve = torque_curve
        physics.max_rpm = 14000
        physics.moi = 1.5
        physics.final_ratio = 1
        physics.clutch_strength = 1000  # very big no clutch
        physics.final_ratio = 1  # ratio from transmission to wheels
        physics.forward_gears = gears
        physics.mass = 2316
        physics.drag_coefficient = 0.24
        physics.gear_switch_time = 0
        self.spawned_vehicle.apply_physics_control(physics)


    def do(self):
        # self._control.steer = self.carlainterface_mp.shared_variables_hardware
        if 'Keyboard' in self.settings.selected_input:
            identifier = int(self.settings.selected_input.replace('Keyboard ', ''))
            self._control.steer = self.carlainterface_mp.shared_variables_hardware.keyboards[identifier].steering_angle /math.radians(450)
            self._control.reverse = self.carlainterface_mp.shared_variables_hardware.keyboards[identifier].reverse
            self._control.hand_brake = self.carlainterface_mp.shared_variables_hardware.keyboards[identifier].handbrake
            self._control.brake = self.carlainterface_mp.shared_variables_hardware.keyboards[identifier].brake
            self._control.throttle = self.carlainterface_mp.shared_variables_hardware.keyboards[identifier].throttle
            print(self._control.steer)
        if 'Joystick' in self.settings.selected_input:
            identifier = int(self.settings.selected_input.replace('Joystick ', ''))
            self._control.steer = self.carlainterface_mp.shared_variables_hardware.joysticks[identifier].steering_angle /math.radians(450)
            self._control.reverse = self.carlainterface_mp.shared_variables_hardware.joysticks[identifier].reverse
            self._control.hand_brake = self.carlainterface_mp.shared_variables_hardware.joysticks[identifier].handbrake
            self._control.brake = self.carlainterface_mp.shared_variables_hardware.joysticks[identifier].brake
            self._control.throttle = self.carlainterface_mp.shared_variables_hardware.joysticks[identifier].throttle
        if 'SensoDrive' in self.settings.selected_input:
            identifier = int(self.settings.selected_input.replace('SensoDrive ', ''))
            self._control.steer = self.carlainterface_mp.shared_variables_hardware.sensodrives[identifier].steering_angle /math.radians(450)
            self._control.reverse = self.carlainterface_mp.shared_variables_hardware.sensodrives[identifier].reverse
            self._control.hand_brake = self.carlainterface_mp.shared_variables_hardware.sensodrives[identifier].handbrake
            self._control.brake = self.carlainterface_mp.shared_variables_hardware.sensodrives[identifier].brake
            self._control.throttle = self.carlainterface_mp.shared_variables_hardware.sensodrives[identifier].throttle
            print(self._control.steer)


        self.spawned_vehicle.apply_control(self._control)



    def destroy(self):
        self.spawned_vehicle.destroy()