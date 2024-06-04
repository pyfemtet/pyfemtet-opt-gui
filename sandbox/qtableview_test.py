import sys
from PySide6.QtWidgets import QApplication, QTableView, QCheckBox, QWidget, QVBoxLayout, QAbstractItemView
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem


import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem


from my_table_model import MyTableModel


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QTableView Example")

        # table_model = QStandardItemModel(4, 3)
        table_model = MyTableModel(self, header=["use", "name", "expression", "init", "lb", "ub"])
        # table_model.setHorizontalHeaderLabels(["use", "name", "expression", "init", "lb", "ub"])


        table_view = QTableView()

        table_view.setModel(table_model)

        self.setCentralWidget(table_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
