<<<<<<< HEAD
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

=======
from __future__ import annotations

import json
import logging
from pathlib import Path

from .browser import create_driver
from .generic import GenericChecker

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "providers" / "configs"
TEMPLATE_DIR = BASE_DIR / "providers" / "templates"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_config(path: Path) -> dict:
    config = load_json(path)
    template_name = config.get("template")
    if not template_name:
        return config

    template = load_json(TEMPLATE_DIR / f"{template_name}.json")
    template.update(config)
    return template


def load_configs() -> dict[str, dict]:
    configs = {}
    for path in sorted(CONFIG_DIR.glob("*.json")):
        config = load_config(path)
        name = config.get("nombre")
        if not name:
            logger.warning("Configuración sin nombre: %s", path)
            continue
        configs[name] = config
    return configs


CONFIGS = load_configs()


class CheckerRunner:
    def __init__(self) -> None:
        self.driver = None
        self.browser = "Firefox"
        self.profile = ""

    def configure(self, browser: str, profile: str) -> None:
        if (browser, profile) != (self.browser, self.profile):
            self.close()
        self.browser = browser
        self.profile = profile

    def execute(self, name: str, curp: str, phone_numbers=None):
        config = CONFIGS.get(name)
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
        if config is None:
            return "unknown"

        if self.driver is None:
<<<<<<< HEAD
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
=======
            self.driver = create_driver(self.browser, self.profile)

        try:
            checker = GenericChecker(self.driver, config)
            result = checker.execute(curp=curp, phone_numbers=phone_numbers or [])
            if checker.driver is None:
                self.driver = None
            return result
        except Exception:
            self.close(force=True)
            raise

    def close(self, force: bool = False) -> None:
        if self.driver is None:
            return

        driver, self.driver = self.driver, None
        service = getattr(driver, "service", None)

        if not force:
            try:
                driver.quit()
                return
            except Exception as exc:
                logger.warning("driver.quit() falló; forzando cierre: %s", exc)

        process = getattr(service, "process", None)
        if process is not None:
            try:
                process.kill()
                process.wait(timeout=3)
            except Exception as exc:
                logger.warning("No se pudo terminar el proceso del driver: %s", exc)
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
