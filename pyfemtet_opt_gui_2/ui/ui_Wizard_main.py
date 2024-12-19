# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Wizard_maincYSgHr.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QPushButton, QSizePolicy, QWidget,
    QWizard, QWizardPage)

class Ui_Wizard(object):
    def setupUi(self, Wizard):
        if not Wizard.objectName():
            Wizard.setObjectName(u"Wizard")
        Wizard.resize(400, 300)
        Wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.wizardPage_init = QWizardPage()
        self.wizardPage_init.setObjectName(u"wizardPage_init")
        self.pushButton = QPushButton(self.wizardPage_init)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(170, 100, 75, 24))
        Wizard.addPage(self.wizardPage_init)

        self.retranslateUi(Wizard)

        QMetaObject.connectSlotsByName(Wizard)
    # setupUi

    def retranslateUi(self, Wizard):
        Wizard.setWindowTitle(QCoreApplication.translate("Wizard", u"Wizard", None))
        self.pushButton.setText(QCoreApplication.translate("Wizard", u"inital page", None))
    # retranslateUi

