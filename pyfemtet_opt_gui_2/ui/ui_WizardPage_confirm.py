# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WizardPage_confirmjXvWKh.ui'
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
from PySide6.QtWidgets import (QApplication, QHeaderView, QSizePolicy, QTreeView,
    QWidget, QWizardPage)

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        if not WizardPage.objectName():
            WizardPage.setObjectName(u"WizardPage")
        WizardPage.resize(400, 300)
        self.treeView = QTreeView(WizardPage)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setGeometry(QRect(60, 20, 256, 192))

        self.retranslateUi(WizardPage)

        QMetaObject.connectSlotsByName(WizardPage)
    # setupUi

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QCoreApplication.translate("WizardPage", u"WizardPage", None))
    # retranslateUi

