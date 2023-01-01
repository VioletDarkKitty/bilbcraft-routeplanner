# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'editor_connectionSeIrmY.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(292, 218)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_2)

        self.location_combo1 = QComboBox(Form)
        self.location_combo1.setObjectName(u"location_combo1")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.location_combo1)

        self.location_combo2 = QComboBox(Form)
        self.location_combo2.setObjectName(u"location_combo2")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.location_combo2)

        self.edit_label = QLineEdit(Form)
        self.edit_label.setObjectName(u"edit_label")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.edit_label)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_3)

        self.edit_weight = QSpinBox(Form)
        self.edit_weight.setObjectName(u"edit_weight")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.edit_weight)

        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_5)

        self.edit_train = QCheckBox(Form)
        self.edit_train.setObjectName(u"edit_train")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.edit_train)


        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.delete_connection = QPushButton(Form)
        self.delete_connection.setObjectName(u"delete_connection")

        self.horizontalLayout_2.addWidget(self.delete_connection)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.cancel_button = QPushButton(Form)
        self.cancel_button.setObjectName(u"cancel_button")

        self.horizontalLayout.addWidget(self.cancel_button)

        self.ok_button = QPushButton(Form)
        self.ok_button.setObjectName(u"ok_button")

        self.horizontalLayout.addWidget(self.ok_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Form)

        self.ok_button.setDefault(True)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"Location 1", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Location 2", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Label", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Weight", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Train?", None))
        self.edit_train.setText("")
        self.delete_connection.setText(QCoreApplication.translate("Form", u"Delete Connection", None))
        self.cancel_button.setText(QCoreApplication.translate("Form", u"Cancel", None))
        self.ok_button.setText(QCoreApplication.translate("Form", u"Create", None))
    # retranslateUi

