# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WizardPage_confirmOUKWAT.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QCheckBox, QGridLayout,
    QHeaderView, QPushButton, QSizePolicy, QTextBrowser,
    QTreeView, QWidget, QWizardPage)

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        if not WizardPage.objectName():
            WizardPage.setObjectName(u"WizardPage")
        WizardPage.resize(603, 514)
        self.gridLayout = QGridLayout(WizardPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.textBrowser = QTextBrowser(WizardPage)
        self.textBrowser.setObjectName(u"textBrowser")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textBrowser.setOpenExternalLinks(True)

        self.gridLayout.addWidget(self.textBrowser, 1, 0, 1, 2)

        self.treeView = QTreeView(WizardPage)
        self.treeView.setObjectName(u"treeView")
        self.treeView.header().setVisible(False)

        self.gridLayout.addWidget(self.treeView, 0, 0, 1, 2)

        self.checkBox_save_with_run = QCheckBox(WizardPage)
        self.checkBox_save_with_run.setObjectName(u"checkBox_save_with_run")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.checkBox_save_with_run.sizePolicy().hasHeightForWidth())
        self.checkBox_save_with_run.setSizePolicy(sizePolicy1)
        self.checkBox_save_with_run.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_save_with_run, 2, 1, 1, 1)

        self.pushButton_save_script = QPushButton(WizardPage)
        self.pushButton_save_script.setObjectName(u"pushButton_save_script")

        self.gridLayout.addWidget(self.pushButton_save_script, 2, 0, 1, 1)


        self.retranslateUi(WizardPage)

        QMetaObject.connectSlotsByName(WizardPage)
    # setupUi

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QCoreApplication.translate("WizardPage", u"WizardPage", None))
#if QT_CONFIG(accessibility)
        self.textBrowser.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.textBrowser.setHtml(QCoreApplication.translate("WizardPage", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u4ee5\u4e0a\u306e\u8a2d\u5b9a\u3067\u3088\u308d\u3057\u3044\u3067\u3059\u304b\uff1f\u300c\u30b9\u30af\u30ea\u30d7\u30c8\u3092\u4fdd\u5b58\u3059\u308b\u300d\u3092\u62bc\u3059\u3068\u6700\u9069\u5316\u3092\u5b9f\u884c\u3059\u308b\u305f\u3081\u306e\u30d7\u30ed\u30b0\u30e9\u30e0\u3092\u4fdd\u5b58\u3057\u307e\u3059\u3002</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-ri"
                        "ght:0px; -qt-block-indent:0; text-indent:0px;\">\u300c\u3059\u3050\u5b9f\u884c\u3059\u308b\u300d\u3092\u30c1\u30a7\u30c3\u30af\u3057\u3066\u300c\u30b9\u30af\u30ea\u30d7\u30c8\u3092\u4fdd\u5b58\u3059\u308b\u300d\u3092\u62bc\u3059\u3068\u3001\u30b9\u30af\u30ea\u30d7\u30c8\u4fdd\u5b58\u5f8c\u305d\u306e\u30b9\u30af\u30ea\u30d7\u30c8\u3092\u4f7f\u7528\u3057\u3066\u6700\u9069\u5316\u3092\u958b\u59cb\u3057\u307e\u3059\u3002</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u6700\u9069\u5316\u4e2d\u306e\u30ed\u30b0\u51fa\u529b\u306f\u3001\u30b3\u30f3\u30bd\u30fc\u30eb\u753b\u9762\uff08\u30b3\u30de\u30f3\u30c9\u30d7\u30ed\u30f3\u30d7\u30c8\uff09\u3092\u3054\u89a7\u304f\u3060\u3055\u3044\u3002</p></body></html>", None))
        self.checkBox_save_with_run.setText(QCoreApplication.translate("WizardPage", u"\u30b9\u30af\u30ea\u30d7\u30c8\u306e\u4fdd\u5b58\u5f8c\u3001\u3059\u3050\u5b9f\u884c\u3059\u308b", None))
#if QT_CONFIG(accessibility)
        self.pushButton_save_script.setAccessibleName(QCoreApplication.translate("WizardPage", u"\u30b9\u30af\u30ea\u30d7\u30c8\u3092\u4fdd\u5b58\u3059\u308b", None))
#endif // QT_CONFIG(accessibility)
        self.pushButton_save_script.setText(QCoreApplication.translate("WizardPage", u"\u30b9\u30af\u30ea\u30d7\u30c8\u3092\u4fdd\u5b58\u3059\u308b", None))
    # retranslateUi

