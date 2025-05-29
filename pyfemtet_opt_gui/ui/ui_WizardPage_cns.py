# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WizardPage_cnsfPCAia.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QFrame,
    QGridLayout, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QTableView, QTextEdit, QVBoxLayout,
    QWidget, QWizardPage)

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        if not WizardPage.objectName():
            WizardPage.setObjectName(u"WizardPage")
        WizardPage.resize(490, 314)
        self.gridLayout = QGridLayout(WizardPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton_add = QPushButton(WizardPage)
        self.pushButton_add.setObjectName(u"pushButton_add")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.pushButton_add.setIcon(icon)

        self.verticalLayout.addWidget(self.pushButton_add)

        self.pushButton_edit = QPushButton(WizardPage)
        self.pushButton_edit.setObjectName(u"pushButton_edit")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MailMessageNew))
        self.pushButton_edit.setIcon(icon1)

        self.verticalLayout.addWidget(self.pushButton_edit)

        self.pushButton_delete = QPushButton(WizardPage)
        self.pushButton_delete.setObjectName(u"pushButton_delete")
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditDelete))
        self.pushButton_delete.setIcon(icon2)

        self.verticalLayout.addWidget(self.pushButton_delete)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_cnsList = QLabel(WizardPage)
        self.label_cnsList.setObjectName(u"label_cnsList")

        self.verticalLayout_2.addWidget(self.label_cnsList)

        self.tableView_cnsList = QTableView(WizardPage)
        self.tableView_cnsList.setObjectName(u"tableView_cnsList")
        self.tableView_cnsList.setFrameShape(QFrame.Shape.Panel)
        self.tableView_cnsList.setEditTriggers(QAbstractItemView.EditTrigger.AnyKeyPressed|QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tableView_cnsList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView_cnsList.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView_cnsList.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableView_cnsList.horizontalHeader().setCascadingSectionResizes(True)
        self.tableView_cnsList.horizontalHeader().setHighlightSections(False)
        self.tableView_cnsList.horizontalHeader().setStretchLastSection(True)
        self.tableView_cnsList.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.tableView_cnsList)


        self.gridLayout.addLayout(self.verticalLayout_2, 0, 1, 1, 1)

        self.textEdit_7 = QTextEdit(WizardPage)
        self.textEdit_7.setObjectName(u"textEdit_7")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit_7.sizePolicy().hasHeightForWidth())
        self.textEdit_7.setSizePolicy(sizePolicy)
        self.textEdit_7.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit_7.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit_7, 1, 0, 1, 2)

#if QT_CONFIG(shortcut)
        self.label_cnsList.setBuddy(self.tableView_cnsList)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(WizardPage)

        QMetaObject.connectSlotsByName(WizardPage)
    # setupUi

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QCoreApplication.translate("WizardPage", u"WizardPage", None))
        self.pushButton_add.setText(QCoreApplication.translate("WizardPage", u"\u8ffd\u52a0", None))
        self.pushButton_edit.setText(QCoreApplication.translate("WizardPage", u"\u7de8\u96c6", None))
        self.pushButton_delete.setText(QCoreApplication.translate("WizardPage", u"\u524a\u9664", None))
        self.label_cnsList.setText(QCoreApplication.translate("WizardPage", u"\u62d8\u675f\u5f0f\u306e\u4e00\u89a7", None))
        self.textEdit_7.setMarkdown(QCoreApplication.translate("WizardPage", u"\u300c\u62d8\u675f\u5f0f\u300d\u306e\u4e0d\u7b49\u5f0f\u304c\u6210\u7acb\u3059\u308b\u30d1\u30e9\u30e1\u30fc\u30bf\u3067\u306e\u307f\u89e3\u6790\u304c\u5b9f\u884c\u3055\u308c\u308b\u3088\u3046\u306b\u3067\u304d\u307e\u3059\u3002\n"
"\n"
"\u30d1\u30e9\u30e1\u30fc\u30bf\u306e\u7d44\u5408\u305b\u3092\u5236\u9650\u3057\u305f\u3044\u5834\u5408\u306f\u3001\u3053\u306e\u753b\u9762\u3067\u8a2d\u5b9a\u3057\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"\u3053\u306e\u8a2d\u5b9a\u304c\u5fc5\u8981\u306a\u3051\u308c\u3070\u3001\u300c\u6b21\u3078\u300d\u3092\u62bc\u3057\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"", None))
        self.textEdit_7.setHtml(QCoreApplication.translate("WizardPage", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u300c\u62d8\u675f\u5f0f\u300d\u306e\u4e0d\u7b49\u5f0f\u304c\u6210\u7acb\u3059\u308b\u30d1\u30e9\u30e1\u30fc\u30bf\u3067\u306e\u307f\u89e3\u6790\u304c\u5b9f\u884c\u3055\u308c\u308b\u3088\u3046\u306b\u3067\u304d\u307e\u3059\u3002</p>\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u30d1\u30e9\u30e1\u30fc\u30bf\u306e\u7d44"
                        "\u5408\u305b\u3092\u5236\u9650\u3057\u305f\u3044\u5834\u5408\u306f\u3001\u3053\u306e\u753b\u9762\u3067\u8a2d\u5b9a\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u3053\u306e\u8a2d\u5b9a\u304c\u5fc5\u8981\u306a\u3051\u308c\u3070\u3001\u300c\u6b21\u3078\u300d\u3092\u62bc\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p></body></html>", None))
    # retranslateUi

