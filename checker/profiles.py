import configparser
import json
import os
import sys
from pathlib import Path

BROWSERS = ["Chromium", "Firefox"]


def _chromium_roots():
    home = Path.home()
    if sys.platform.startswith("win"):
        local = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
        return [local / "Chromium/User Data", local / "Google/Chrome/User Data"]
    if sys.platform == "darwin":
        base = home / "Library/Application Support"
        return [base / "Chromium", base / "Google/Chrome"]
    return [home / ".config/chromium", home / ".config/google-chrome"]


def _firefox_roots():
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


def _chromium_profiles():
    profiles = []
    for root in _chromium_roots():
        if not root.is_dir():
            continue

        # "Local State" guarda el nombre visible de cada perfil
        names = {}
        try:
            status = json.loads((root / "Local State").read_text(encoding="utf-8"))
            names = {
                directory: profile_data.get("name", directory)
                for directory, profile_data in status["profile"]["info_cache"].items()
            }
        except (OSError, ValueError, KeyError, AttributeError):
            pass

        directories = [
            d for d in root.iterdir()
            if d.is_dir() and (d.name == "Default" or d.name.startswith("Profile "))
        ]
        for d in sorted(directories):
            profiles.append((f"{names.get(d.name, d.name)} — {root.name}", d))
    return profiles


def _firefox_profiles():
    profiles = []
    for root in _firefox_roots():
        ini_path = root / "profiles.ini"
        if not ini_path.is_file():
            continue

        config = configparser.ConfigParser()
        try:
            config.read(ini_path, encoding="utf-8")
        except configparser.Error:
            continue

        for section in config.sections():
            if not section.startswith("Profile"):
                continue
            path = config[section].get("Path")
            if not path:
                continue
            is_relative = config[section].get("IsRelative", "1") == "1"
            directory = root / path if is_relative else Path(path)
            if directory.is_dir():
                profiles.append((config[section].get("Name", directory.name), directory))
    return profiles


def detect_profiles(browser):
    if browser == "Firefox":
        return _firefox_profiles()
    return _chromium_profiles()


def profile_arguments(browser, path):
    path = Path(path)
    if browser == "Firefox":
        return ["-profile", str(path)]
    if (path / "Preferences").exists():  # carpeta de perfil: Default, Profile 1…
        return [f"--user-data-dir={path.parent}", f"--profile-directory={path.name}"]
    return [f"--user-data-dir={path}"]   # carpeta propia usada como raíz