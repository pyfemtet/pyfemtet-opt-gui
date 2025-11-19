import os
import locale
from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication

# Detect the locale before loading other modules
def main():
    app = QApplication()
    app.setStyle('fusion')

    langage_region, _ = locale.getlocale()
    # if True:  # debug
    if langage_region != 'Japanese_Japan':
        here = os.path.dirname(__file__)    
        qm_path = os.path.join(here, 'qml_en_us.qm')
        translator = QTranslator()
        translator.load(qm_path)
        app.installTranslator(translator)

    from pyfemtet_opt_gui.main import main as main_
    main_(app)


if __name__ == '__main__':
    main()
