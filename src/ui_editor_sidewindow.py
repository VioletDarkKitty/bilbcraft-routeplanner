# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'editor-sidewindowlxkqvk.ui'
##
## Created by: Qt User Interface Compiler version 6.2.4
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QSizePolicy, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 265)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.id_edit = QLineEdit(Form)
        self.id_edit.setObjectName(u"id_edit")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.id_edit)

        self.label_edit = QLineEdit(Form)
        self.label_edit.setObjectName(u"label_edit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.label_edit)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_4)

        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_5)

        self.x_edit = QSpinBox(Form)
        self.x_edit.setObjectName(u"x_edit")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.x_edit)

        self.y_edit = QSpinBox(Form)
        self.y_edit.setObjectName(u"y_edit")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.y_edit)


        self.verticalLayout.addLayout(self.formLayout)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.connections_list = QListWidget(Form)
        self.connections_list.setObjectName(u"connections_list")

        self.verticalLayout.addWidget(self.connections_list)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"ID", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Label", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"X", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Y (minecraft Z)", None))
        self.label.setText(QCoreApplication.translate("Form", u"Connections", None))
    # retranslateUi

