import sys
from PySide6.QtWidgets import QApplication, QTableView, QCheckBox, QWidget, QVBoxLayout, QAbstractItemView
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem


import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QStandardItemModel, QStandardItem


from dummy_femtet import DummyFemtet


_femtet = DummyFemtet()


class MyTableModel(QAbstractTableModel):

    def __init__(self, parent, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = None
        self._initModel()
        self.header = header  # checkbox, expression, init, lb, ub
        self.change_flag = True

    def _initModel(self):
        prm_names = _femtet.GetVariableNames()
        tmp = []
        for prm_name in prm_names:
            expression = _femtet.GetVariableExpression(prm_name)
            init = _femtet.GetVariableValue(prm_name)
            lb = 0; ub = 1
            tmp.append([QCheckBox(""), expression, init, lb, ub])
        self.mylist = tmp
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid():
            return None

        if index.column() == 0:
            value = self.mylist[index.row()][index.column()].text()
        else:
            value = self.mylist[index.row()][index.column()]

        if role == Qt.EditRole:
            return value
        elif role == Qt.DisplayRole:
            return value
        elif role == Qt.CheckStateRole:
            if index.column() == 0:
                if self.mylist[index.row()][index.column()].isChecked():
                    return Qt.Checked
                else:
                    return Qt.Unchecked

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def flags(self, index):
        if not index.isValid():
            return None
        # print(">>> flags() index.column() = ", index.column())
        if index.column() == 0:
            # return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsUserCheckable
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        # print(">>> setData() role = ", role)
        # print(">>> setData() index.column() = ", index.column())
        # print(">>> setData() value = ", value)
        if role == Qt.CheckStateRole and index.column() == 0:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
            if value == Qt.Checked:
                self.mylist[index.row()][index.column()].setChecked(True)
                self.mylist[index.row()][index.column()].setText("开")
                # if studentInfos.size() > index.row():
                #     emit StudentInfoIsChecked(studentInfos[index.row()])
            else:
                self.mylist[index.row()][index.column()].setChecked(False)
                self.mylist[index.row()][index.column()].setText("")
        else:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
        # self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        print(">>> setData() index.row = ", index.row())
        print(">>> setData() index.column = ", index.column())
        self.dataChanged.emit(index, index)
        return True
