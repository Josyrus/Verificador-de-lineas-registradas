from __future__ import annotations

import logging
import platform
import shutil
import subprocess
import time
from pathlib import Path

from selenium.common.exceptions import (
    NoSuchWindowException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

logger = logging.getLogger(__name__)
ALERT_SOUND = Path(__file__).resolve().parent.parent / "media" / "alerta.wav"


class GenericChecker:
    def __init__(self, driver, config: dict):
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, 15)
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)

    @staticmethod
    def _play_alert() -> None:
        system = platform.system()
        player = {"Linux": "paplay", "Darwin": "afplay"}.get(system)
        if player:
            executable = shutil.which(player)
            if executable:
                subprocess.Popen(
                    [executable, str(ALERT_SOUND)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
        if system == "Windows":
            import winsound
            winsound.PlaySound(str(ALERT_SOUND), winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        print("\a", end="", flush=True)

    @staticmethod
    def _locator(step: dict):
        locator_type = step["type"]
        locator = step["selector"]
        if locator_type == "css":
            return By.CSS_SELECTOR, locator
        if locator_type == "xpath":
            return By.XPATH, locator
        if locator_type == "class":
            return By.CLASS_NAME, locator
        raise ValueError(f"Tipo de selector desconocido: {locator_type}")

    def close_browser(self) -> None:
        driver, self.driver = self.driver, None
        if driver is None:
            return
        try:
            driver.quit()
        except Exception as exc:
            logger.warning("Error al cerrar el navegador: %s", exc)

    def detect_result(self, timeout: int = 500):
        raw_results = self.config.get("results", {})
        aliases = {"positive:": "positive", "postive": "positive"}
        results = {aliases.get(key, key): value for key, value in raw_results.items()}
        locators = {status: self._locator(step) for status, step in results.items() if status in {"positive", "negative"}}

        def find_result(driver):
            for status, locator in locators.items():
                try:
                    if driver.find_elements(*locator):
                        return status
                except StaleElementReferenceException:
                    continue
            return False

        try:
            return WebDriverWait(
                self.driver,
                timeout,
                poll_frequency=0.5,
                ignored_exceptions=(StaleElementReferenceException,),
            ).until(find_result)
        except TimeoutException:
            logger.error("No apareció ningún resultado en %s s", timeout)
            self.close_browser()
            return None
        except (NoSuchWindowException, WebDriverException) as exc:
            logger.error("Error de WebDriver: %s", exc)
            self.close_browser()
            return None

    def execute(self, **variables):
        current_step = None
        try:
            try:
                self.driver.get(self.config["url"])
            except TimeoutException:
                logger.warning("La página tardó demasiado en cargar; deteniendo carga")
                self.driver.execute_script("window.stop();")

            for index, step in enumerate(self.config.get("steps", []), start=1):
                action = step["action"]
                current_step = f"#{index} ({action})"
                self._execute_step(action, step, variables)

            return self.detect_result()
        except TimeoutException:
            logger.error("Timeout en el paso %s", current_step)
            self.close_browser()
            return None
        except (NoSuchWindowException, WebDriverException) as exc:
            logger.error("Error de WebDriver en %s: %s", current_step, exc)
            self.close_browser()
            return None
        except Exception:
            logger.exception("Error inesperado en %s", current_step)
            self.close_browser()
            raise

    def _execute_step(self, action: str, step: dict, variables: dict) -> None:
        if action == "reach_down":
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elif action == "scroll_down":
            self.driver.execute_script(f"window.scrollTo(0, {step.get('value', 50)});")
        elif action == "switch_to_frame":
            iframe = self.wait.until(EC.presence_of_element_located(self._locator(step)))
            self.driver.switch_to.frame(iframe)
        elif action == "fill":
            element = self.wait.until(EC.element_to_be_clickable(self._locator(step)))
            self._fill(element, step["value"].format(**variables))
        elif action == "fill_shadow":
            host = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step["host"])))
            element = host.shadow_root.find_element(*self._locator(step))
            self._fill(element, step["value"].format(**variables))
        elif action == "click":
            self._click(step)
        elif action == "click_if_present":
            elements = self.driver.find_elements(*self._locator(step))
            if elements and elements[0].is_displayed():
                elements[0].click()
        elif action == "click_shadow":
            host = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step["host"])))
            host.shadow_root.find_element(By.CSS_SELECTOR, step["selector"]).click()
        elif action == "select_option":
            element = self.wait.until(EC.presence_of_element_located(self._locator(step)))
            Select(element).select_by_value(step["value"])
        elif action in {"wait4captcha", "wait_if_captcha"}:
            self._wait_for_captcha(step)
        elif action == "pause":
            time.sleep(step.get("time", 1))
        elif action == "script":
            self.driver.execute_script(step["script"])
        else:
            raise ValueError(f"Acción desconocida: {action}")

    def _fill(self, element, value: str) -> None:
        element.click()
        element.clear()
        element.send_keys(value)
        actual = element.get_attribute("value")
        if actual != value:
            raise RuntimeError(f"No se pudo rellenar el campo. Esperado: {value}; obtenido: {actual}")

    def _click(self, step: dict) -> None:
        timeout = step.get("timeout", 15)
        by, selector = self._locator(step)

        def clickable(driver):
            element = driver.find_element(by, selector)
            return element if (
                element.is_displayed()
                and element.is_enabled()
                and element.get_attribute("disabled") is None
                and element.get_attribute("aria-disabled") != "true"
            ) else False

        self.wait = WebDriverWait(self.driver, timeout)
        self.wait.until(clickable).click()

    def _wait_for_captcha(self, step: dict) -> None:
        locator = self._locator(step)
        if not self.driver.find_elements(*locator):
            return
        self._play_alert()
        WebDriverWait(self.driver, 300).until(lambda driver: not driver.find_elements(*locator))
