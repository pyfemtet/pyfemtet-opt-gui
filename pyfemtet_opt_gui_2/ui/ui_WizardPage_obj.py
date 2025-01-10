# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WizardPage_objQiBzQa.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCommandLinkButton,
    QGridLayout, QHeaderView, QPushButton, QSizePolicy,
    QTableView, QTextEdit, QWidget, QWizardPage)

class Ui_WizardPage_obj(object):
    def setupUi(self, WizardPage_obj):
        if not WizardPage_obj.objectName():
            WizardPage_obj.setObjectName(u"WizardPage_obj")
        WizardPage_obj.resize(624, 386)
        self.gridLayout = QGridLayout(WizardPage_obj)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton = QPushButton(WizardPage_obj)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 1)

        self.tableView = QTableView(WizardPage_obj)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.AnyKeyPressed|QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tableView.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableView.horizontalHeader().setCascadingSectionResizes(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.tableView, 0, 1, 1, 1)

        self.textEdit = QTextEdit(WizardPage_obj)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit, 1, 0, 1, 2)

        self.commandLinkButton = QCommandLinkButton(WizardPage_obj)
        self.commandLinkButton.setObjectName(u"commandLinkButton")
        self.commandLinkButton.setIconSize(QSize(20, 20))

        self.gridLayout.addWidget(self.commandLinkButton, 2, 0, 1, 2)


        self.retranslateUi(WizardPage_obj)

        QMetaObject.connectSlotsByName(WizardPage_obj)
    # setupUi

    def retranslateUi(self, WizardPage_obj):
        WizardPage_obj.setWindowTitle(QCoreApplication.translate("WizardPage_obj", u"WizardPage", None))
        self.pushButton.setText(QCoreApplication.translate("WizardPage_obj", u"[F\u27a1] sync", None))
#if QT_CONFIG(tooltip)
        self.textEdit.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.textEdit.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.textEdit.setHtml(QCoreApplication.translate("WizardPage_obj", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u6700\u9069\u5316\u3059\u308b\u76ee\u7684\u95a2\u6570\u3092\u9078\u3093\u3067\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u203b Femtet \u306e\u30d1\u30e9\u30e1\u30c8\u30ea\u30c3\u30af\u89e3\u6790\u30c0\u30a4\u30a2\u30ed\u30b0\u3067\u76ee\u7684\u95a2\u6570\u3092\u5b9a\u7fa9\u3057\u3066"
                        "\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u203b <span style=\" font-weight:700;\">\u6700\u9069\u5316\u5b9f\u884c\u524d\u306b\u65e2\u5b58\u306e\u30b9\u30a4\u30fc\u30d7\u30c6\u30fc\u30d6\u30eb\u3092\u524a\u9664\u3057\u3066\u304f\u3060\u3055\u3044\u3002</span></p></body></html>", None))
        self.commandLinkButton.setText(QCoreApplication.translate("WizardPage_obj", u"\u30d1\u30e9\u30e1\u30c8\u30ea\u30c3\u30af\u89e3\u6790\u306e\u4f7f\u3044\u65b9\u3092\u78ba\u8a8d\u3059\u308b\uff08\u30a4\u30f3\u30bf\u30fc\u30cd\u30c3\u30c8\u30ea\u30f3\u30af\uff09", None))
    # retranslateUi

