from core.module_manager import ModuleManager
from modules.joanmodules import JOANModules
from modules.hardwaremp.hardwaremp_inputtypes import HardwareInputTypes
from modules.hardwaremp.hardwaremp_sharedvalues import KeyboardSharedValues, JoystickSharedValues, SensoDriveSharedValues
from PyQt5 import uic


class HardwareMPManager(ModuleManager):
    """Example JOAN module"""

    def __init__(self, time_step_in_ms=10, parent=None):
        super().__init__(module=JOANModules.HARDWARE_MP, time_step_in_ms=time_step_in_ms, parent=parent)
        self._hardware_inputs = {}
        self.hardware_input_type = None
        self.hardware_input_settings = None

        self._hardware_input_settings_dict = {}
        self._hardware_input_settingdialogs_dict = {}

    def initialize(self):
        super().initialize()
        for idx, _ in enumerate(self.module_settings.keyboards):
            self.shared_variables.keyboards.update({'Keyboard ' + str(idx): KeyboardSharedValues()})
        for idx, _ in enumerate(self.module_settings.joysticks):
            self.shared_variables.joysticks.update({'Joystick ' + str(idx): JoystickSharedValues()})
        for idx, _ in enumerate(self.module_settings.sensodrives):
            self.shared_variables.sensodrives.update({'SensoDrive ' + str(idx): SensoDriveSharedValues()})

    def add_hardware_input(self, hardware_input_type, hardware_input_name, hardware_input_settings=None):
        " Here we just add the settings and settings dialog functionality"
        if not hardware_input_settings:
            hardware_input_settings = hardware_input_type.settings
            if hardware_input_type == HardwareInputTypes.KEYBOARD:
                self.module_settings.keyboards.append(hardware_input_settings)
            if hardware_input_type == HardwareInputTypes.JOYSTICK:
                self.module_settings.joysticks.append(hardware_input_settings)
            if hardware_input_type == HardwareInputTypes.SENSODRIVE:
                self.module_settings.sensodrives.append(hardware_input_settings)

        self._hardware_input_settings_dict[hardware_input_name] = hardware_input_settings
        self._hardware_input_settingdialogs_dict[hardware_input_name] = hardware_input_type.klass_dialog(hardware_input_settings)

    def _open_settings_dialog(self, hardware_input_name):
        self._hardware_input_settingdialogs_dict[hardware_input_name].show()


    def _remove_hardware_input_device(self, hardware_input_name):
        # Remove settings if they are available
        self.module_settings.remove_hardware_input_device(self._hardware_input_settings_dict[hardware_input_name])

        # Remove settings dialog
        self._hardware_input_settingdialogs_dict[hardware_input_name].setParent(None)
        del self._hardware_input_settingdialogs_dict[hardware_input_name]

        self.module_dialog.repaint()
