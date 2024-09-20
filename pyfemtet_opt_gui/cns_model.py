from PySide6.QtCore import Qt, QPoint, QModelIndex
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox

import pyfemtet_opt_gui._p as _p

from pyfemtet_opt_gui.item_as_model import (
    MyStandardItemAsTableModel,
    _isnumeric,
    MyStandardItemAsTableModelWithoutHeader
)
from pyfemtet_opt_gui.prm_model import PrmModel

from pyfemtet_opt_gui.ui.return_code import ReturnCode, should_stop


class CnsModel(MyStandardItemAsTableModel):
    """A table for determining whether to use Femtet variables in optimization.

    use        | name       | formula    | lb             | ub             | strict     |
    -------------------------------------------------------------------------------------
    checkbox   | str        | str        | float or empty | float or empty | checkbox   |
    uneditable |            | uneditable | uneditable     | uneditable     | uneditable |

    # if checkbox is false, disable the row (excluding use column).
    # lb, ub, formula is uneditable (because dialog has checking functions)
    # use, strict is uneditable and checkable

    """

    USE = 'use'
    NAME = 'name'
    FORMULA = 'formula'
    LB = 'lower bound'
    UB = 'upper bound'
    STRICT = 'strict'

    HEADER = [USE, NAME, STRICT, LB, UB, FORMULA]

    AUTOMATIC_CNS_NAME = '（自動決定）'

    def __init__(self, table_item: QStandardItem, root: QStandardItem, parent=None):
        super().__init__(table_item, root, parent)
        self.initialize_table()

    def initialize_table(self):
        # initialize table
        table: QStandardItem = self._item
        table.clearData()
        table.setText(self._category)
        table.setRowCount(0)
        table.setColumnCount(len(self.HEADER))
        self.set_header(self.HEADER)
        self._root.setColumnCount(max(self._root.columnCount(), self._item.columnCount()))

    def flags(self, index):
        if not index.isValid(): return super().flags(index)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        # if checkbox is false, disable the row (excluding use column).
        use_col = self.get_col_from_name(self.USE)
        use_item = self.get_item(row, use_col)
        if use_item.checkState() == Qt.CheckState.Unchecked:
            if col_name != self.USE:
                return ~Qt.ItemFlag.ItemIsEnabled

        # lb, ub, formula is uneditable
        if col_name in [self.FORMULA, self.LB, self.UB]:
            flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            return flags

        # use / strict is uneditable and checkable
        if col_name in [self.USE, self.STRICT]:
            flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable
            return flags

        return super().flags(index)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid(): return super().setData(index, value, role)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        return super().setData(index, value, role)

    def add_row(self):
        n_rows = self._item.rowCount()
        self._item.setRowCount(n_rows + 1)

    def get_n_rows(self):
        return self._item.rowCount()

    def set_constraint_data(
            self,
            row: int,
            name: str,
            lb: str,  # numeric or ''
            ub: str,  # numeric or ''
            formula: str,
            strict: bool = True,
    ):
        table: QStandardItem = self._item

        # notify to start editing to the abstract model
        self.beginResetModel()

        item = QStandardItem()
        item.setCheckable(True)
        item.setCheckState(Qt.CheckState.Checked)
        table.setChild(row, self.get_col_from_name(self.USE), item)

        item = QStandardItem()
        item.setCheckable(strict)
        item.setCheckState(Qt.CheckState.Checked)
        table.setChild(row, self.get_col_from_name(self.STRICT), item)

        item = QStandardItem(lb)
        table.setChild(row, self.get_col_from_name(self.LB), item)

        item = QStandardItem(ub)
        table.setChild(row, self.get_col_from_name(self.UB), item)

        item = QStandardItem(formula)
        table.setChild(row, self.get_col_from_name(self.FORMULA), item)

        item = QStandardItem(name)
        table.setChild(row, self.get_col_from_name(self.NAME), item)

        # notify to end editing to the abstract model
        self.endResetModel()

    def remove_constraint(self, row: int):
        table: QStandardItem = self._item
        self.beginResetModel()
        table.removeRow(row)
        self.endResetModel()


class PrmProxyModelForCns(MyStandardItemAsTableModelWithoutHeader):
    """Filter name and exp columns from PrmModel"""

    def filterAcceptsColumn(self, source_column: int, source_parent: QModelIndex) -> bool:
        prm_model: PrmModel = self.sourceModel()
        if not prm_model:
            return False

        # define columns to show
        columns_to_show = [
            prm_model.get_col_from_name(prm_model.NAME),
            prm_model.get_col_from_name(prm_model.INIT),
        ]

        # filter
        return source_column in columns_to_show

    def flags(self, proxyIndex):
        # uneditable anyway
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
