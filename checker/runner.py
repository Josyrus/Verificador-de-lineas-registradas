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
        if config is None:
            return "unknown"

        if self.driver is None:
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
