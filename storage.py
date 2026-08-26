# -*- coding: utf-8 -*-
"""Guarda y carga el progreso de la consulta en un JSON en el directorio
de configuración del usuario, para poder cerrar la app y seguir después."""

import json
import os
from pathlib import Path

from carriers import CARRIERS

ESTADOS = ["Pendiente", "Línea encontrada", "Sin línea", "No se pudo revisar"]


def _config_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    d = base / "lineas-curp"
    d.mkdir(parents=True, exist_ok=True)
    return d


DEFAULT_PATH = _config_dir() / "progreso.json"


def nuevo_progreso() -> dict:
    return {
        "curp": "",
        "telefonos": [],
        "resultados": {
            nombre: {"estado": "Pendiente", "notas": ""} for nombre, _url in CARRIERS
        },
    }


def cargar(path: Path = DEFAULT_PATH) -> dict:
    if not Path(path).exists():
        return nuevo_progreso()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return nuevo_progreso()

    # Asegurar que compañías nuevas del directorio aparezcan, y no perder
    # resultados de compañías que el usuario ya revisó.
    base = nuevo_progreso()
    base["curp"] = data.get("curp", "")
    base["telefonos"] = data.get("telefonos", [])
    resultados_guardados = data.get("resultados", {})
    for nombre in base["resultados"]:
        if nombre in resultados_guardados:
            base["resultados"][nombre] = resultados_guardados[nombre]
    return base


def guardar(data: dict, path: Path = DEFAULT_PATH) -> None:
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)
