# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'go_to_move.ui'
##
## Created by: Qt User Interface Compiler version 6.0.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_go_to_move(object):
    def setupUi(self, go_to_move):
        if not go_to_move.objectName():
            go_to_move.setObjectName(u"go_to_move")
        go_to_move.resize(174, 113)
        self.verticalLayout = QVBoxLayout(go_to_move)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.move_num = QLineEdit(go_to_move)
        self.move_num.setObjectName(u"move_num")

        self.verticalLayout.addWidget(self.move_num)

        self.widget = QWidget(go_to_move)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.white = QRadioButton(self.widget)
        self.white.setObjectName(u"white")
        self.white.setChecked(True)

        self.horizontalLayout.addWidget(self.white)

        self.black = QRadioButton(self.widget)
        self.black.setObjectName(u"black")

        self.horizontalLayout.addWidget(self.black)


        self.verticalLayout.addWidget(self.widget)

        self.buttonBox = QDialogButtonBox(go_to_move)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(go_to_move)
        self.buttonBox.accepted.connect(go_to_move.accept)
        self.buttonBox.rejected.connect(go_to_move.reject)

        QMetaObject.connectSlotsByName(go_to_move)
    # setupUi

    def retranslateUi(self, go_to_move):
        go_to_move.setWindowTitle(QCoreApplication.translate("go_to_move", u"Go to move", None))
        self.white.setText(QCoreApplication.translate("go_to_move", u"White", None))
        self.black.setText(QCoreApplication.translate("go_to_move", u"Black", None))
    # retranslateUi

