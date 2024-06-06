# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wizardTNlFuj.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QHeaderView, QLabel,
    QPlainTextEdit, QPushButton, QSizePolicy, QTableView,
    QTextEdit, QWidget, QWizard, QWizardPage)

class Ui_Wizard(object):
    def setupUi(self, Wizard):
        if not Wizard.objectName():
            Wizard.setObjectName(u"Wizard")
        Wizard.resize(684, 422)
        Wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        Wizard.setOptions(QWizard.WizardOption.HelpButtonOnRight)
        self.wizardPage1_launch = QWizardPage()
        self.wizardPage1_launch.setObjectName(u"wizardPage1_launch")
        self.pushButton_launch = QPushButton(self.wizardPage1_launch)
        self.pushButton_launch.setObjectName(u"pushButton_launch")
        self.pushButton_launch.setGeometry(QRect(290, 170, 75, 24))
        Wizard.addPage(self.wizardPage1_launch)
        self.wizardPage2_model = QWizardPage()
        self.wizardPage2_model.setObjectName(u"wizardPage2_model")
        self.pushButton_load = QPushButton(self.wizardPage2_model)
        self.pushButton_load.setObjectName(u"pushButton_load")
        self.pushButton_load.setGeometry(QRect(100, 180, 75, 24))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoDown))
        self.pushButton_load.setIcon(icon)
        self.label_project = QLabel(self.wizardPage2_model)
        self.label_project.setObjectName(u"label_project")
        self.label_project.setGeometry(QRect(210, 150, 49, 16))
        self.label_model = QLabel(self.wizardPage2_model)
        self.label_model.setObjectName(u"label_model")
        self.label_model.setGeometry(QRect(210, 220, 49, 16))
        self.plainTextEdit_prj = QPlainTextEdit(self.wizardPage2_model)
        self.plainTextEdit_prj.setObjectName(u"plainTextEdit_prj")
        self.plainTextEdit_prj.setGeometry(QRect(260, 130, 311, 51))
        self.plainTextEdit_prj.setReadOnly(True)
        self.plainTextEdit_model = QPlainTextEdit(self.wizardPage2_model)
        self.plainTextEdit_model.setObjectName(u"plainTextEdit_model")
        self.plainTextEdit_model.setGeometry(QRect(260, 210, 311, 41))
        self.textEdit = QTextEdit(self.wizardPage2_model)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(110, 280, 451, 81))
        self.textEdit.setReadOnly(True)
        Wizard.addPage(self.wizardPage2_model)
        self.wizardPage3_param = QWizardPage()
        self.wizardPage3_param.setObjectName(u"wizardPage3_param")
        self.pushButton_load_prm = QPushButton(self.wizardPage3_param)
        self.pushButton_load_prm.setObjectName(u"pushButton_load_prm")
        self.pushButton_load_prm.setGeometry(QRect(9, 85, 75, 24))
        self.pushButton_load_prm.setIcon(icon)
        self.tableView_prm = QTableView(self.wizardPage3_param)
        self.tableView_prm.setObjectName(u"tableView_prm")
        self.tableView_prm.setGeometry(QRect(90, 9, 585, 291))
        self.tableView_prm.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.textEdit_2 = QTextEdit(self.wizardPage3_param)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(154, 328, 331, 41))
        Wizard.addPage(self.wizardPage3_param)
        self.wizardPage4_obj = QWizardPage()
        self.wizardPage4_obj.setObjectName(u"wizardPage4_obj")
        self.textEdit_3 = QTextEdit(self.wizardPage4_obj)
        self.textEdit_3.setObjectName(u"textEdit_3")
        self.textEdit_3.setGeometry(QRect(145, 309, 421, 51))
        self.textEdit_3.setReadOnly(True)
        self.tableView_obj = QTableView(self.wizardPage4_obj)
        self.tableView_obj.setObjectName(u"tableView_obj")
        self.tableView_obj.setGeometry(QRect(81, 0, 585, 291))
        self.pushButton_load_obj = QPushButton(self.wizardPage4_obj)
        self.pushButton_load_obj.setObjectName(u"pushButton_load_obj")
        self.pushButton_load_obj.setGeometry(QRect(0, 76, 75, 24))
        self.pushButton_load_obj.setIcon(icon)
        Wizard.addPage(self.wizardPage4_obj)
        self.wizardPage9_verify = QWizardPage()
        self.wizardPage9_verify.setObjectName(u"wizardPage9_verify")
        self.textEdit_4 = QTextEdit(self.wizardPage9_verify)
        self.textEdit_4.setObjectName(u"textEdit_4")
        self.textEdit_4.setGeometry(QRect(150, 270, 421, 51))
        self.textEdit_4.setReadOnly(True)
        Wizard.addPage(self.wizardPage9_verify)
