import configparser
import json
import os
import sys
from pathlib import Path

NAVEGADORES = ["Chromium", "Firefox"]


def _raices_chromium():
    home = Path.home()
    if sys.platform.startswith("win"):
        local = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
        return [local / "Chromium/User Data", local / "Google/Chrome/User Data"]
    if sys.platform == "darwin":
        base = home / "Library/Application Support"
        return [base / "Chromium", base / "Google/Chrome"]
    return [home / ".config/chromium", home / ".config/google-chrome"]


def _raices_firefox():
    home = Path.home()
    if sys.platform.startswith("win"):
        return [Path(os.environ.get("APPDATA", home / "AppData/Roaming")) / "Mozilla/Firefox"]
    if sys.platform == "darwin":
        return [home / "Library/Application Support/Firefox"]
    return [
        home / ".mozilla/firefox",
        home / ".config/mozilla/firefox",
        home / "snap/firefox/common/.mozilla/firefox",
    ]


def _perfiles_chromium():
    encontrados = []
    for raiz in _raices_chromium():
        if not raiz.is_dir():
            continue

        # "Local State" guarda el nombre visible de cada perfil
        nombres = {}
        try:
            estado = json.loads((raiz / "Local State").read_text(encoding="utf-8"))
            nombres = {
                carpeta: datos.get("name", carpeta)
                for carpeta, datos in estado["profile"]["info_cache"].items()
            }
        except (OSError, ValueError, KeyError, AttributeError):
            pass

        carpetas = [
            d for d in raiz.iterdir()
            if d.is_dir() and (d.name == "Default" or d.name.startswith("Profile "))
        ]
        for d in sorted(carpetas):
            encontrados.append((f"{nombres.get(d.name, d.name)} — {raiz.name}", d))
    return encontrados


def _perfiles_firefox():
    encontrados = []
    for raiz in _raices_firefox():
        ini = raiz / "profiles.ini"
        if not ini.is_file():
            continue

        cfg = configparser.ConfigParser()
        try:
            cfg.read(ini, encoding="utf-8")
        except configparser.Error:
            continue

        for seccion in cfg.sections():
            if not seccion.startswith("Profile"):
                continue
            ruta = cfg[seccion].get("Path")
            if not ruta:
                continue
            es_relativa = cfg[seccion].get("IsRelative", "1") == "1"
            carpeta = raiz / ruta if es_relativa else Path(ruta)
            if carpeta.is_dir():
                encontrados.append((cfg[seccion].get("Name", carpeta.name), carpeta))
    return encontrados


def detectar_perfiles(navegador):
    if navegador == "Firefox":
        return _perfiles_firefox()
    return _perfiles_chromium()


def argumentos_perfil(navegador, ruta):
    ruta = Path(ruta)
    if navegador == "Firefox":
        return ["-profile", str(ruta)]
    if (ruta / "Preferences").exists():  # carpeta de perfil: Default, Profile 1…
        return [f"--user-data-dir={ruta.parent}", f"--profile-directory={ruta.name}"]
    return [f"--user-data-dir={ruta}"]   # carpeta propia usada como raíz