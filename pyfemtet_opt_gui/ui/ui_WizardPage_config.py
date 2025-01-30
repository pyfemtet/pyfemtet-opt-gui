# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WizardPage_configlYhibT.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QGridLayout,
    QHeaderView, QSizePolicy, QTextEdit, QTreeView,
    QWidget, QWizardPage)

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        if not WizardPage.objectName():
            WizardPage.setObjectName(u"WizardPage")
        WizardPage.resize(629, 387)
        self.gridLayout = QGridLayout(WizardPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.textEdit = QTextEdit(WizardPage)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit, 1, 0, 1, 1)

        self.treeView = QTreeView(WizardPage)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.gridLayout.addWidget(self.treeView, 0, 0, 1, 1)


        self.retranslateUi(WizardPage)

        QMetaObject.connectSlotsByName(WizardPage)
    # setupUi

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QCoreApplication.translate("WizardPage", u"WizardPage", None))
        self.textEdit.setMarkdown(QCoreApplication.translate("WizardPage", u"\u6700\u9069\u5316\u306e\u5b9f\u884c\u8a2d\u5b9a\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"", None))
        self.textEdit.setHtml(QCoreApplication.translate("WizardPage", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u6700\u9069\u5316\u306e\u5b9f\u884c\u8a2d\u5b9a\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p></body></html>", None))
    # retranslateUi

