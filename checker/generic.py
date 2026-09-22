from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException
)
import json
import time
from storage import ESTADOS, DEFAULT_PATH, guardar

class GenericChecker:

    def __init__(self, driver, config_path):
        self.driver = driver

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.wait = WebDriverWait(driver, 15)

    def _locator(self, step):
        if step["type"] == "css":
            return By.CSS_SELECTOR, step["selector"]

        if step["type"] == "xpath":
            return By.XPATH, step["selector"]
        
        if step["type"] == "class":
            return By.CLASS_NAME, step["selector"]

        raise ValueError(
            f"Tipo de selector desconocido: {step['type']}"
        )

    def detectar_resultado(self, timeout=30):

        estrategia = self.config.get("result_strategy", "dom")

        if estrategia == "livewire":
            return self.detectar_resultado_livewire(timeout)

        resultados = self.config.get("results", {})

        def buscar_resultado(driver):

            for estado, step in resultados.items():

                by, selector = self._locator(step)

                elementos = driver.find_elements(
                    by,
                    selector
                )

                if elementos:
                    return estado

            return False

        try:
            return WebDriverWait(
                self.driver,
                timeout,
                poll_frequency=0.5
            ).until(buscar_resultado)

        except TimeoutException:
            return None
        
    def detectar_resultado_livewire(self, timeout=30):

        limite = time.time() + timeout

        while time.time() < limite:

            try:
                componentes = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "[wire\\:snapshot]"
                )

                for componente in componentes:

                    try:
                        raw = componente.get_attribute("wire:snapshot")

                        if not raw:
                            continue

                        snapshot = json.loads(raw)
                        data = snapshot.get("data", {})

                        # Componente que contiene el estado
                        # de la consulta.
                        if (
                            "paso2" not in data
                            or "encontrado" not in data
                        ):
                            continue

                        print(
                            "[DEBUG LIVEWIRE]",
                            json.dumps(
                                data,
                                indent=2,
                                ensure_ascii=False
                            )
                        )

                        if data.get("paso2") is True:

                            if data.get("encontrado") is True:
                                return "positive"

                            return "negative"

                    except StaleElementReferenceException:
                        continue

            except WebDriverException as e:
                print("[DEBUG LIVEWIRE ERROR]", e)

            time.sleep(0.4)

        print("[DEBUG LIVEWIRE] Timeout")

        return None

    def ejecutar(self, **variables):

        self.driver.get(self.config["url"])

        for step in self.config["steps"]:
            
            action = step["action"]

            if action == "reach_down":
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            elif action == "scroll_down":
                value = step.get("value", 50)
                self.driver.execute_script(f"window.scrollTo(0, {value});")

            elif action == "fill":

                by, selector = self._locator(step)

                elemento = self.wait.until(
                    EC.element_to_be_clickable(
                        (by, selector)
                    )
                )

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

                print("\n====================")
                print("ACTION: CLICK")
                print("BY:", by)
                print("SELECTOR:", selector)

                elemento = self.wait.until(
                    EC.element_to_be_clickable((by, selector))
                )

                print("FOUND:", elemento.tag_name)
                print("TEXT:", repr(elemento.text))

                elemento.click()

                print("CLICK OK")
                print("====================")

            elif action == "click_shadow":
                host = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, step["host"])
                    )
                )

                shadow = host.shadow_root

                elemento = shadow.find_element(
                    By.CSS_SELECTOR,
                    step["selector"]
                )

                elemento.click()

            elif action == "select_option":
                by, selector = self._locator(step)

                elemento = self.wait.until(
                    EC.presence_of_element_located((by, selector))
                )
                Select(elemento).select_by_value(step["value"])
                
            elif action == "wait4captcha":
                by, selector = self._locator(step)
                
                elemento = self.wait.until(
                    EC.invisibility_of_element_located((by, selector))
                )

            elif action == "pause":
                time.sleep(step.get("time", 1))
            
        return self.detectar_resultado()