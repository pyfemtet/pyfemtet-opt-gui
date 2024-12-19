# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WizardPage_objvaysqx.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHeaderView, QSizePolicy,
    QTableView, QWidget, QWizardPage)

class Ui_WizardPage_obj(object):
    def setupUi(self, WizardPage_obj):
        if not WizardPage_obj.objectName():
            WizardPage_obj.setObjectName(u"WizardPage_obj")
        WizardPage_obj.resize(400, 300)
        self.tableView_obj = QTableView(WizardPage_obj)
        self.tableView_obj.setObjectName(u"tableView_obj")
        self.tableView_obj.setGeometry(QRect(45, 61, 271, 171))
        self.tableView_obj.setEditTriggers(QAbstractItemView.EditTrigger.AnyKeyPressed|QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tableView_obj.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableView_obj.horizontalHeader().setCascadingSectionResizes(True)
        self.tableView_obj.horizontalHeader().setStretchLastSection(True)

        self.retranslateUi(WizardPage_obj)

        QMetaObject.connectSlotsByName(WizardPage_obj)
    # setupUi

    def retranslateUi(self, WizardPage_obj):
        WizardPage_obj.setWindowTitle(QCoreApplication.translate("WizardPage_obj", u"WizardPage", None))
    # retranslateUi

