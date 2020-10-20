import enum
import os

from .hardwaremp_settings import KeyBoardSettings


class HardwareInputTypes(enum.Enum):
    KEYBOARD = 0

    @property
    def klass(self):
        from modules.hardwaremp.hardwaremp_inputclasses.joankeyboard import JOANKeyboard

        return {HardwareInputTypes.KEYBOARD: JOANKeyboard
                }[self]

    @property
    def mpklass(self):
        from modules.hardwaremp.hardwaremp_inputclasses.joankeyboard import JOANKeyboardMP

        return {HardwareInputTypes.KEYBOARD: JOANKeyboardMP}[self]

    @property
    def shared_values(self):
        from modules.hardwaremp.hardwaremp_sharedvalues import KeyboardSharedValues

        return {HardwareInputTypes.KEYBOARD: KeyboardSharedValues()}[self]

    @property
    def settings_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hardwaremp_inputclasses/ui/")
        return {HardwareInputTypes.KEYBOARD: os.path.join(path_to_uis, "keyboard_settings_ui.ui")
                }[self]

    @property
    def hardware_tab_ui_file(self):
        path_to_uis = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hardwaremp_inputclasses/ui/")
        return {HardwareInputTypes.KEYBOARD: os.path.join(path_to_uis, "hardware_tab.ui")
                }[self]

    @property
    def settings(self):
        return {HardwareInputTypes.KEYBOARD: KeyBoardSettings()
                }[self]

    def __str__(self):
        return {HardwareInputTypes.KEYBOARD: 'Keyboard',
                }[self]
