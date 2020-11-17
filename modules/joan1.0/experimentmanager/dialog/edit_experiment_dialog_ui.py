# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_experiment_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExperimentManagerWidget(object):
    def setupUi(self, ExperimentManagerWidget):
        ExperimentManagerWidget.setObjectName("ExperimentManagerWidget")
        ExperimentManagerWidget.resize(640, 640)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ExperimentManagerWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(ExperimentManagerWidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 1, 0, 1, 1)
        self.baseSettingsTreeWidget = QtWidgets.QTreeWidget(self.groupBox)
        self.baseSettingsTreeWidget.setObjectName("baseSettingsTreeWidget")
        self.gridLayout_2.addWidget(self.baseSettingsTreeWidget, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 1, 1, 1)
        self.experimentNameLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.experimentNameLineEdit.setReadOnly(True)
        self.experimentNameLineEdit.setObjectName("experimentNameLineEdit")
        self.gridLayout_2.addWidget(self.experimentNameLineEdit, 0, 1, 1, 1)
        self.modulesIncludedListWidget = QtWidgets.QListWidget(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modulesIncludedListWidget.sizePolicy().hasHeightForWidth())
        self.modulesIncludedListWidget.setSizePolicy(sizePolicy)
        self.modulesIncludedListWidget.setMinimumSize(QtCore.QSize(0, 100))
        self.modulesIncludedListWidget.setObjectName("modulesIncludedListWidget")
        self.gridLayout_2.addWidget(self.modulesIncludedListWidget, 2, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.horizontalGroupBox = QtWidgets.QGroupBox(ExperimentManagerWidget)
        self.horizontalGroupBox.setObjectName("horizontalGroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.horizontalGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.addConditionPushButton = QtWidgets.QPushButton(self.horizontalGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addConditionPushButton.sizePolicy().hasHeightForWidth())
        self.addConditionPushButton.setSizePolicy(sizePolicy)
        self.addConditionPushButton.setMinimumSize(QtCore.QSize(10, 0))
        self.addConditionPushButton.setObjectName("addConditionPushButton")
        self.verticalLayout.addWidget(self.addConditionPushButton)
        self.removeConditionPushButton = QtWidgets.QPushButton(self.horizontalGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.removeConditionPushButton.sizePolicy().hasHeightForWidth())
        self.removeConditionPushButton.setSizePolicy(sizePolicy)
        self.removeConditionPushButton.setMinimumSize(QtCore.QSize(10, 0))
        self.removeConditionPushButton.setObjectName("removeConditionPushButton")
        self.verticalLayout.addWidget(self.removeConditionPushButton)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.verticalLayout, 3, 1, 1, 1)
        self.availableConditionsListWidget = QtWidgets.QListWidget(self.horizontalGroupBox)
        self.availableConditionsListWidget.setObjectName("availableConditionsListWidget")
        self.gridLayout.addWidget(self.availableConditionsListWidget, 3, 0, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.addTransitionPushButton = QtWidgets.QPushButton(self.horizontalGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addTransitionPushButton.sizePolicy().hasHeightForWidth())
        self.addTransitionPushButton.setSizePolicy(sizePolicy)
        self.addTransitionPushButton.setMinimumSize(QtCore.QSize(10, 0))
        self.addTransitionPushButton.setObjectName("addTransitionPushButton")
        self.verticalLayout_3.addWidget(self.addTransitionPushButton)
        self.removeTransitionPushButton = QtWidgets.QPushButton(self.horizontalGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.removeTransitionPushButton.sizePolicy().hasHeightForWidth())
        self.removeTransitionPushButton.setSizePolicy(sizePolicy)
        self.removeTransitionPushButton.setMinimumSize(QtCore.QSize(10, 0))
        self.removeTransitionPushButton.setObjectName("removeTransitionPushButton")
        self.verticalLayout_3.addWidget(self.removeTransitionPushButton)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.gridLayout.addLayout(self.verticalLayout_3, 3, 5, 1, 1)
        self.currentConditionsListWidget = QtWidgets.QListWidget(self.horizontalGroupBox)
        self.currentConditionsListWidget.setObjectName("currentConditionsListWidget")
        self.gridLayout.addWidget(self.currentConditionsListWidget, 3, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.horizontalGroupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.conditionUpPushButton = QtWidgets.QPushButton(self.horizontalGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.conditionUpPushButton.sizePolicy().hasHeightForWidth())
        self.conditionUpPushButton.setSizePolicy(sizePolicy)
        self.conditionUpPushButton.setMinimumSize(QtCore.QSize(10, 23))
        self.conditionUpPushButton.setObjectName("conditionUpPushButton")
        self.horizontalLayout_3.addWidget(self.conditionUpPushButton)
        self.conditionDownPushButton = QtWidgets.QPushButton(self.horizontalGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.conditionDownPushButton.sizePolicy().hasHeightForWidth())
        self.conditionDownPushButton.setSizePolicy(sizePolicy)
        self.conditionDownPushButton.setMinimumSize(QtCore.QSize(10, 23))
        self.conditionDownPushButton.setObjectName("conditionDownPushButton")
        self.horizontalLayout_3.addWidget(self.conditionDownPushButton)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem5)
        self.gridLayout.addLayout(self.horizontalLayout_3, 4, 2, 1, 1)
        self.createConditionPushButton = QtWidgets.QPushButton(self.horizontalGroupBox)
        self.createConditionPushButton.setObjectName("createConditionPushButton")
        self.gridLayout.addWidget(self.createConditionPushButton, 4, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.horizontalGroupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 2, 1, 1)
        self.availableTransitionsListWidget = QtWidgets.QListWidget(self.horizontalGroupBox)
        self.availableTransitionsListWidget.setObjectName("availableTransitionsListWidget")
        self.gridLayout.addWidget(self.availableTransitionsListWidget, 3, 6, 1, 1)
        self.deleteAvailableConditionPushButton = QtWidgets.QPushButton(self.horizontalGroupBox)
        self.deleteAvailableConditionPushButton.setObjectName("deleteAvailableConditionPushButton")
        self.gridLayout.addWidget(self.deleteAvailableConditionPushButton, 5, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.horizontalGroupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 6, 1, 1)
        self.verticalLayout_2.addWidget(self.horizontalGroupBox)
        self.saveExperimentPushButton = QtWidgets.QPushButton(ExperimentManagerWidget)
        self.saveExperimentPushButton.setMinimumSize(QtCore.QSize(0, 50))
        self.saveExperimentPushButton.setObjectName("saveExperimentPushButton")
        self.verticalLayout_2.addWidget(self.saveExperimentPushButton)

        self.retranslateUi(ExperimentManagerWidget)
        QtCore.QMetaObject.connectSlotsByName(ExperimentManagerWidget)

    def retranslateUi(self, ExperimentManagerWidget):
        _translate = QtCore.QCoreApplication.translate
        ExperimentManagerWidget.setWindowTitle(_translate("ExperimentManagerWidget", "Edit Current Experiment"))
        self.groupBox.setTitle(_translate("ExperimentManagerWidget", "Current experiment"))
        self.label.setText(_translate("ExperimentManagerWidget", "Current Experiment:"))
        self.label_5.setText(_translate("ExperimentManagerWidget", "Modules included in experiment:"))
        self.baseSettingsTreeWidget.headerItem().setText(0, _translate("ExperimentManagerWidget", "Setting Item"))
        self.baseSettingsTreeWidget.headerItem().setText(1, _translate("ExperimentManagerWidget", "Value"))
        self.label_4.setText(_translate("ExperimentManagerWidget", "Base Settings:"))
        self.horizontalGroupBox.setTitle(_translate("ExperimentManagerWidget", "Conditions"))
        self.addConditionPushButton.setText(_translate("ExperimentManagerWidget", "🡒"))
        self.removeConditionPushButton.setText(_translate("ExperimentManagerWidget", "🡐"))
        self.addTransitionPushButton.setText(_translate("ExperimentManagerWidget", "🡐"))
        self.removeTransitionPushButton.setText(_translate("ExperimentManagerWidget", "🡒"))
        self.label_2.setText(_translate("ExperimentManagerWidget", "Available Conditions"))
        self.conditionUpPushButton.setText(_translate("ExperimentManagerWidget", "🡑"))
        self.conditionDownPushButton.setText(_translate("ExperimentManagerWidget", "🡓"))
        self.createConditionPushButton.setText(_translate("ExperimentManagerWidget", "Create new condition from current settings"))
        self.label_3.setText(_translate("ExperimentManagerWidget", "Current Condition Sequence"))
        self.deleteAvailableConditionPushButton.setText(_translate("ExperimentManagerWidget", "Remove selected available condition"))
        self.label_6.setText(_translate("ExperimentManagerWidget", "Available Transitions"))
        self.saveExperimentPushButton.setText(_translate("ExperimentManagerWidget", "Save experiment"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ExperimentManagerWidget = QtWidgets.QWidget()
    ui = Ui_ExperimentManagerWidget()
    ui.setupUi(ExperimentManagerWidget)
    ExperimentManagerWidget.show()
    sys.exit(app.exec_())