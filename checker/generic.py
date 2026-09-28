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
                except StaleElementReferenceException:
                    continue
            return False

        try:
            return WebDriverWait(
                self.driver,
                timeout,
                poll_frequency=0.5,
                ignored_exceptions=(StaleElementReferenceException,),
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

        try:
            try:
                self.driver.get(self.config["url"])
            except TimeoutException:
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