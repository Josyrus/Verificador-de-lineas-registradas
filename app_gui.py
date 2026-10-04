import sys

from PySide6.QtWidgets import QApplication

from application.model import AppModel
from controllers.main_controller import MainController
from views.main_window import MainWindow


def main(argv=None):
    app = QApplication(argv or sys.argv)
    model = AppModel()
    window = MainWindow(model.companies, model.data)
    controller = MainController(model, window)
    app.aboutToQuit.connect(controller.close)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
