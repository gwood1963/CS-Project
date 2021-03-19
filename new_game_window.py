# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_game_window.ui'
##
## Created by: Qt User Interface Compiler version 6.0.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_new_game_dialog(object):
    def setupUi(self, new_game_dialog):
        if not new_game_dialog.objectName():
            new_game_dialog.setObjectName(u"new_game_dialog")
        new_game_dialog.setWindowModality(Qt.WindowModal)
        new_game_dialog.resize(179, 166)
        new_game_dialog.setModal(True)
        self.verticalLayout = QVBoxLayout(new_game_dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.to_move = QGroupBox(new_game_dialog)
        self.to_move.setObjectName(u"to_move")
        self.horizontalLayout_3 = QHBoxLayout(self.to_move)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.white = QRadioButton(self.to_move)
        self.white.setObjectName(u"white")
        self.white.setChecked(True)

        self.horizontalLayout_3.addWidget(self.white)

        self.black = QRadioButton(self.to_move)
        self.black.setObjectName(u"black")
        self.black.setChecked(False)

        self.horizontalLayout_3.addWidget(self.black)


        self.verticalLayout.addWidget(self.to_move)

        self.start_pos = QGroupBox(new_game_dialog)
        self.start_pos.setObjectName(u"start_pos")
        self.horizontalLayout_2 = QHBoxLayout(self.start_pos)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.standard = QRadioButton(self.start_pos)
        self.standard.setObjectName(u"standard")
        self.standard.setChecked(True)

        self.horizontalLayout_2.addWidget(self.standard)

        self.custom = QRadioButton(self.start_pos)
        self.custom.setObjectName(u"custom")

        self.horizontalLayout_2.addWidget(self.custom)


        self.verticalLayout.addWidget(self.start_pos)

        self.response = QDialogButtonBox(new_game_dialog)
        self.response.setObjectName(u"response")
        self.response.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.response.setCenterButtons(True)

        self.verticalLayout.addWidget(self.response)


        self.retranslateUi(new_game_dialog)
        self.response.accepted.connect(new_game_dialog.accept)
        self.response.rejected.connect(new_game_dialog.reject)

        QMetaObject.connectSlotsByName(new_game_dialog)
    # setupUi

    def retranslateUi(self, new_game_dialog):
        new_game_dialog.setWindowTitle(QCoreApplication.translate("new_game_dialog", u"New game", None))
        self.to_move.setTitle(QCoreApplication.translate("new_game_dialog", u"To move ...", None))
        self.white.setText(QCoreApplication.translate("new_game_dialog", u"White", None))
        self.black.setText(QCoreApplication.translate("new_game_dialog", u"Black", None))
        self.start_pos.setTitle(QCoreApplication.translate("new_game_dialog", u"Starting position ...", None))
        self.standard.setText(QCoreApplication.translate("new_game_dialog", u"Standard", None))
        self.custom.setText(QCoreApplication.translate("new_game_dialog", u"Custom", None))
    # retranslateUi

