from pathlib import Path

from .browser import crear_driver
from .generic import GenericChecker
import json, traceback

BASE_DIR = Path(__file__).resolve().parent

CONFIG_DIR = BASE_DIR / "providers" / "configs"
TEMPLATE_DIR = BASE_DIR / "providers" / "templates"

def cargar_config(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        config = json.load(f)

    template = config.get("template")

    if template:
        template_path = TEMPLATE_DIR / f"{template}.json"

        with open(template_path, "r", encoding="utf-8") as f:
            base = json.load(f)

        base.update(config)
        config = base

    return config


CONFIGS = {}

for archivo in CONFIG_DIR.glob("*.json"):
    config = cargar_config(archivo)
    CONFIGS[config["nombre"]] = config
    
class CheckerRunner:

    def __init__(self):
        self.driver = None
        self.navegador = "Firefox"
        self.perfil = ""

    def configurar(self, navegador, perfil):
        if (navegador, perfil) != (self.navegador, self.perfil):
            self.cerrar()
        self.navegador = navegador
        self.perfil = perfil

    def ejecutar(self, nombre, curp, telefonos=None):
        config = CONFIGS.get(nombre)

        print(f"[>] Proveedor: {nombre}")
        print(f"[DEBUG] config existe: {config is not None}")

        if config is None:
            return "unknown"

        if self.driver is None:
            self.driver = crear_driver(self.navegador, self.perfil)

        checker = None
        try:
            checker = GenericChecker(self.driver, config)
            return checker.ejecutar(
                curp=curp,
                telefonos=telefonos or []
            )

        except Exception as e:
            print(f"[DEBUG] EXCEPCIÓN REAL: {type(e).__name__}: {e}")
            traceback.print_exc()
            self.cerrar(forzar=True)
            raise

        finally:
            if checker is not None and checker.driver is None:
                self.driver = None

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