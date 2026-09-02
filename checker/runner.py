from pathlib import Path

from .browser import crear_driver
from .generic import GenericChecker


BASE_DIR = Path(__file__).resolve().parent

CONFIGS = {
    "Redes ALTÁN": BASE_DIR / "providers" / "configs" / "altan.json"
}


class CheckerRunner:

    def __init__(self):
        self.driver = None

    def ejecutar(self, nombre, curp, telefonos=None):

        config = CONFIGS.get(nombre)

        if config is None:
            return False

        if self.driver is None:
            self.driver = crear_driver()

        checker = GenericChecker(
            self.driver,
            config
        )

        checker.ejecutar(
            curp=curp,
            telefonos=telefonos or []
        )

        return True

    def cerrar(self):

        if self.driver is not None:
            self.driver.quit()
            self.driver = None