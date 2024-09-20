# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cns_inputuHXdBQ.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QAbstractScrollArea, QApplication,
    QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPlainTextEdit,
    QPushButton, QSizePolicy, QTableView, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(550, 271)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_prmOnCns = QLabel(Dialog)
        self.label_prmOnCns.setObjectName(u"label_prmOnCns")

        self.gridLayout.addWidget(self.label_prmOnCns, 0, 0, 1, 1)

        self.lineEdit_name = QLineEdit(Dialog)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setMinimumSize(QSize(171, 0))

        self.gridLayout.addWidget(self.lineEdit_name, 0, 2, 1, 3)

        self.pushButton_loadPrmOnCns = QPushButton(Dialog)
        self.pushButton_loadPrmOnCns.setObjectName(u"pushButton_loadPrmOnCns")
        self.pushButton_loadPrmOnCns.setMaximumSize(QSize(75, 24))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoDown))
        self.pushButton_loadPrmOnCns.setIcon(icon)

        self.gridLayout.addWidget(self.pushButton_loadPrmOnCns, 1, 0, 1, 1)

        self.lineEdit_lb = QLineEdit(Dialog)
        self.lineEdit_lb.setObjectName(u"lineEdit_lb")
        self.lineEdit_lb.setMaximumSize(QSize(81, 21))

        self.gridLayout.addWidget(self.lineEdit_lb, 1, 2, 1, 1)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label, 1, 3, 1, 1)

        self.lineEdit_ub = QLineEdit(Dialog)
        self.lineEdit_ub.setObjectName(u"lineEdit_ub")
        self.lineEdit_ub.setMaximumSize(QSize(81, 21))

        self.gridLayout.addWidget(self.lineEdit_ub, 1, 4, 1, 2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMaximumSize(QSize(75, 24))

        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(Dialog)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMaximumSize(QSize(75, 24))

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(Dialog)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setMaximumSize(QSize(75, 24))

        self.horizontalLayout.addWidget(self.pushButton_3)


        self.gridLayout.addLayout(self.horizontalLayout, 4, 2, 1, 4)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 5, 5, 1, 1)

        self.pushButton_addPrmToCns = QPushButton(Dialog)
        self.pushButton_addPrmToCns.setObjectName(u"pushButton_addPrmToCns")
        self.pushButton_addPrmToCns.setMaximumSize(QSize(31, 24))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSend))
        self.pushButton_addPrmToCns.setIcon(icon1)

        self.gridLayout.addWidget(self.pushButton_addPrmToCns, 2, 1, 1, 1)

        self.tableView_prmsOnCns = QTableView(Dialog)
        self.tableView_prmsOnCns.setObjectName(u"tableView_prmsOnCns")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_prmsOnCns.sizePolicy().hasHeightForWidth())
        self.tableView_prmsOnCns.setSizePolicy(sizePolicy)
        self.tableView_prmsOnCns.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tableView_prmsOnCns.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView_prmsOnCns.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.gridLayout.addWidget(self.tableView_prmsOnCns, 2, 0, 3, 1)

        self.plainTextEdit_cnsFormula = QPlainTextEdit(Dialog)
        self.plainTextEdit_cnsFormula.setObjectName(u"plainTextEdit_cnsFormula")

        self.gridLayout.addWidget(self.plainTextEdit_cnsFormula, 2, 2, 2, 4)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.pushButton_loadPrmOnCns.clicked.connect(Dialog.update_problem)
        self.pushButton_addPrmToCns.clicked.connect(Dialog.add_prm_to_cns_formula)
        self.pushButton.clicked.connect(Dialog.add_max_to_cns_formula)
        self.pushButton_2.clicked.connect(Dialog.add_min_to_cns_formula)
        self.pushButton_3.clicked.connect(Dialog.add_mean_to_cns_formula)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_prmOnCns.setText(QCoreApplication.translate("Dialog", u"\u5909\u6570\u4e00\u89a7", None))
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u62d8\u675f\u540d\uff08\u7a7a\u6b04\u6642\u306f\u81ea\u52d5\u547d\u540d\uff09", None))
        self.pushButton_loadPrmOnCns.setText(QCoreApplication.translate("Dialog", u"Load", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_lb.setToolTip(QCoreApplication.translate("Dialog", u"\u4e0a\u9650\u3068\u4e0b\u9650\u306e\u3044\u305a\u308c\u304b\u306e\u5165\u529b\u304c\u5fc5\u9808\u3067\u3059\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_lb.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u4e0b\u9650\u3092\u5165\u529b", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"<= \u5f0f <=", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_ub.setToolTip(QCoreApplication.translate("Dialog", u"\u4e0a\u9650\u3068\u4e0b\u9650\u306e\u3044\u305a\u308c\u304b\u306e\u5165\u529b\u304c\u5fc5\u9808\u3067\u3059\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_ub.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u4e0a\u9650\u3092\u5165\u529b", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"max()", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog", u"min()", None))
        self.pushButton_3.setText(QCoreApplication.translate("Dialog", u"mean()", None))
        self.pushButton_addPrmToCns.setText("")
        self.plainTextEdit_cnsFormula.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u5f0f\u3092\u5165\u529b   \u4f8b\uff1a(a + max(b, c)) * d   \u6539\u884c\u53ef", None))
    # retranslateUi

