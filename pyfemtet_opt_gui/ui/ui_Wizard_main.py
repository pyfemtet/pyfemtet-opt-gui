# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Wizard_mainIULYOf.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QCheckBox, QComboBox,
    QGridLayout, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QTextEdit, QWidget, QWizard,
    QWizardPage)

class Ui_Wizard(object):
    def setupUi(self, Wizard):
        if not Wizard.objectName():
            Wizard.setObjectName(u"Wizard")
        Wizard.resize(993, 570)
        Wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        Wizard.setOptions(QWizard.WizardOption.HaveNextButtonOnLastPage|QWizard.WizardOption.HelpButtonOnRight|QWizard.WizardOption.NoCancelButtonOnLastPage)
        Wizard.setTitleFormat(Qt.TextFormat.RichText)
        Wizard.setSubTitleFormat(Qt.TextFormat.RichText)
        self.wizardPage_init = QWizardPage()
        self.wizardPage_init.setObjectName(u"wizardPage_init")
        self.gridLayout = QGridLayout(self.wizardPage_init)
        self.gridLayout.setObjectName(u"gridLayout")
        self.textEdit_2 = QTextEdit(self.wizardPage_init)
        self.textEdit_2.setObjectName(u"textEdit_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit_2.sizePolicy().hasHeightForWidth())
        self.textEdit_2.setSizePolicy(sizePolicy)
        self.textEdit_2.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit_2.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit_2, 6, 0, 1, 4)

        self.comboBox = QComboBox(self.wizardPage_init)
        self.comboBox.setObjectName(u"comboBox")

        self.gridLayout.addWidget(self.comboBox, 3, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 3, 1, 1)

        self.label = QLabel(self.wizardPage_init)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label, 3, 1, 1, 1)

        self.pushButton_launch = QPushButton(self.wizardPage_init)
        self.pushButton_launch.setObjectName(u"pushButton_launch")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_launch.sizePolicy().hasHeightForWidth())
        self.pushButton_launch.setSizePolicy(sizePolicy1)
        self.pushButton_launch.setFlat(False)

        self.gridLayout.addWidget(self.pushButton_launch, 1, 1, 1, 2)

        self.checkBox_openSampleFemprj = QCheckBox(self.wizardPage_init)
        self.checkBox_openSampleFemprj.setObjectName(u"checkBox_openSampleFemprj")

        self.gridLayout.addWidget(self.checkBox_openSampleFemprj, 2, 1, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 0, 1, 1, 2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 5, 1, 1, 2)

        self.label_connectionState = QLabel(self.wizardPage_init)
        self.label_connectionState.setObjectName(u"label_connectionState")
        self.label_connectionState.setMinimumSize(QSize(0, 40))
        self.label_connectionState.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_connectionState, 4, 1, 1, 2)

        Wizard.addPage(self.wizardPage_init)

        self.retranslateUi(Wizard)

        QMetaObject.connectSlotsByName(Wizard)
    # setupUi

    def retranslateUi(self, Wizard):
        Wizard.setWindowTitle(QCoreApplication.translate("Wizard", u"pyfemtet.opt Script Builder", None))
        self.textEdit_2.setMarkdown(QCoreApplication.translate("Wizard", u"\u3053\u306e\u30d7\u30ed\u30b0\u30e9\u30e0\u3067\u306f\u3001**\u6700\u9069\u5316\u3092\u884c\u3046\u305f\u3081\u306e\u30b9\u30af\u30ea\u30d7\u30c8\u3092\u4f5c\u6210**\u3057\u307e\u3059\u3002\n"
"\u6700\u521d\u306b\u3001Femtet \u306b\u63a5\u7d9a\u3057\u3066\u6700\u9069\u5316\u3092\u884c\u3046\u89e3\u6790\u30e2\u30c7\u30eb\u3092\u6c7a\u3081\u307e\u3059\u3002\n"
"\u30dc\u30bf\u30f3\u3092\u62bc\u3059\u3068\n"
"Fetmet \u3068\u306e\u81ea\u52d5\u63a5\u7d9a\u304c\u59cb\u307e\u308a\u307e\u3059\u3002\n"
"\n"
"", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("Wizard", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u3053\u306e\u30d7\u30ed\u30b0\u30e9\u30e0\u3067\u306f\u3001<span style=\" font-weight:700;\">\u6700\u9069\u5316\u3092\u884c\u3046\u305f\u3081\u306e\u30b9\u30af\u30ea\u30d7\u30c8\u3092\u4f5c\u6210</span>\u3057\u307e\u3059\u3002<br />\u6700\u521d\u306b\u3001Femtet \u306b\u63a5\u7d9a\u3057\u3066\u6700\u9069\u5316\u3092\u884c\u3046\u89e3\u6790\u30e2\u30c7\u30eb\u3092\u6c7a\u3081\u307e\u3059\u3002<br "
                        "/>\u30dc\u30bf\u30f3\u3092\u62bc\u3059\u3068 Fetmet \u3068\u306e\u81ea\u52d5\u63a5\u7d9a\u304c\u59cb\u307e\u308a\u307e\u3059\u3002</p></body></html>", None))
        self.label.setText(QCoreApplication.translate("Wizard", u"CAD \u9023\u643a", None))
#if QT_CONFIG(accessibility)
        self.pushButton_launch.setAccessibleName(QCoreApplication.translate("Wizard", u"Connect to Femtet", None))
#endif // QT_CONFIG(accessibility)
        self.pushButton_launch.setText(QCoreApplication.translate("Wizard", u"Femtet \u306b\u63a5\u7d9a", None))
        self.checkBox_openSampleFemprj.setText(QCoreApplication.translate("Wizard", u"\u63a5\u7d9a\u6642\u306b\u30b5\u30f3\u30d7\u30eb\u30d5\u30a1\u30a4\u30eb\u3092\u958b\u304f", None))
#if QT_CONFIG(accessibility)
        self.label_connectionState.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.label_connectionState.setText(QCoreApplication.translate("Wizard", u"<html><head/><body><p><span style='color:#FF0000'>\u63a5\u7d9a\u3055\u308c\u3066\u3044\u307e\u305b\u3093\u3002</span></p></body></html>", None))
    # retranslateUi

