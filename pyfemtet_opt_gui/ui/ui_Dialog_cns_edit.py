# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Dialog_cns_editEbwvTk.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QAbstractScrollArea, QApplication,
    QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPlainTextEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTableView,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(664, 296)
        self.gridLayout_2 = QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lineEdit_name = QLineEdit(Dialog)
        self.lineEdit_name.setObjectName(u"lineEdit_name")
        self.lineEdit_name.setMinimumSize(QSize(171, 0))

        self.gridLayout_2.addWidget(self.lineEdit_name, 0, 0, 1, 1)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.pushButton_load_var = QPushButton(Dialog)
        self.pushButton_load_var.setObjectName(u"pushButton_load_var")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.GoDown))
        self.pushButton_load_var.setIcon(icon)

        self.gridLayout_3.addWidget(self.pushButton_load_var, 0, 0, 1, 1)

        self.label_prmOnCns = QLabel(Dialog)
        self.label_prmOnCns.setObjectName(u"label_prmOnCns")

        self.gridLayout_3.addWidget(self.label_prmOnCns, 0, 1, 1, 1)

        self.tableView_prmsOnCns = QTableView(Dialog)
        self.tableView_prmsOnCns.setObjectName(u"tableView_prmsOnCns")
        self.tableView_prmsOnCns.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tableView_prmsOnCns.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView_prmsOnCns.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView_prmsOnCns.verticalHeader().setVisible(False)

        self.gridLayout_3.addWidget(self.tableView_prmsOnCns, 1, 0, 1, 2)


        self.gridLayout_2.addLayout(self.gridLayout_3, 3, 0, 3, 1)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_input_mean = QPushButton(Dialog)
        self.pushButton_input_mean.setObjectName(u"pushButton_input_mean")
        self.pushButton_input_mean.setMaximumSize(QSize(75, 24))

        self.gridLayout.addWidget(self.pushButton_input_mean, 1, 2, 1, 1)

        self.pushButton_input_devide = QPushButton(Dialog)
        self.pushButton_input_devide.setObjectName(u"pushButton_input_devide")
        self.pushButton_input_devide.setMaximumSize(QSize(75, 24))

        self.gridLayout.addWidget(self.pushButton_input_devide, 3, 0, 1, 1)

        self.pushButton_input_min = QPushButton(Dialog)
        self.pushButton_input_min.setObjectName(u"pushButton_input_min")
        self.pushButton_input_min.setMaximumSize(QSize(75, 24))

        self.gridLayout.addWidget(self.pushButton_input_min, 1, 1, 1, 1)

        self.pushButton_input_max = QPushButton(Dialog)
        self.pushButton_input_max.setObjectName(u"pushButton_input_max")
        self.pushButton_input_max.setMaximumSize(QSize(75, 24))

        self.gridLayout.addWidget(self.pushButton_input_max, 1, 0, 1, 1)

        self.pushButton_input_minus = QPushButton(Dialog)
        self.pushButton_input_minus.setObjectName(u"pushButton_input_minus")
        self.pushButton_input_minus.setMaximumSize(QSize(75, 24))

        self.gridLayout.addWidget(self.pushButton_input_minus, 2, 1, 1, 1)

        self.pushButton_input_plus = QPushButton(Dialog)
        self.pushButton_input_plus.setObjectName(u"pushButton_input_plus")
        self.pushButton_input_plus.setMaximumSize(QSize(75, 24))

        self.gridLayout.addWidget(self.pushButton_input_plus, 2, 0, 1, 1)

        self.pushButton_input_var = QPushButton(Dialog)
        self.pushButton_input_var.setObjectName(u"pushButton_input_var")

        self.gridLayout.addWidget(self.pushButton_input_var, 0, 0, 1, 3)

        self.pushButton_input_multiply = QPushButton(Dialog)
        self.pushButton_input_multiply.setObjectName(u"pushButton_input_multiply")
        self.pushButton_input_multiply.setMaximumSize(QSize(75, 24))

        self.gridLayout.addWidget(self.pushButton_input_multiply, 2, 2, 1, 1)

        self.pushButton_input_comma = QPushButton(Dialog)
        self.pushButton_input_comma.setObjectName(u"pushButton_input_comma")
        self.pushButton_input_comma.setMaximumSize(QSize(75, 24))

        self.gridLayout.addWidget(self.pushButton_input_comma, 3, 1, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 3, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout_2.addWidget(self.buttonBox, 5, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_lb = QLineEdit(Dialog)
        self.lineEdit_lb.setObjectName(u"lineEdit_lb")
        self.lineEdit_lb.setMaximumSize(QSize(81, 21))

        self.horizontalLayout.addWidget(self.lineEdit_lb)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.label_4)

        self.plainTextEdit_cnsFormula = QPlainTextEdit(Dialog)
        self.plainTextEdit_cnsFormula.setObjectName(u"plainTextEdit_cnsFormula")

        self.horizontalLayout.addWidget(self.plainTextEdit_cnsFormula)

        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.label_5)

        self.lineEdit_ub = QLineEdit(Dialog)
        self.lineEdit_ub.setObjectName(u"lineEdit_ub")
        self.lineEdit_ub.setMaximumSize(QSize(81, 21))

        self.horizontalLayout.addWidget(self.lineEdit_ub)


        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 0, 1, 2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 4, 1, 1, 1)

        self.label_calc_value = QLabel(Dialog)
        self.label_calc_value.setObjectName(u"label_calc_value")

        self.gridLayout_2.addWidget(self.label_calc_value, 0, 1, 1, 1)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u62d8\u675f\u540d\uff08\u7a7a\u6b04\u6642\u306f\u81ea\u52d5\u547d\u540d\uff09", None))
        self.pushButton_load_var.setText(QCoreApplication.translate("Dialog", u"Load", None))
        self.label_prmOnCns.setText(QCoreApplication.translate("Dialog", u"\u5909\u6570\u4e00\u89a7", None))
        self.pushButton_input_mean.setText(QCoreApplication.translate("Dialog", u"Mean( )", None))
        self.pushButton_input_devide.setText(QCoreApplication.translate("Dialog", u"/", None))
        self.pushButton_input_min.setText(QCoreApplication.translate("Dialog", u"Min( )", None))
        self.pushButton_input_max.setText(QCoreApplication.translate("Dialog", u"Max( )", None))
        self.pushButton_input_minus.setText(QCoreApplication.translate("Dialog", u"-", None))
        self.pushButton_input_plus.setText(QCoreApplication.translate("Dialog", u"+", None))
        self.pushButton_input_var.setText(QCoreApplication.translate("Dialog", u"\u9078\u629e\u4e2d\u306e\u5909\u6570\u3092\u5165\u529b", None))
        self.pushButton_input_multiply.setText(QCoreApplication.translate("Dialog", u"*", None))
        self.pushButton_input_comma.setText(QCoreApplication.translate("Dialog", u",", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_lb.setToolTip(QCoreApplication.translate("Dialog", u"\u4e0a\u9650\u3068\u4e0b\u9650\u306e\u3044\u305a\u308c\u304b\u306e\u5165\u529b\u304c\u5fc5\u9808\u3067\u3059\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_lb.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.lineEdit_lb.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u4e0b\u9650\u3092\u5165\u529b", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"<=", None))
        self.plainTextEdit_cnsFormula.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u5f0f\u3092\u5165\u529b   \u4f8b\uff1a(a + Max(b, c)) * d   \u6539\u884c\u53ef", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"<=", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_ub.setToolTip(QCoreApplication.translate("Dialog", u"\u4e0a\u9650\u3068\u4e0b\u9650\u306e\u3044\u305a\u308c\u304b\u306e\u5165\u529b\u304c\u5fc5\u9808\u3067\u3059\u3002", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_ub.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u4e0a\u9650\u3092\u5165\u529b", None))
        self.label_calc_value.setText(QCoreApplication.translate("Dialog", u"\u73fe\u5728\u306e\u8a08\u7b97\u5024: ", None))
    # retranslateUi

