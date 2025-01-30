# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WizardPage_analysis_modelbQYNCo.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QGridLayout,
    QHeaderView, QPushButton, QSizePolicy, QTableView,
    QTextEdit, QWidget, QWizardPage)

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        if not WizardPage.objectName():
            WizardPage.setObjectName(u"WizardPage")
        WizardPage.resize(601, 364)
        self.gridLayout = QGridLayout(WizardPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_load = QPushButton(WizardPage)
        self.pushButton_load.setObjectName(u"pushButton_load")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoDown))
        self.pushButton_load.setIcon(icon)

        self.gridLayout.addWidget(self.pushButton_load, 0, 0, 1, 1)

        self.textEdit = QTextEdit(WizardPage)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit, 1, 0, 1, 2)

        self.tableView = QTableView(WizardPage)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setWordWrap(False)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.tableView, 0, 1, 1, 1)


        self.retranslateUi(WizardPage)

        QMetaObject.connectSlotsByName(WizardPage)
    # setupUi

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QCoreApplication.translate("WizardPage", u"WizardPage", None))
        self.pushButton_load.setText(QCoreApplication.translate("WizardPage", u"Load", None))
        self.textEdit.setMarkdown(QCoreApplication.translate("WizardPage", u"Femtet \u3067\u6700\u9069\u5316\u3057\u305f\u3044 .femprj \u30d5\u30a1\u30a4\u30eb\u3092\u958b\u3044\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
".femprj \u30d5\u30a1\u30a4\u30eb\u3092\u5909\u66f4\u3057\u305f\u5834\u5408\u306f\u3001\u518d\u8aad\u307f\u8fbc\u307f\u306e\u305f\u3081\u300cLoad\u300d\u30dc\u30bf\u30f3\u3092\u62bc\u3057\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"\u4e0a\u8a18\u306e .femprj \u3068 model \u306b\u9593\u9055\u3044\u304c\u306a\u3051\u308c\u3070\u3001\u300c\u6b21\u3078 / Next\u300d \u3092\u62bc\u3057\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"", None))
        self.textEdit.setHtml(QCoreApplication.translate("WizardPage", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Femtet \u3067\u6700\u9069\u5316\u3057\u305f\u3044 .femprj \u30d5\u30a1\u30a4\u30eb\u3092\u958b\u3044\u3066\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">.femprj \u30d5\u30a1\u30a4\u30eb\u3092\u5909\u66f4\u3057\u305f\u5834\u5408\u306f\u3001\u518d\u8aad\u307f\u8fbc\u307f\u306e\u305f\u3081"
                        "\u300cLoad\u300d\u30dc\u30bf\u30f3\u3092\u62bc\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u4e0a\u8a18\u306e .femprj \u3068 model \u306b\u9593\u9055\u3044\u304c\u306a\u3051\u308c\u3070\u3001\u300c\u6b21\u3078 / Next\u300d \u3092\u62bc\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p></body></html>", None))
    # retranslateUi

