import enum
from pyfemtet_opt_gui.fem_interfaces.femtet_interface_gui import FemtetInterfaceGUI
from pyfemtet_opt_gui.fem_interfaces.solidworks_interface_gui import SolidWorksInterfaceGUI


class CADIntegration(enum.StrEnum):
    no = 'なし'
    solidworks = 'Solidworks'


current_cad = CADIntegration.no


def get():
    if current_cad == CADIntegration.no:
        return FemtetInterfaceGUI

    elif current_cad == CADIntegration.solidworks:
        return SolidWorksInterfaceGUI


def switch_cad(cad):
    global current_cad
    current_cad = cad


def get_current_cad_name():
    return current_cad
