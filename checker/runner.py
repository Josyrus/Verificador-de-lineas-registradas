from pathlib import Path

from .browser import crear_driver
from .generic import GenericChecker
import json

BASE_DIR = Path(__file__).resolve().parent

CONFIG_DIR = BASE_DIR / "providers" / "configs"

CONFIGS = {}

for archivo in CONFIG_DIR.glob("*.json"):
    with open(archivo, "r", encoding="utf-8") as f:
        config = json.load(f)

    CONFIGS[config["nombre"]] = archivo
    
class CheckerRunner:

    def __init__(self):
        self.driver = None

    def ejecutar(self, nombre, curp, telefonos=None):

        config = CONFIGS.get(nombre)
        print(f"[>] Proveedor: {nombre}")
        print(f"[>] Configuración: {config}")

        if config is None:
            return "unknown"

        if self.driver is None:
            self.driver = crear_driver()

        try:
            checker = GenericChecker(
                self.driver,
                config
            )
        
            return checker.ejecutar(
                curp=curp,
                telefonos=telefonos or []
            )
        except Exception:
            self.cerrar(forzar=True)   
            raise

    def cerrar(self, forzar=False):
        if self.driver is None:
            return

        servicio = getattr(self.driver, "service", None)

        if not forzar:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"[!] driver.quit() falló, forzando cierre: {e}")
                forzar = True

        if forzar and servicio is not None and servicio.process is not None:
            try:
                servicio.process.kill()
                servicio.process.wait(timeout=3)
            except Exception as e:
                print(f"[!] No se pudo matar el proceso de chromedriver: {e}")

        self.driver = None