# -*- coding: utf-8 -*-
"""Guarda y carga el progreso de la consulta en un JSON en el directorio
de configuración del usuario, para poder cerrar la app y seguir después."""

import json
import os
from datetime import datetime
from pathlib import Path

from carriers import CARRIERS

ESTADOS = ["Pendiente", "Línea encontrada", "Sin línea", "No se pudo revisar"]
MAX_HISTORIAL = 20


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
        "navegador": "Firefox",
        "perfil": "",
        "resultados": {
            nombre: {"estado": "Pendiente", "notas": "", "fecha": "", "historial": []}
            for nombre, _url in CARRIERS
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

    base = nuevo_progreso()
    base["curp"] = data.get("curp", "")
    base["navegador"] = data.get("navegador", base["navegador"])
    base["perfil"] = data.get("perfil", "")
    resultados_guardados = data.get("resultados", {})
    for nombre in base["resultados"]:
        if nombre in resultados_guardados:
            # update() conserva los campos nuevos (fecha, historial) con su
            # valor por defecto si el progreso.json es de una versión anterior
            base["resultados"][nombre].update(resultados_guardados[nombre])
    return base


def registrar_estado(data: dict, nombre: str, estado: str, notas=None) -> None:
    """Cambia el estado de una compañía y deja constancia de cuándo y qué
    se marcó (fecha de última verificación + historial acotado). Usar esto
    en GUI y CLI en vez de escribir data["resultados"][nombre] a mano."""
    r = data["resultados"][nombre]
    ahora = datetime.now().isoformat(timespec="seconds")
    r["estado"] = estado
    r["fecha"] = ahora
    if notas is not None:
        r["notas"] = notas
    historial = r.setdefault("historial", [])
    historial.append({"fecha": ahora, "estado": estado})
    del historial[:-MAX_HISTORIAL]


def guardar(data: dict, path: Path = DEFAULT_PATH) -> None:
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)
