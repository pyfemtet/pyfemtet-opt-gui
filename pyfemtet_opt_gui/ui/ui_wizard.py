# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wizardpHxyDr.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCheckBox,
    QFormLayout, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QTableView, QTextEdit,
    QTreeView, QVBoxLayout, QWidget, QWizard,
    QWizardPage)

class Ui_Wizard(object):
    def setupUi(self, Wizard):
        if not Wizard.objectName():
            Wizard.setObjectName(u"Wizard")
        Wizard.resize(658, 445)
        Wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        Wizard.setOptions(QWizard.WizardOption.HaveNextButtonOnLastPage|QWizard.WizardOption.HelpButtonOnRight|QWizard.WizardOption.NoCancelButtonOnLastPage)
        self.wizardPage1_launch = QWizardPage()
        self.wizardPage1_launch.setObjectName(u"wizardPage1_launch")
        self.gridLayout = QGridLayout(self.wizardPage1_launch)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 0, 1, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 1, 0, 1, 1)

        self.pushButton_launch = QPushButton(self.wizardPage1_launch)
        self.pushButton_launch.setObjectName(u"pushButton_launch")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_launch.sizePolicy().hasHeightForWidth())
        self.pushButton_launch.setSizePolicy(sizePolicy)
        self.pushButton_launch.setFlat(False)

        self.gridLayout.addWidget(self.pushButton_launch, 1, 1, 1, 1)

        self.textEdit_2 = QTextEdit(self.wizardPage1_launch)
        self.textEdit_2.setObjectName(u"textEdit_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.textEdit_2.sizePolicy().hasHeightForWidth())
        self.textEdit_2.setSizePolicy(sizePolicy1)
        self.textEdit_2.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit_2.setReadOnly(True)

        self.gridLayout.addWidget(self.textEdit_2, 5, 0, 1, 3)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 3, 1, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_4, 1, 2, 1, 1)

        self.label_connectionState = QLabel(self.wizardPage1_launch)
        self.label_connectionState.setObjectName(u"label_connectionState")
        self.label_connectionState.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_connectionState, 2, 1, 1, 1)

        Wizard.addPage(self.wizardPage1_launch)
        self.wizardPage2_model = QWizardPage()
        self.wizardPage2_model.setObjectName(u"wizardPage2_model")
        self.verticalLayout = QVBoxLayout(self.wizardPage2_model)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_load_femprj = QPushButton(self.wizardPage2_model)
        self.pushButton_load_femprj.setObjectName(u"pushButton_load_femprj")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoDown))
        self.pushButton_load_femprj.setIcon(icon)

        self.horizontalLayout.addWidget(self.pushButton_load_femprj)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_project = QLabel(self.wizardPage2_model)
        self.label_project.setObjectName(u"label_project")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_project)

        self.label_model = QLabel(self.wizardPage2_model)
        self.label_model.setObjectName(u"label_model")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_model)

        self.plainTextEdit_prj = QPlainTextEdit(self.wizardPage2_model)
        self.plainTextEdit_prj.setObjectName(u"plainTextEdit_prj")
        sizePolicy.setHeightForWidth(self.plainTextEdit_prj.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_prj.setSizePolicy(sizePolicy)
        self.plainTextEdit_prj.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.plainTextEdit_prj.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.plainTextEdit_prj)

        self.plainTextEdit_model = QPlainTextEdit(self.wizardPage2_model)
        self.plainTextEdit_model.setObjectName(u"plainTextEdit_model")
        sizePolicy1.setHeightForWidth(self.plainTextEdit_model.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_model.setSizePolicy(sizePolicy1)
        self.plainTextEdit_model.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.plainTextEdit_model.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.plainTextEdit_model.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.plainTextEdit_model.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.plainTextEdit_model.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.plainTextEdit_model)


        self.horizontalLayout.addLayout(self.formLayout)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.textEdit = QTextEdit(self.wizardPage2_model)
        self.textEdit.setObjectName(u"textEdit")
        sizePolicy1.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy1)
        self.textEdit.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit.setReadOnly(True)

        self.verticalLayout.addWidget(self.textEdit)

        Wizard.addPage(self.wizardPage2_model)
        self.wizardPage3_param = QWizardPage()
        self.wizardPage3_param.setObjectName(u"wizardPage3_param")
        self.verticalLayout_2 = QVBoxLayout(self.wizardPage3_param)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_load_prm = QPushButton(self.wizardPage3_param)
        self.pushButton_load_prm.setObjectName(u"pushButton_load_prm")
        self.pushButton_load_prm.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.pushButton_load_prm)

        self.tableView_prm = QTableView(self.wizardPage3_param)
        self.tableView_prm.setObjectName(u"tableView_prm")
        sizePolicy.setHeightForWidth(self.tableView_prm.sizePolicy().hasHeightForWidth())
        self.tableView_prm.setSizePolicy(sizePolicy)
        self.tableView_prm.setFrameShape(QFrame.Shape.Panel)
        self.tableView_prm.setFrameShadow(QFrame.Shadow.Sunken)
        self.tableView_prm.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.tableView_prm.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        self.tableView_prm.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.tableView_prm.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableView_prm.horizontalHeader().setCascadingSectionResizes(True)
        self.tableView_prm.horizontalHeader().setHighlightSections(False)
        self.tableView_prm.horizontalHeader().setStretchLastSection(True)
        self.tableView_prm.verticalHeader().setVisible(False)

        self.horizontalLayout_2.addWidget(self.tableView_prm)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.textEdit_5 = QTextEdit(self.wizardPage3_param)
        self.textEdit_5.setObjectName(u"textEdit_5")
        sizePolicy1.setHeightForWidth(self.textEdit_5.sizePolicy().hasHeightForWidth())
        self.textEdit_5.setSizePolicy(sizePolicy1)
        self.textEdit_5.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit_5.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.textEdit_5)

        Wizard.addPage(self.wizardPage3_param)
        self.wizardPage4_obj = QWizardPage()
        self.wizardPage4_obj.setObjectName(u"wizardPage4_obj")
        self.verticalLayout_3 = QVBoxLayout(self.wizardPage4_obj)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButton_load_obj = QPushButton(self.wizardPage4_obj)
        self.pushButton_load_obj.setObjectName(u"pushButton_load_obj")
        self.pushButton_load_obj.setIcon(icon)

        self.horizontalLayout_3.addWidget(self.pushButton_load_obj)

        self.tableView_obj = QTableView(self.wizardPage4_obj)
        self.tableView_obj.setObjectName(u"tableView_obj")
        self.tableView_obj.setFrameShape(QFrame.Shape.Panel)
        self.tableView_obj.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        self.tableView_obj.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.tableView_obj.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tableView_obj.horizontalHeader().setCascadingSectionResizes(True)
        self.tableView_obj.horizontalHeader().setHighlightSections(False)
        self.tableView_obj.horizontalHeader().setStretchLastSection(True)
        self.tableView_obj.verticalHeader().setVisible(False)

        self.horizontalLayout_3.addWidget(self.tableView_obj)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.textEdit_3 = QTextEdit(self.wizardPage4_obj)
        self.textEdit_3.setObjectName(u"textEdit_3")
        sizePolicy1.setHeightForWidth(self.textEdit_3.sizePolicy().hasHeightForWidth())
        self.textEdit_3.setSizePolicy(sizePolicy1)
        self.textEdit_3.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit_3.setReadOnly(True)

        self.verticalLayout_3.addWidget(self.textEdit_3)

        Wizard.addPage(self.wizardPage4_obj)
        self.wizardPage6_run = QWizardPage()
        self.wizardPage6_run.setObjectName(u"wizardPage6_run")
        self.verticalLayout_5 = QVBoxLayout(self.wizardPage6_run)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.tableView_run = QTableView(self.wizardPage6_run)
        self.tableView_run.setObjectName(u"tableView_run")
        self.tableView_run.setFrameShape(QFrame.Shape.Panel)
        self.tableView_run.setWordWrap(False)
        self.tableView_run.horizontalHeader().setCascadingSectionResizes(True)
        self.tableView_run.horizontalHeader().setHighlightSections(False)
        self.tableView_run.horizontalHeader().setStretchLastSection(True)
        self.tableView_run.verticalHeader().setVisible(False)

        self.horizontalLayout_4.addWidget(self.tableView_run)


        self.verticalLayout_5.addLayout(self.horizontalLayout_4)

        self.textEdit_6 = QTextEdit(self.wizardPage6_run)
        self.textEdit_6.setObjectName(u"textEdit_6")
        sizePolicy1.setHeightForWidth(self.textEdit_6.sizePolicy().hasHeightForWidth())
        self.textEdit_6.setSizePolicy(sizePolicy1)
        self.textEdit_6.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_6.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit_6.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit_6.setReadOnly(True)

        self.verticalLayout_5.addWidget(self.textEdit_6)

        Wizard.addPage(self.wizardPage6_run)
        self.wizardPage9_verify = QWizardPage()
        self.wizardPage9_verify.setObjectName(u"wizardPage9_verify")
        self.gridLayout_2 = QGridLayout(self.wizardPage9_verify)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.checkBox_save_with_run = QCheckBox(self.wizardPage9_verify)
        self.checkBox_save_with_run.setObjectName(u"checkBox_save_with_run")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.checkBox_save_with_run.sizePolicy().hasHeightForWidth())
        self.checkBox_save_with_run.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.checkBox_save_with_run, 4, 1, 1, 1)

        self.pushButton_save_script = QPushButton(self.wizardPage9_verify)
        self.pushButton_save_script.setObjectName(u"pushButton_save_script")

        self.gridLayout_2.addWidget(self.pushButton_save_script, 4, 0, 1, 1)

        self.textEdit_4 = QTextEdit(self.wizardPage9_verify)
        self.textEdit_4.setObjectName(u"textEdit_4")
        sizePolicy1.setHeightForWidth(self.textEdit_4.sizePolicy().hasHeightForWidth())
        self.textEdit_4.setSizePolicy(sizePolicy1)
        self.textEdit_4.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.textEdit_4.setReadOnly(True)

        self.gridLayout_2.addWidget(self.textEdit_4, 1, 0, 1, 2)

        self.treeView = QTreeView(self.wizardPage9_verify)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setFrameShape(QFrame.Shape.Panel)
        self.treeView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.treeView.setWordWrap(False)
        self.treeView.setHeaderHidden(False)

        self.gridLayout_2.addWidget(self.treeView, 0, 0, 1, 2)

        Wizard.addPage(self.wizardPage9_verify)
