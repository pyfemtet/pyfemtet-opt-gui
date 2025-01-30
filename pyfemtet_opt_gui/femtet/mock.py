from pyfemtet_opt_gui.common.return_msg import ReturnMsg

__all__ = [
    'get_femtet',
    'get_connection_state',
    'get_obj_names',
    'get_variables',
]


class FemtetMock:

    def Version(self):
        return '2025.0.0'

    def hWnd(self):
        return 1


def get_femtet():
    return FemtetMock()


def get_connection_state():
    return ReturnMsg.no_message


def get_obj_names():
    return ['obj1', 'obj2',], ReturnMsg.no_message


def get_variables():
    out = dict(
        a=1,
        b=2,
        c='a + b'
    )
    return out, ReturnMsg.no_message
