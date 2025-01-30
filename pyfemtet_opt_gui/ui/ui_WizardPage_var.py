# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WizardPage_varvBrBdu.ui'
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

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        if not WizardPage.objectName():
            WizardPage.setObjectName(u"WizardPage")
        WizardPage.resize(634, 319)
        self.gridLayout = QGridLayout(WizardPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_load_prm = QPushButton(WizardPage)
        self.pushButton_load_prm.setObjectName(u"pushButton_load_prm")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoDown))
        self.pushButton_load_prm.setIcon(icon)

        self.gridLayout.addWidget(self.pushButton_load_prm, 0, 0, 1, 1)

        self.tableView = QTableView(WizardPage)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.AnyKeyPressed|QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.tableView.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableView.horizontalHeader().setCascadingSectionResizes(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.tableView, 0, 1, 1, 1)

        self.pushButton_test_prm = QPushButton(WizardPage)
        self.pushButton_test_prm.setObjectName(u"pushButton_test_prm")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoUp))
        self.pushButton_test_prm.setIcon(icon1)

        self.gridLayout.addWidget(self.pushButton_test_prm, 0, 2, 1, 1)

        self.textEdit = QTextEdit(WizardPage)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit, 1, 0, 1, 3)

        self.commandLinkButton = QCommandLinkButton(WizardPage)
        self.commandLinkButton.setObjectName(u"commandLinkButton")

        self.gridLayout.addWidget(self.commandLinkButton, 2, 0, 1, 3)


        self.retranslateUi(WizardPage)

        QMetaObject.connectSlotsByName(WizardPage)
    # setupUi

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QCoreApplication.translate("WizardPage", u"WizardPage", None))
        self.pushButton_load_prm.setText(QCoreApplication.translate("WizardPage", u"Load", None))
        self.pushButton_test_prm.setText(QCoreApplication.translate("WizardPage", u"Test", None))
#if QT_CONFIG(tooltip)
        self.textEdit.setToolTip(QCoreApplication.translate("WizardPage", u"<html><head/><body><p>&lt;\u7528\u8a9e\u306e\u8aac\u660e&gt;</p><p>\u300c\u5909\u6570\u300d...Femtet \u89e3\u6790\u30e2\u30c7\u30eb\u3067\u5b9a\u7fa9\u3055\u308c\u3066\u3044\u308b\u5909\u6570\u3067\u3059\u3002 (\u4f8b\uff1a&quot;coil_height&quot;)</p><p>\u300c\u30d1\u30e9\u30e1\u30fc\u30bf\u300d...\u300c\u5909\u6570\u300d\u306e\u3046\u3061\u3001\u6700\u9069\u5316\u306e\u969b\u306b\u5024\u3092\u5909\u66f4\u3059\u308b\u3082\u306e\u3067\u3059\u3002</p><p>\u300c\u5f0f\u300d...\u300c\u5909\u6570\u300d\u306e\u5024\u3092\u6c7a\u3081\u308b\u305f\u3081\u306e\u6570\u5f0f\u3067\u3059\u3002Femtet \u306e\u30d7\u30ed\u30b8\u30a7\u30af\u30c8\u30c4\u30ea\u30fc\u306b\u8868\u793a\u3055\u308c\u3066\u3044\u308b\u3082\u306e\u3067\u3059\u3002 (\u4f8b: &quot;coil_pitch * n * 3&quot;, &quot;1 * 2&quot;)</p><p>\u300c\u6587\u5b57\u5f0f\u300d...\u300c\u5909\u6570\u300d\u306e\u300c\u5f0f\u300d\u306e\u3046\u3061\u3001\u4ed6\u306e\u300c\u5909\u6570\u300d\u3092\u53c2\u7167\u3057\u3066\u3044\u308b\u3082\u306e\u3067\u3059\u3002 (\u4f8b: &quot"
                        ";coil_pitch * n * 3&quot;)</p><p>\u300c\u6570\u5f0f\u300d...\u300c\u5909\u6570\u300d\u306e\u300c\u5f0f\u300d\u306e\u3046\u3061\u300c\u6587\u5b57\u5f0f\u300d\u4ee5\u5916\u306e\u3082\u306e\u3001\u3064\u307e\u308a\u6570\u5b57\u306e\u307f\u3067\u5b9a\u7fa9\u3055\u308c\u3066\u3044\u308b\u300c\u5f0f\u300d\u3067\u3059\u3002 (\u4f8b: &quot;1 * 2&quot;)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.textEdit.setMarkdown(QCoreApplication.translate("WizardPage", u"\u6700\u9069\u5316\u306e\u969b\u306b\u8abf\u6574\u3059\u308b\u30d1\u30e9\u30e1\u30fc\u30bf\u3092\u9078\u629e\u3057\u3001\u521d\u671f\u5024\u3001\u4e0b\u9650\u3001\u4e0a\u9650\u3092\u8a2d\u5b9a\u30fb\u78ba\u8a8d\u3057\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"Femtet \u3067\u5909\u6570\u3084\u5f0f\u306e\u8a2d\u5b9a\u3092\u5909\u66f4\u3057\u305f\u5834\u5408\u306f\u300cLoad\u300d\u30dc\u30bf\u30f3\u3092\u62bc\u3057\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"\u300cTest\u300d \u30dc\u30bf\u30f3\u3092\u62bc\u3059\u3068 Femtet \u306b\u300c\u30c6\u30b9\u30c8\u5024\u300d\u5217\u306e\u5024\u3092\u8ee2\u9001\u3057\u3001\u305d\u306e\u5024\u3067\u306e\u30e2\u30c7\u30eb\u306e\u72b6\u614b\u3092\u78ba\u8a8d\u3059\u308b\u3053\u3068\u304c\u3067\u304d\u307e\u3059\u3002\n"
"\n"
"", None))
        self.textEdit.setHtml(QCoreApplication.translate("WizardPage", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u6700\u9069\u5316\u306e\u969b\u306b\u8abf\u6574\u3059\u308b\u30d1\u30e9\u30e1\u30fc\u30bf\u3092\u9078\u629e\u3057\u3001\u521d\u671f\u5024\u3001\u4e0b\u9650\u3001\u4e0a\u9650\u3092\u8a2d\u5b9a\u30fb\u78ba\u8a8d\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Femtet \u3067\u5909"
                        "\u6570\u3084\u5f0f\u306e\u8a2d\u5b9a\u3092\u5909\u66f4\u3057\u305f\u5834\u5408\u306f\u300cLoad\u300d\u30dc\u30bf\u30f3\u3092\u62bc\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u300cTest\u300d \u30dc\u30bf\u30f3\u3092\u62bc\u3059\u3068 Femtet \u306b\u300c\u30c6\u30b9\u30c8\u5024\u300d\u5217\u306e\u5024\u3092\u8ee2\u9001\u3057\u3001\u305d\u306e\u5024\u3067\u306e\u30e2\u30c7\u30eb\u306e\u72b6\u614b\u3092\u78ba\u8a8d\u3059\u308b\u3053\u3068\u304c\u3067\u304d\u307e\u3059\u3002</p></body></html>", None))
        self.commandLinkButton.setText(QCoreApplication.translate("WizardPage", u"\u5909\u6570 \u306e\u4f7f\u3044\u65b9\u3092\u78ba\u8a8d\u3059\u308b\uff08\u30a4\u30f3\u30bf\u30fc\u30cd\u30c3\u30c8\u30ea\u30f3\u30af\uff09", None))
    # retranslateUi