#if QT_CONFIG(shortcut)
        self.label_project.setBuddy(self.plainTextEdit_prj)
        self.label_model.setBuddy(self.plainTextEdit_model)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(Wizard)
        self.pushButton_launch.clicked.connect(Wizard.connect_process)
        self.pushButton_load_prm.clicked.connect(Wizard.update_problem)
        self.pushButton_load_obj.clicked.connect(Wizard.update_problem)
        self.pushButton_save_script.clicked.connect(Wizard.build_script)
        self.pushButton_load_femprj.clicked.connect(Wizard.update_problem)
        Wizard.currentIdChanged.connect(self.treeView.expandAll)
        self.checkBox_save_with_run.checkStateChanged.connect(Wizard.check_save_button_should_enabled)

        QMetaObject.connectSlotsByName(Wizard)
    # setupUi

    def retranslateUi(self, Wizard):
        Wizard.setWindowTitle(QCoreApplication.translate("Wizard", u"Wizard", None))
#if QT_CONFIG(accessibility)
        self.pushButton_launch.setAccessibleName(QCoreApplication.translate("Wizard", u"Connect to Femtet", None))
#endif // QT_CONFIG(accessibility)
        self.pushButton_launch.setText(QCoreApplication.translate("Wizard", u"Connect to Femtet", None))
        self.textEdit_2.setMarkdown(QCoreApplication.translate("Wizard", u"\u6700\u9069\u5316\u3092\u884c\u3046\u305f\u3081\u306e\u30b9\u30af\u30ea\u30d7\u30c8\u306e\u8a2d\u5b9a\u3092\u884c\u3044\u307e\u3059\u3002\n"
"\u6700\u521d\u306b\u3001Femtet \u306b\u63a5\u7d9a\u3057\u3066\u6700\u9069\u5316\u3092\u884c\u3046\u89e3\u6790\u30e2\u30c7\u30eb\u3092\u6c7a\u3081\u307e\u3059\u3002\n"
"\u30dc\u30bf\u30f3\u3092\u62bc\u3059\u3068 Fetmet\n"
"\u3068\u306e\u81ea\u52d5\u63a5\u7d9a\u304c\u59cb\u307e\u308a\u307e\u3059\u3002\n"
"\n"
"", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("Wizard", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u6700\u9069\u5316\u3092\u884c\u3046\u305f\u3081\u306e\u30b9\u30af\u30ea\u30d7\u30c8\u306e\u8a2d\u5b9a\u3092\u884c\u3044\u307e\u3059\u3002<br />\u6700\u521d\u306b\u3001Femtet \u306b\u63a5\u7d9a\u3057\u3066\u6700\u9069\u5316\u3092\u884c\u3046\u89e3\u6790\u30e2\u30c7\u30eb\u3092\u6c7a\u3081\u307e\u3059\u3002<br />\u30dc\u30bf\u30f3\u3092\u62bc\u3059\u3068 Fetmet \u3068\u306e\u81ea\u52d5\u63a5\u7d9a\u304c"
                        "\u59cb\u307e\u308a\u307e\u3059\u3002</p></body></html>", None))
#if QT_CONFIG(accessibility)
        self.label_connectionState.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.label_connectionState.setText(QCoreApplication.translate("Wizard", u"<html><head/><body><p><span style='color:#FF0000'>\u63a5\u7d9a\u3055\u308c\u3066\u3044\u307e\u305b\u3093\u3002</span></p></body></html>", None))
        self.wizardPage2_model.setSubTitle(QCoreApplication.translate("Wizard", u"<table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0 width=\"83%\"  style='width:83.32%;border-collapse:collapse'>  <tr>   <td width=\"19%\" valign=top style='width:19.98%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><b><i><span style='color:#0987D5'>\u30e2\u30c7\u30eb\u6307\u5b9a</span></i></b></p>   </td>   <td width=\"20%\" valign=top style='width:20.0%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u5909\u6570\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.02%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u76ee\u7684\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.02%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u5b9f\u884c\u8a2d\u5b9a</span></p>   </td>   <td width=\"19%\" valign=top style='width:19.96%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u78ba\u8a8d</span></p>   </td>  </tr> </table>", None))
        self.pushButton_load_femprj.setText(QCoreApplication.translate("Wizard", u"Load", None))
        self.label_project.setText(QCoreApplication.translate("Wizard", u".femprj", None))
        self.label_model.setText(QCoreApplication.translate("Wizard", u"model", None))
        self.plainTextEdit_prj.setPlainText("")
        self.plainTextEdit_prj.setPlaceholderText(QCoreApplication.translate("Wizard", u"<.femprj path>", None))
        self.plainTextEdit_model.setPlainText("")
        self.plainTextEdit_model.setPlaceholderText(QCoreApplication.translate("Wizard", u"<analysis model name>", None))
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
        self.wizardPage3_param.setSubTitle(QCoreApplication.translate("Wizard", u"<table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0 width=\"83%\"  style='width:83.32%;border-collapse:collapse'>  <tr>   <td width=\"19%\" valign=top style='width:19.98%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u30e2\u30c7\u30eb\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.0%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><b><i><span style='color:#0987D5'>\u5909\u6570\u6307\u5b9a</span></i></b></p>   </td>   <td width=\"20%\" valign=top style='width:20.02%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u76ee\u7684\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.02%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u5b9f\u884c\u8a2d\u5b9a</span></p>   </td>   <td width=\"19%\" valign=top style='width:19.96%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u78ba\u8a8d</span></p>   </td>  </tr> </table>", None))
        self.pushButton_load_prm.setText(QCoreApplication.translate("Wizard", u"Load", None))
        self.textEdit_5.setMarkdown(QCoreApplication.translate("Wizard", u"\u6700\u9069\u5316\u306e\u969b\u306b\u8abf\u6574\u3059\u308b\u30d1\u30e9\u30e1\u30fc\u30bf\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"\u521d\u671f\u5024\u3001\u4e0b\u9650\u3001\u4e0a\u9650\u3092\u8a2d\u5b9a\u30fb\u78ba\u8a8d\u3057\u3066\u304f\u3060\u3055\u3044\u3002\n"
"\n"
"", None))
        self.textEdit_5.setHtml(QCoreApplication.translate("Wizard", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u6700\u9069\u5316\u306e\u969b\u306b\u8abf\u6574\u3059\u308b\u30d1\u30e9\u30e1\u30fc\u30bf\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:6px; margin-bottom:6px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u521d\u671f\u5024\u3001\u4e0b\u9650\u3001\u4e0a\u9650\u3092\u8a2d\u5b9a\u30fb\u78ba\u8a8d\u3057\u3066\u304f\u3060\u3055"
                        "\u3044\u3002</p></body></html>", None))
        self.wizardPage4_obj.setSubTitle(QCoreApplication.translate("Wizard", u"<table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0 width=\"83%\"  style='width:83.32%;border-collapse:collapse'>  <tr>   <td width=\"19%\" valign=top style='width:19.98%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u30e2\u30c7\u30eb\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.0%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u5909\u6570\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.02%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><b><i><span style='color:#0987D5'>\u76ee\u7684\u6307\u5b9a</span></i></b></p>   </td>   <td width=\"20%\" valign=top style='width:20.02%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u5b9f\u884c\u8a2d\u5b9a</span></p>   </td>   <td width=\"19%\" valign=top style='width:19.96%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u78ba\u8a8d</span></p>   </td>  </tr> </table>", None))
        self.pushButton_load_obj.setText(QCoreApplication.translate("Wizard", u"Load", None))
        self.textEdit_3.setHtml(QCoreApplication.translate("Wizard", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u6700\u9069\u5316\u3059\u308b\u76ee\u7684\u95a2\u6570\u3092\u9078\u3093\u3067\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u203b Femtet \u306e\u30d1\u30e9\u30e1\u30c8\u30ea\u30c3\u30af\u89e3\u6790\u30c0\u30a4\u30a2\u30ed\u30b0\u3067\u76ee\u7684\u95a2\u6570\u3092\u5b9a\u7fa9\u3057\u3066"
                        "\u304f\u3060\u3055\u3044\u3002</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u203b \u30d7\u30ed\u30b8\u30a7\u30af\u30c8\u306b\u65e2\u5b58\u306e\u30d1\u30e9\u30e1\u30c8\u30ea\u30c3\u30af\u89e3\u6790\u8a2d\u5b9a\u304c\u3042\u308b\u5834\u5408\u3001\u6700\u9069\u5316\u5b9f\u884c\u524d\u306b\u30b9\u30a4\u30fc\u30d7\u30c6\u30fc\u30d6\u30eb\u3092\u524a\u9664\u3057\u3066\u304f\u3060\u3055\u3044\u3002</p></body></html>", None))
        self.wizardPage6_run.setSubTitle(QCoreApplication.translate("Wizard", u"<table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0 width=\"83%\"  style='width:83.32%;border-collapse:collapse'>  <tr>   <td width=\"19%\" valign=top style='width:19.98%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u30e2\u30c7\u30eb\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.0%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u5909\u6570\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.02%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u76ee\u7684\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.02%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><b><i><span style='color:#0987D5'>\u5b9f\u884c\u8a2d\u5b9a</span></i></b></p>   </td>   <td width=\"19%\" valign=top style='width:19.96%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u78ba\u8a8d</span></p>   </td>  </tr> </table>"
                        " ", None))
        self.textEdit_6.setHtml(QCoreApplication.translate("Wizard", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u5b9f\u884c\u6642\u306e\u8a2d\u5b9a\u3092\u884c\u3063\u3066\u304f\u3060\u3055\u3044\u3002</p></body></html>", None))
        self.wizardPage9_verify.setSubTitle(QCoreApplication.translate("Wizard", u"<table class=MsoNormalTable border=0 cellspacing=0 cellpadding=0 width=\"83%\"  style='width:83.32%;border-collapse:collapse'>  <tr>   <td width=\"19%\" valign=top style='width:19.98%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u30e2\u30c7\u30eb\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.0%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u5909\u6570\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.02%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u76ee\u7684\u6307\u5b9a</span></p>   </td>   <td width=\"20%\" valign=top style='width:20.02%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><span style='color:#7F7F7F'>\u5b9f\u884c\u8a2d\u5b9a</span></p>   </td>   <td width=\"19%\" valign=top style='width:19.96%;padding:0mm 5.4pt 0mm 5.4pt'>   <p class=MsoNormal><b><i><span style='color:#0987D5'>\u78ba\u8a8d</span></i></b></p>   </td>  </tr> </table>"
                        " ", None))
        self.checkBox_save_with_run.setText(QCoreApplication.translate("Wizard", u"\u30b9\u30af\u30ea\u30d7\u30c8\u306e\u4fdd\u5b58\u5f8c\u5b9f\u884c\u3059\u308b", None))
#if QT_CONFIG(accessibility)
        self.pushButton_save_script.setAccessibleName(QCoreApplication.translate("Wizard", u"\u30b9\u30af\u30ea\u30d7\u30c8\u3092\u4fdd\u5b58\u3059\u308b", None))
#endif // QT_CONFIG(accessibility)
        self.pushButton_save_script.setText(QCoreApplication.translate("Wizard", u"\u30b9\u30af\u30ea\u30d7\u30c8\u3092\u4fdd\u5b58\u3059\u308b", None))
        self.textEdit_4.setHtml(QCoreApplication.translate("Wizard", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Yu Gothic UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\u3088\u308d\u3057\u3044\u3067\u3059\u304b\uff1f</p></body></html>", None))
    # retranslateUi