#if QT_CONFIG(shortcut)
        self.label_project.setBuddy(self.plainTextEdit_prj)
        self.label_model.setBuddy(self.plainTextEdit_model)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(Wizard)
        self.pushButton_launch.clicked.connect(Wizard.connect_process)
        self.pushButton_load.clicked.connect(Wizard.load_model)
        self.pushButton_load_prm.clicked.connect(Wizard.load_prm)
        self.pushButton_load_obj.clicked.connect(Wizard.load_obj)

        QMetaObject.connectSlotsByName(Wizard)
    # setupUi

    def retranslateUi(self, Wizard):
        Wizard.setWindowTitle(QCoreApplication.translate("Wizard", u"Wizard", None))
        self.pushButton_launch.setText(QCoreApplication.translate("Wizard", u"Connect", None))
        self.pushButton_load.setText(QCoreApplication.translate("Wizard", u"Load", None))
        self.label_project.setText(QCoreApplication.translate("Wizard", u".femprj", None))
        self.label_model.setText(QCoreApplication.translate("Wizard", u"model", None))
        self.plainTextEdit_prj.setPlainText(QCoreApplication.translate("Wizard", u"<.femprj path>", None))
        self.plainTextEdit_model.setPlainText(QCoreApplication.translate("Wizard", u"<analysis model name>", None))
        self.textEdit.setMarkdown(QCoreApplication.translate("Wizard", u".femprj \u30d5\u30a1\u30a4\u30eb\u3092\u958b\u3044\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"\u76ee\u7684\u306e\u89e3\u6790\u30e2\u30c7\u30eb\u3092\u958b\u304d\u3001Load \u3092\u62bc\u3057\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"", None))
        self.textEdit.setHtml(QCoreApplication.translate("Wizard", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">.femprj \u30d5\u30a1\u30a4\u30eb\u3092\u958b\u3044\u3066\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u76ee\u7684\u306e\u89e3\u6790\u30e2\u30c7\u30eb\u3092\u958b\u304d\u3001Load \u3092\u62bc\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p></body></html>", None))
        self.pushButton_load_prm.setText(QCoreApplication.translate("Wizard", u"Load", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("Wizard", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u6700\u9069\u5316\u3059\u308b\u5909\u6570\u3092\u9078\u3093\u3067\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u521d\u671f\u5024\u3001\u4e0a\u9650\u3001\u4e0b\u9650\u3092\u6307\u5b9a\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p></body></html>", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("Wizard", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u6700\u9069\u5316\u3059\u308b\u76ee\u7684\u95a2\u6570\u3092\u9078\u3093\u3067\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u203b Femtet \u306e\u30d1\u30e9\u30e1\u30c8\u30ea\u30c3\u30af\u89e3\u6790\u30c0\u30a4\u30a2\u30ed\u30b0\u3067\u76ee\u7684\u95a2\u6570\u3092\u5b9a\u7fa9\u3057\u3066"
                        "\u304f\u3060\u3055\u3044\u3002</p></body></html>", None))
        self.pushButton_load_obj.setText(QCoreApplication.translate("Wizard", u"Load", None))
        self.textEdit_4.setHtml(QCoreApplication.translate("Wizard", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u3088\u308d\u3057\u3044\u3067\u3059\u304b\uff1f</p></body></html>", None))
    # retranslateUi

