from PySide6.QtWidgets import QProgressDialog
from win32com.client import CDispatch
# noinspection PyUnresolvedReferences
from pythoncom import com_error

from pyfemtet_opt_gui.common.return_msg import ReturnType, ReturnMsg
from pyfemtet_opt_gui.fem_interfaces.femtet_interface_gui import FemtetInterfaceGUI

from typing import TYPE_CHECKING


# noinspection PyMethodMayBeStatic
class GaudiMock:

    LastXTPath = 'dummy.x_t'

    @staticmethod
    def Activate():
        return None

    @staticmethod
    def ReExecute():
        return True



if TYPE_CHECKING:
    class FemtetMock(CDispatch):
        pass

else:
    # noinspection PyMethodMayBeStatic
    class FemtetMock:

        hWnd = 1000

        _dummy_var = {
            'pi': 3.141592653589793238,
            'fem_x1': 1.0,
            'fem_x2': -2.0,
            'fem_x3': 'fem_x1 + fem_x3',
        }

        Project='dummy.femprj'
        AnalysisModelName='dummy_model'

        def SaveProject(self, femprj_path, bForce):
            self.Project = femprj_path
            return True

        def LoadProject(self, femprj_path, bForce):
            self.Project = femprj_path
            return True

        def GetVariableNames_py(self):
            return tuple(self._dummy_var.keys())

        def GetVariableExpression(self, name):
            return str(self._dummy_var[name])

        def UpdateVariable(self, name, value):
            if isinstance(value, int | float):
                self._dummy_var[name] = value
                return True
            else:
                return False

        def ShowLastError(self):
            raise com_error('dummy exception.')

        @staticmethod
        def Redraw():
            return None


class FemtetInterfaceMock(FemtetInterfaceGUI):

    @classmethod
    def get_femtet(cls, progress: QProgressDialog = None) -> tuple[FemtetMock | None, ReturnType]:
        return FemtetMock(), ReturnMsg.no_message
