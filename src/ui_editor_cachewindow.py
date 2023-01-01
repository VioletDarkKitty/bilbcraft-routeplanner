# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'editor_cachewindowCrNqir.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(396, 226)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.edit_x_min = QSpinBox(Form)
        self.edit_x_min.setObjectName(u"edit_x_min")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.edit_x_min)

        self.edit_x_max = QSpinBox(Form)
        self.edit_x_max.setObjectName(u"edit_x_max")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.edit_x_max)

        self.edit_y_min = QSpinBox(Form)
        self.edit_y_min.setObjectName(u"edit_y_min")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.edit_y_min)

        self.edit_y_max = QSpinBox(Form)
        self.edit_y_max.setObjectName(u"edit_y_max")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.edit_y_max)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_4)

        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_5)

        self.edit_threads = QSpinBox(Form)
        self.edit_threads.setObjectName(u"edit_threads")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.edit_threads)


        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.start_button = QPushButton(Form)
        self.start_button.setObjectName(u"start_button")

        self.horizontalLayout.addWidget(self.start_button)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.progress_text = QLabel(Form)
        self.progress_text.setObjectName(u"progress_text")

        self.horizontalLayout_2.addWidget(self.progress_text)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.progressBar = QProgressBar(Form)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.horizontalLayout_2.addWidget(self.progressBar)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label.setText(QCoreApplication.translate("Form", u"Min X", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Max X", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Min Y", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Max Y", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Threads", None))
        self.start_button.setText(QCoreApplication.translate("Form", u"Start", None))
        self.progress_text.setText(QCoreApplication.translate("Form", u"TextLabel", None))
    # retranslateUi

