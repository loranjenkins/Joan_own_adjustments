import os

from PyQt5 import QtWidgets, uic


class SettingsOverviewDialog(QtWidgets.QDialog):
    def __init__(self, all_settings, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "settingsoverviewdialog.ui"), self)

        for module_key, settings_object in all_settings.items():
            try:
                self._create_tree_item(self.treeWidget, module_key, settings_object.as_dict())
            except AttributeError:
                # This means the settings object is a dict, which is old style  TODO remove this try/except when fully converted to new style
                self._create_tree_item(self.treeWidget, module_key, settings_object)

        self.show()

    @staticmethod
    def _create_tree_item(parent, key, value):
        if isinstance(value, dict):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, str(key))

            for inner_key, inner_value in value.items():
                SettingsOverviewDialog._create_tree_item(item, inner_key, inner_value)
            return item
        if isinstance(value, list):
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, str(key))

            for index, inner_value in enumerate(value):
                SettingsOverviewDialog._create_tree_item(item, str(index), inner_value)
            return item
        else:
            item = QtWidgets.QTreeWidgetItem(parent)
            item.setData(0, 0, str(key))
            item.setData(1, 0, str(value))
            return item
