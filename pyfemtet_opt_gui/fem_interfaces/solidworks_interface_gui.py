from pyfemtet_opt_gui.common.return_msg import ReturnType
from pyfemtet_opt_gui.fem_interfaces.femtet_interface_gui import FemtetInterfaceGUI



class SolidWorksInterfaceGUI(FemtetInterfaceGUI):

    femtet: type(FemtetInterfaceGUI) = FemtetInterfaceGUI

    @classmethod
    def get_connection_state(cls) -> ReturnType:
        return super().get_connection_state()


