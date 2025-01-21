# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

from pyfemtet_opt_gui_2.ui.ui_WizardPage_cns import Ui_WizardPage

from pyfemtet_opt_gui_2.common.qt_util import *
from pyfemtet_opt_gui_2.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui_2.common.return_msg import *
from pyfemtet_opt_gui_2.femtet.femtet import *

import enum
import sys
from contextlib import nullcontext

# ===== model singleton pattern =====
_CNS_MODEL = None
_WITH_DUMMY = False


def get_cns_model(parent=None, _with_dummy=None):
    global _CNS_MODEL
    if _CNS_MODEL is None:
        _CNS_MODEL = ConstraintModel(
            parent=parent,
            _with_dummy=_with_dummy if _with_dummy is not None else _WITH_DUMMY,
        )
    return _CNS_MODEL


def get_cns_model_for_problem(parent=None, with_dummy=None):
    model = get_cns_model(parent, _with_dummy=None)
    model_for_problem = ConstraintModelForProblem()
    model_for_problem.setSoruceModel(model)
    return model_for_problem


# ===== header data =====
class ConstraintColumnNames(enum.StrEnum):
    use = CommonItemColumnName.use
    name = '名前'
    expr = '式'
    lb = '下限'
    ub = '上限'
    note = 'メモ欄'


# ===== Qt objects =====
# 大元のモデル
class ConstraintModel(StandardItemModelWithHeader):
    ColumnNames = ConstraintColumnNames


