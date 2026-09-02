from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

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

        raise ValueError(
            f"Tipo de selector desconocido: {step['type']}"
        )

    def ejecutar(self, **variables):

        self.driver.get(self.config["url"])

        for step in self.config["steps"]:

            action = step["action"]

            if action == "fill":

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

                # Verificar que realmente se escribió
                valor_actual = elemento.get_attribute("value")

                print(f"[<] Campo contiene: {valor_actual}")

                if valor_actual != valor:
                    raise RuntimeError(
                        f"No se pudo rellenar el campo.\n"
                        f"Esperado: {valor}\n"
                        f"Obtenido: {valor_actual}"
                    )

            elif action == "click":

                by, selector = self._locator(step)

                elemento = self.wait.until(
                    EC.element_to_be_clickable(
                        (by, selector)
                    )
                )

                elemento.click()

            elif action == "pause":

                input(
                    step.get(
                        "message",
                        "Presiona ENTER para continuar..."
                    )
                )