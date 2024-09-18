from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem

import pyfemtet_opt_gui._p as _p

from pyfemtet_opt_gui.item_as_model import MyStandardItemAsTableModel, _isnumeric
from pyfemtet_opt_gui.ui.return_code import ReturnCode, should_stop


class PrmModel(MyStandardItemAsTableModel):
    """A table for determining whether to use Femtet variables in optimization.

    use        | name       | init         | lb             | ub             | test
    --------------------------------------------------------------------------------
    checkbox   | str        | float or str | float or empty | float or empty | float
    uneditable | uneditable |              |                |                |

    note: if init is not numeric, disable the row (including use column).
    note: init, lb, ub, test must be a float.
    note: if checkbox is false, disable the row (excluding use column).
    note: must be (lb < init < ub).

    """

    USE = 'use'
    NAME = 'name'
    INIT = 'initial value'
    LB = 'lower bound'
    UB = 'upper bound'
    TEST = 'test value'

    HEADER = [
            USE,
            NAME,
            INIT,
            LB,
            UB,
            TEST,
        ]

    def load(self) -> ReturnCode:

        self.beginResetModel()

        # initialize table
        table: QStandardItem = self._item
        table.clearData()
        table.setText(self._category)
        table.setRowCount(0)
        table.setColumnCount(6)
        self.set_header(self.HEADER)
        self._root.setColumnCount(max(self._root.columnCount(), table.columnCount()))

        self.endResetModel()

        # if Femtet is not alive, do nothing
        if not _p.check_femtet_alive():
            return ReturnCode.ERROR.FEMTET_CONNECTION_FAILED

        # load prm
        names = _p.Femtet.GetVariableNames_py()

        if names is None:
            return ReturnCode.WARNING.PARAMETER_EMPTY

        if len(names) == 0:
            return ReturnCode.WARNING.PARAMETER_EMPTY

        # notify to start editing to the abstract model
        self.beginResetModel()

        # set data to table
        table.setRowCount(len(names)+1)  # including header row (hidden by WithoutHeader proxy).

        for row, name in enumerate(names):

            exp = str(_p.Femtet.GetVariableExpression(name))

            row = row + 1  # avoid header row

            # use
            item = QStandardItem()
            if _isnumeric(exp):
                item.setCheckable(True)
                item.setCheckState(Qt.CheckState.Checked)
            table.setChild(row, 0, item)

            # name
            item = QStandardItem(name)
            table.setChild(row, 1, item)

            # init
            item = QStandardItem(exp)
            table.setChild(row, 2, item)

            # lb
            lb = str(float(exp)-1.0) if _isnumeric(exp) else None
            item = QStandardItem(lb)
            table.setChild(row, 3, item)

            # ub
            ub = str(float(exp)+1.0) if _isnumeric(exp) else None
            item = QStandardItem(ub)
            table.setChild(row, 4, item)

            # test
            test = exp if _isnumeric(exp) else None
            item = QStandardItem(test)
            table.setChild(row, 5, item)

        # notify to end editing to the abstract model
        self.endResetModel()

        return super().load()

    def flags(self, index):
        if not index.isValid(): return super().flags(index)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        # note: if init is not numeric, disable the row (including use column).
        exp_col = self.get_col_from_name(self.INIT)
        exp_index = self.createIndex(row, exp_col)
        if not _isnumeric(self.data(exp_index)):
            return ~Qt.ItemIsEnabled

        # note: init, lb, ub, test must be a float.
        # implemented in setData

        # note: if checkbox is false, disable the row (excluding use column).
        use_col = self.get_col_from_name('use')
        use_item = self.get_item(row, use_col)
        if use_item.checkState() == Qt.CheckState.Unchecked:
            if col_name != 'use':
                return ~Qt.ItemIsEnabled

        # note: must be (lb < init < ub).
        # implemented in setData

        # use / name is uneditable
        if col_name in ['use', 'name']:
            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
            if col_name == 'use':
                flags = flags | Qt.ItemIsUserCheckable
            return flags

        return super().flags(index)

    def setData(self, index, value, role=Qt.EditRole) -> bool:
        if not index.isValid(): return super().setData(index, value, role)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        # note: init, lb, ub, test must be a float.
        if col_name in [self.INIT, self.LB, self.UB, self.TEST]:
            if not _isnumeric(value):
                _p.logger.error('数値を入力してください。')
                return False

        # note: must be (lb < init < ub).
        if col_name in [self.INIT, self.LB, self.UB]:
            exp_index = self.createIndex(row, self.get_col_from_name(self.INIT))
            exp_float = float(value) if col_name == self.INIT else float(self.data(exp_index))

            lb_index = self.createIndex(row, self.get_col_from_name(self.LB))
            lb_float = float(value) if col_name == self.LB else float(self.data(lb_index))

            ub_index = self.createIndex(row, self.get_col_from_name(self.UB))
            ub_float = float(value) if col_name == self.UB else float(self.data(ub_index))

            if not (lb_float <= exp_float):
                should_stop(ReturnCode.ERROR.BOUND_INIT_UNDER_LB)
                return False

            if not (exp_float <= ub_float):
                should_stop(ReturnCode.ERROR.BOUND_INIT_OVER_UB)
                return False

            if lb_float == ub_float:
                should_stop(ReturnCode.ERROR.BOUND_NO_RANGE)
                return False

        # if all of 'use' is unchecked, raise warning
        if (col_name == self.USE) and (role == Qt.ItemDataRole.CheckStateRole):
            col2 = self.get_col_from_name(self.USE)
            unchecked = {}
            for row2 in range(1, self.rowCount()):
                unchecked.update(
                    {row2: self.get_item(row2, col2).checkState() == Qt.CheckState.Unchecked}
                )
            unchecked[row] = value == Qt.CheckState.Unchecked.value
            if all(unchecked.values()):
                should_stop(ReturnCode.WARNING.PARAMETER_NOT_SELECTED)
                return False

        return super().setData(index, value, role)
