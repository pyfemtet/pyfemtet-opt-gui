import enum
from PySide6.QtCore import QCoreApplication


class CADIntegration(enum.StrEnum):
    no = QCoreApplication.translate('CAD', 'なし')
    solidworks = QCoreApplication.translate('CAD', 'Solidworks')


current_cad: CADIntegration = CADIntegration.no


def get():
    # 循環参照を避けるためここでインポート

    if current_cad == CADIntegration.no:
        from pyfemtet_opt_gui.fem_interfaces.femtet_interface.femtet_interface import FemtetInterfaceGUI
        return FemtetInterfaceGUI

    elif current_cad == CADIntegration.solidworks:
        from pyfemtet_opt_gui.fem_interfaces.solidworks_interface.solidworks_interface import SolidWorksInterfaceGUI
        return SolidWorksInterfaceGUI

    else:
        assert False, f'Unknown current_cad: {current_cad}'


def switch_cad(cad: CADIntegration):
    global current_cad
    current_cad = cad


def get_current_cad_name() -> CADIntegration:
    return current_cad
