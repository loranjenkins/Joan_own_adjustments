import os

from PyQt5 import QtWidgets, uic, QtGui, QtCore

from core.joanmoduleaction import JoanModuleAction
from core.statesenum import State
from modules.joanmodules import JOANModules


class JoanModuleDialog(QtWidgets.QDialog):
    # signal when dialog is closed
    closed = QtCore.pyqtSignal()

    def __init__(self, module: JOANModules, module_action: JoanModuleAction, use_state_machine_and_timer=True, parent=None):
        """
        Initialize
        :param module: module type
        :param module_action: module action object
        :param parent: QMainWindow parent (JOANHQWindow)
        """
        super().__init__(parent=parent)

        # reference to the action class of this module
        self.module_action = module_action

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.setWindowTitle(str(module))

        self.menu_bar = QtWidgets.QMenuBar(self)
        self.layout().setMenuBar(self.menu_bar)
        self.file_menu = self.menu_bar.addMenu('File')
        self.file_menu.addAction('Close', self.close)
        self.file_menu.addSeparator()

        # Settings
        self.settings_menu = QtWidgets.QMenu('Settings')
        self.load_settings = QtWidgets.QAction('Load Settings')
        self.load_settings.triggered.connect(self._load_settings)
        self.load_settings.setEnabled(True)
        self.settings_menu.addAction(self.load_settings)
        self.save_settings = QtWidgets.QAction('Save Settings')
        self.save_settings.triggered.connect(self._save_settings)
        self.settings_menu.addAction(self.save_settings)
        self.menu_bar.addMenu(self.settings_menu)

        if use_state_machine_and_timer:
            self.module_action.state_machine.add_state_change_listener(self.handle_state_change)

            # setup state widget
            self.state_widget = uic.loadUi(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../resources/state_widget.ui"))
            self.layout().addWidget(self.state_widget)
            self.state_widget.btn_start.clicked.connect(self._button_start_clicked)
            self.state_widget.btn_stop.clicked.connect(self._button_stop_clicked)
            self.state_widget.btn_initialize.clicked.connect(self._button_initialize_clicked)
            self.state_widget.btn_start.setEnabled(False)
            self.state_widget.btn_stop.setEnabled(False)
            self.state_widget.input_tick_millis.setValidator(QtGui.QIntValidator(0, 10000, parent=self))
            self.state_widget.input_tick_millis.setPlaceholderText(str(self.module_action.tick_interval_ms))
            self.state_widget.input_tick_millis.textChanged.connect(self._set_tick_interval_ms)

            # setup button enables
            self.state_widget.btn_start.setEnabled(False)

        # setup module-specific widget
        self.module_widget = uic.loadUi(module.ui_file)
        self.layout().addWidget(self.module_widget)

        self.module_action.register_module_dialog(module_dialog=self)

        # load default settings
        self.module_action.load_default_settings()

        # reflect latest state
        self.handle_state_change()

    def _button_start_clicked(self):
        self.module_action.start()

    def _button_stop_clicked(self):
        self.module_action.stop()

    def _button_initialize_clicked(self):
        self.module_action.initialize()

    def _load_settings(self):
        """
        Loads settings from json file.
        :return:
        """
        settings_file_to_load, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'load settings',
                                                                         os.path.join(self.module_action.module_path,
                                                                                      'action'),
                                                                         filter='*.json')
        if settings_file_to_load:
            self.module_action.load_settings_from_file(settings_file_to_load)

    def _save_settings(self):
        """
        Saves settings to json file
        :return:
        """
        file_to_save_in, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'save settings',
                                                                   os.path.join(self.module_action.module_path, 'action', 'default_settings.json'),
                                                                   filter='*.json')
        if file_to_save_in:
            self.module_action.save_settings_to_file(file_to_save_in)

    def _set_tick_interval_ms(self, text):
        self.module_action.tick_interval_ms = int(text)

    def handle_state_change(self):
        """
        handle state change
        This function is connected to the module's state machine
        """

        if hasattr(self, 'state_widget'):
            current_state = self.module_action.state_machine.current_state
            message = self.module_action.state_machine.state_message

            # update the state label
            self.state_widget.lbl_module_state.setText(str(current_state))
            self.state_widget.lbl_state_message.setText(message)

            if current_state is State.RUNNING:
                self.state_widget.lbl_module_state.setStyleSheet("background: green;")
            elif current_state is State.INITIALIZED:
                self.state_widget.lbl_module_state.setStyleSheet("background: orange;")
            elif current_state is State.READY:
                self.state_widget.lbl_module_state.setStyleSheet("background: yellow;")
            elif current_state is State.ERROR:  # an Error state
                self.state_widget.lbl_module_state.setStyleSheet("background: red;")

            if current_state == State.READY:
                self.state_widget.btn_start.setEnabled(True)
                self.state_widget.input_tick_millis.setEnabled(True)
                self.state_widget.input_tick_millis.clear()
                self.state_widget.input_tick_millis.setPlaceholderText(str(self.module_action.tick_interval_ms))
            else:
                self.state_widget.btn_start.setEnabled(False)

            if current_state == State.INITIALIZED or current_state == State.ERROR:
                self.state_widget.btn_initialize.setEnabled(True)
            else:
                self.state_widget.btn_initialize.setEnabled(False)

            if current_state == State.RUNNING:
                self.state_widget.btn_stop.setEnabled(True)
                self.state_widget.input_tick_millis.setEnabled(False)
                self.state_widget.input_tick_millis.clear()
                self.state_widget.input_tick_millis.clearFocus()
                self.state_widget.input_tick_millis.setPlaceholderText(str(self.module_action.tick_interval_ms))
            else:
                self.state_widget.btn_stop.setEnabled(False)

            if current_state == State.INITIALIZED:
                self.state_widget.input_tick_millis.setEnabled(True)
                self.state_widget.input_tick_millis.clear()
                self.state_widget.input_tick_millis.setPlaceholderText(str(self.module_action.tick_interval_ms))

            # If module is running change button color
            if current_state == State.RUNNING:
                self.state_widget.btn_start.setStyleSheet("background-color: lightgreen")
                self.state_widget.btn_start.setText('Running')
                # self.state_widget.btn_start.setEnabled(False)
            elif current_state == State.ERROR:
                self.state_widget.btn_initialize.setStyleSheet("background-color: orange")
                self.state_widget.btn_initialize.setText('Clear Error')
            else:
                self.state_widget.btn_start.setStyleSheet("background-color: none")
                self.state_widget.btn_initialize.setStyleSheet("background-color: none")
                self.state_widget.btn_initialize.setText('Initialize')
                self.state_widget.btn_start.setText('Start')
                # self.state_widget.btn_start.setEnabled(True)

    def toggle_show_close(self):
        """
        toggle visibility of this dialog
        """
        if not self.isVisible():
            self.show()
        else:
            self.close()

    def closeEvent(self, event):
        """
        close event
        """
        self.closed.emit()
        super().closeEvent(event)