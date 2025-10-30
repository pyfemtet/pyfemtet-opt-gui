import enum
from PySide6.QtCore import QCoreApplication


class CADIntegration(enum.StrEnum):
    no = QCoreApplication.translate('CAD', 'なし')
    solidworks = QCoreApplication.translate('CAD', 'Solidworks')


current_cad: CADIntegration = CADIntegration.no


def get():
    if current_cad == CADIntegration.no:
        return FemtetInterfaceGUI

    elif current_cad == CADIntegration.solidworks:
        return SolidWorksInterfaceGUI

    else:
        assert False, f'Unknown current_cad: {current_cad}'


def switch_cad(cad: CADIntegration):
    global current_cad
    current_cad = cad


def get_current_cad_name() -> CADIntegration:
    return current_cad


# 循環参照を避けるためここでインポート
from pyfemtet_opt_gui.fem_interfaces.femtet_interface import FemtetInterfaceGUI
from pyfemtet_opt_gui.fem_interfaces.solidworks_interface import SolidWorksInterfaceGUI
