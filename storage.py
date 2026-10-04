<<<<<<< HEAD
# -*- coding: utf-8 -*-
=======
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
"""Guarda y carga el progreso de la consulta en un JSON en el directorio
de configuración del usuario, para poder cerrar la app y seguir después."""

import json
import os
from datetime import datetime
from pathlib import Path

from carriers import CARRIERS

<<<<<<< HEAD
ESTADOS = ["Pendiente", "Línea encontrada", "Sin línea", "No se pudo revisar"]
MAX_HISTORIAL = 20


def _config_dir() -> Path:
=======
STATUS_OPTIONS = ["Pendiente", "Línea encontrada", "Sin línea", "No se pudo revisar"]
MAX_HISTORY = 20


def _get_config_dir() -> Path:
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    d = base / "lineas-curp"
    d.mkdir(parents=True, exist_ok=True)
    return d


<<<<<<< HEAD
DEFAULT_PATH = _config_dir() / "progreso.json"


def nuevo_progreso() -> dict:
=======
DEFAULT_PATH = _get_config_dir() / "progreso.json"


def create_default_state() -> dict:
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
    return {
        "curp": "",
        "navegador": "Firefox",
        "perfil": "",
        "resultados": {
<<<<<<< HEAD
            nombre: {"estado": "Pendiente", "notas": "", "fecha": "", "historial": []}
            for nombre, _url in CARRIERS
=======
            name: {"estado": "Pendiente", "notas": "", "fecha": "", "historial": []}
            for name, _url in CARRIERS
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
        },
    }


<<<<<<< HEAD
def cargar(path: Path = DEFAULT_PATH) -> dict:
    if not Path(path).exists():
        return nuevo_progreso()
=======
def load_progress(path: Path = DEFAULT_PATH) -> dict:
    if not Path(path).exists():
        return create_default_state()
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
<<<<<<< HEAD
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
=======
        return create_default_state()

    base = create_default_state()
    base["curp"] = data.get("curp", "")
    base["navegador"] = data.get("navegador", base["navegador"])
    base["perfil"] = data.get("perfil", "")
    saved_results = data.get("resultados", {})
    for name in base["resultados"]:
        if name in saved_results:
            base["resultados"][name].update(saved_results[name])
    return base


def record_status(data: dict, name: str, status: str, notes=None) -> None:
    """Cambia el estado de una compañía y deja constancia de cuándo y qué
    se marcó"""
    choice = data["resultados"][name]
    timestamp = datetime.now().isoformat(timespec="seconds")
    choice["estado"] = status
    choice["fecha"] = timestamp
    if notes is not None:
        choice["notas"] = notes
    history = choice.setdefault("historial", [])
    history.append({"fecha": timestamp, "estado": status})
    del history[:-MAX_HISTORY]


def save_progress(data: dict, path: Path = DEFAULT_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)
