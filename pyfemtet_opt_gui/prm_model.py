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

    def __init__(self, table_item: QStandardItem, root: QStandardItem, parent=None):
        super().__init__(table_item, root, parent)
        self.initialize_table()

    def initialize_table(self):
        # initialize table
        table: QStandardItem = self._item
        table.clearData()
        table.setText(self._category)
        table.setRowCount(0)
        table.setColumnCount(6)
        self.set_header(self.HEADER)
        self._root.setColumnCount(max(self._root.columnCount(), table.columnCount()))

    def load(self) -> ReturnCode:
        # 現在の table の状態と Femtet からの情報を比較し、
        # table を Femtet と同期する

        # if Femtet is not alive, do nothing
        if not _p.check_femtet_alive():
            return ReturnCode.ERROR.FEMTET_CONNECTION_FAILED

        # load prm
        new_prm_names = _p.Femtet.GetVariableNames_py()

        # if no parameter in Femtet, show error message
        if new_prm_names is None:
            return ReturnCode.WARNING.PARAMETER_EMPTY
        if len(new_prm_names) == 0:
            return ReturnCode.WARNING.PARAMETER_EMPTY

        # declare
        table: QStandardItem = self._item

        # get current names and its row
        current_prm_names: list[str]
        current_prm_rows: list[int]
        current_prm_names, current_prm_rows = self.get_variable_names(with_row=True)

        # notify to start editing to the abstract model
        self.beginResetModel()

        prm_names_to_add = []
        for new_prm_name in new_prm_names:
            # if new parameter is in current ones,
            # update test value only.
            if new_prm_name in current_prm_names:
                idx = current_prm_names.index(new_prm_name)
                row = current_prm_rows[idx]
                new_prm_exp = str(_p.Femtet.GetVariableExpression(new_prm_name))
                self.set_parameter(row, test=new_prm_exp)

            # if new parameter is not in current ones,
            # mark it to add
            else:
                prm_names_to_add.append(new_prm_name)

        # if current parameter is not in new ones,
        # mark it to remove.
        prm_rows_to_remove = []
        for current_prm_name, row in zip(current_prm_names, current_prm_rows):
            if current_prm_name not in new_prm_names:
                prm_rows_to_remove.append(row)

        # remove parameters
        for row in prm_rows_to_remove[::-1]:
            table.removeRow(row)

        # raises an error without this section
        # if the all parameters are removed temporally
        self.endResetModel()
        self.beginResetModel()

        # add parameters
        for prm_name in prm_names_to_add:
            exp = str(_p.Femtet.GetVariableExpression(prm_name))
            self.add_parameter(name=prm_name, expression=exp)

        # notify to end editing to the abstract model
        self.endResetModel()

        return super().load()

    def add_parameter(self, name: str, expression: str):
        # declare
        table = self._item

        # use
        use = None
        if _isnumeric(expression):
            use = True

        # lb
        lb = ''
        if _isnumeric(expression):
            lb = str(float(expression) - 1.0)

        # ub
        ub = ''
        if _isnumeric(expression):
            ub = str(float(expression) + 1.0)

        # test
        test = ''
        if _isnumeric(expression):
            test = expression

        # append row
        table.setRowCount(table.rowCount() + 1)
        self.set_parameter(
            row=table.rowCount() - 1,
            name=name,
            use=use,
            init=expression,
            lb=lb,
            ub=ub,
            test=test,
        )

    def set_parameter(
            self,
            row: int,
            name: str = None,
            use: bool = None,
            init: str = None,  # expression
            lb: str = None,  # float
            ub: str = None,  # float
            test: str = None,  # expression
    ):
        # declare
        table = self._item

        # use
        if use is not None:
            item = QStandardItem()
            item.setCheckable(True)
            if use:
                check_state = Qt.CheckState.Checked
            else:
                check_state = Qt.CheckState.Unchecked
            item.setCheckState(check_state)
            table.setChild(row, 0, item)

        # name
        if name is not None:
            item = QStandardItem(name)
            table.setChild(row, 1, item)

        # init
        if init is not None:
            item = QStandardItem(init)
            table.setChild(row, 2, item)

        # lb
        if lb is not None:
            item = QStandardItem(lb)
            table.setChild(row, 3, item)

        # ub
        if ub is not None:
            item = QStandardItem(ub)
            table.setChild(row, 4, item)

        # test
        if test is not None:
            item = QStandardItem(test)
            table.setChild(row, 5, item)

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

    def get_variable_names(self, with_row=False) -> list[str]:
        # get all variables in model
        out = []
        out1 = []
        table: QStandardItem = self._item
        for r in range(1, table.rowCount()):
            # name
            name = table.child(r, self.get_col_from_name(self.NAME)).text()
            out.append(name)
            out1.append(r)
        if with_row:
            return out, out1
        else:
            return out
