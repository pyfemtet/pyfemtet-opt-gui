import os


def get_test_femprj_path():
    return os.path.join(
        os.path.dirname(__file__),
        'test_heatsink.femprj'
    )
