from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from undetected_geckodriver import Firefox

def crear_driver():
    options = Options()
    
    options.set_preference("dom.webdriver.enabled", False)
    options.profile = "/home/josyrus/perfil-automatizacion"
    
    driver = Firefox()
    return driver