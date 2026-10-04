from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from undetected_geckodriver import Firefox

<<<<<<< HEAD
from checker.perfiles import argumentos_perfil


def crear_driver(navegador="Firefox", perfil=""):

    if navegador == "Firefox":
        options = FirefoxOptions()
        options.set_preference("dom.webdriver.enabled", False)

        if perfil:
            for arg in argumentos_perfil(navegador, perfil):
=======
from checker.profiles import profile_arguments


def create_driver(browser="Firefox", profile=""):

    if browser == "Firefox":
        options = FirefoxOptions()
        options.set_preference("dom.webdriver.enabled", False)

        if profile:
            for arg in profile_arguments(browser, profile):
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
                options.add_argument(arg)

        return Firefox(options=options)

    options = ChromeOptions()

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

<<<<<<< HEAD
    if perfil:
        for arg in argumentos_perfil(navegador, perfil):
=======
    if profile:
        for arg in profile_arguments(browser, profile):
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
            options.add_argument(arg)

    driver = webdriver.Chrome(options=options)

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        },
    )

    return driver