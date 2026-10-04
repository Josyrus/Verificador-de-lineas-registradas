<<<<<<< HEAD
import logging, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchWindowException,
    WebDriverException,
)
from storage import ESTADOS, DEFAULT_PATH, guardar

logger = logging.getLogger(__name__)

class GenericChecker:

    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, 15)
        self.driver.set_page_load_timeout(30)
        self.driver.set_script_timeout(30)

    def _locator(self, step):
        if step["type"] == "css":
            return By.CSS_SELECTOR, step["selector"]
        if step["type"] == "xpath":
            return By.XPATH, step["selector"]
        if step["type"] == "class":
            return By.CLASS_NAME, step["selector"]
        raise ValueError(f"Tipo de selector desconocido: {step['type']}")

    def cerrar_navegador(self):
        
        if not getattr(self, "driver", None):
            return
        try:
            self.driver.quit()
        except Exception as e:
            logger.warning("Error al cerrar el navegador: %s", e)
        finally:
            self.driver = None

    def detectar_resultado(self, timeout=30):
        resultados = self.config.get("results", {})
        locators = {estado: self._locator(step) for estado, step in resultados.items()}

        def buscar_resultado(driver):
            for estado, (by, selector) in locators.items():
                try:
                    if driver.find_elements(by, selector):
                        return estado
=======
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
        # Tolerate old configuration typos without spreading compatibility logic.
        aliases = {"positive:": "positive", "postive": "positive"}
        results = {aliases.get(key, key): value for key, value in raw_results.items()}
        locators = {status: self._locator(step) for status, step in results.items() if status in {"positive", "negative"}}

        def find_result(driver):
            for status, locator in locators.items():
                try:
                    if driver.find_elements(*locator):
                        return status
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
                except StaleElementReferenceException:
                    continue
            return False

        try:
            return WebDriverWait(
                self.driver,
                timeout,
                poll_frequency=0.5,
                ignored_exceptions=(StaleElementReferenceException,),
<<<<<<< HEAD
            ).until(buscar_resultado)

        except TimeoutException:
            logger.error("No apareció ningún resultado en %s s. Cerrando navegador.", timeout)
            self.cerrar_navegador()
            return None

        except (NoSuchWindowException, WebDriverException) as e:
            logger.error("Error de WebDriver: %s. Cerrando navegador.", e)
            self.cerrar_navegador()
            return None
            
    def ejecutar(self, **variables):
        paso_actual = None 

=======
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
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
        try:
            try:
                self.driver.get(self.config["url"])
            except TimeoutException:
<<<<<<< HEAD
                logger.warning("La página tardó demasiado en cargar, deteniendo carga.")
                self.driver.execute_script("window.stop();")

            for i, step in enumerate(self.config["steps"], start=1):
                action = step["action"]
                paso_actual = f"#{i} ({action})"

                if action == "reach_down":
                    time.sleep(1)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                elif action == "switch_to_frame":
                    by, selector = self._locator(step)
                    iframe = self.wait.until(EC.presence_of_element_located((by, selector)))
                    self.driver.switch_to.frame(iframe)
                    print(f"[>] Cambiado a iframe: {selector}")

                elif action == "scroll_down":
                    value = step.get("value", 50)
                    self.driver.execute_script(f"window.scrollTo(0, {value});")

                elif action == "fill":
                    by, selector = self._locator(step)
                    elemento = self.wait.until(EC.element_to_be_clickable((by, selector)))
                    valor = step["value"].format(**variables)

                    print(f"[>] Rellenando: {selector}")
                    print(f"[>] Valor: {valor}")

                    elemento.click()
                    elemento.clear()
                    elemento.send_keys(valor)

                    valor_actual = elemento.get_attribute("value")
                    print(f"[<] Campo contiene: {valor_actual}")

                    if valor_actual != valor:
                        raise RuntimeError(
                            f"No se pudo rellenar el campo.\n"
                            f"Esperado: {valor}\n"
                            f"Obtenido: {valor_actual}"
                        )

                elif action == "script":
                    resultado = self.driver.execute_script(step["script"])
                    print("[DEBUG SCRIPT]", resultado)

                elif action == "click":
                    by, selector = self._locator(step)
                    timeout = step.get("timeout", 15)

                    print("\n====================")
                    print("ACTION: CLICK")
                    print("BY:", by)
                    print("SELECTOR:", selector)

                    elemento = WebDriverWait(self.driver, timeout).until(
                        lambda d: (
                            (e := d.find_element(by, selector))
                            and e.is_displayed()
                            and e.is_enabled()
                            and e.get_attribute("disabled") is None
                            and e.get_attribute("aria-disabled") != "true"
                        ) and e
                    )

                    print("FOUND:", elemento.tag_name)
                    print("TEXT:", repr(elemento.text))
                    elemento.click()
                    print("CLICK OK")
                    print("====================")

                elif action == "wait_if_captcha":
                    by, selector = self._locator(step)

                    if not self.driver.find_elements(by, selector):
                        print("[>] CAPTCHA no presente, continuando")
                        continue

                    print("[!] CAPTCHA detectado. Esperando resolución...")
                    WebDriverWait(self.driver, 300).until(
                        lambda d: not d.find_elements(by, selector)
                    )
                    print("[>] CAPTCHA resuelto, continuando")

                elif action == "click_shadow":
                    host = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, step["host"]))
                    )
                    elemento = host.shadow_root.find_element(By.CSS_SELECTOR, step["selector"])
                    elemento.click()

                elif action == "fill_shadow":
                    host_by, host_selector = self._locator({
                        "type": step["type"],
                        "selector": step["host"],
                    })
                    host = self.wait.until(
                        EC.presence_of_element_located((host_by, host_selector))
                    )
                    by, selector = self._locator(step)
                    elemento = host.shadow_root.find_element(by, selector)
                    valor = step["value"].format(**variables)

                    print(f"[>] Rellenando Shadow DOM: {selector}")
                    print(f"[>] Valor: {valor}")

                    elemento.click()
                    elemento.clear()
                    elemento.send_keys(valor)

                elif action == "select_option":
                    by, selector = self._locator(step)
                    elemento = self.wait.until(EC.presence_of_element_located((by, selector)))
                    Select(elemento).select_by_value(step["value"])

                elif action == "wait4captcha":
                    by, selector = self._locator(step)
                    self.wait.until(EC.invisibility_of_element_located((by, selector)))

                    WebDriverWait(self.driver, 300).until(EC.alert_is_present())
                    self.driver.switch_to.alert.accept()

                elif action == "pause":
                    time.sleep(step.get("time", 1))

                else:
                    raise ValueError(f"Acción desconocida: {action}")

            return self.detectar_resultado()

        except TimeoutException:
            logger.error("Timeout en el paso %s. Cerrando navegador.", paso_actual)
            self.cerrar_navegador()
            return None

        except (NoSuchWindowException, WebDriverException) as e:
            logger.error("Error de WebDriver en el paso %s: %s. Cerrando navegador.", paso_actual, e)
            self.cerrar_navegador()
            return None

        except Exception:
            logger.exception("Error inesperado en el paso %s", paso_actual)
            self.cerrar_navegador()
            raise
=======
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
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
