import json
import os
from datetime import datetime
from pathlib import Path

from carriers import CARRIERS

STATUS_OPTIONS = ["Pendiente", "Línea encontrada", "Sin línea", "No se pudo revisar"]
MAX_HISTORY = 20


def _get_config_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    d = base / "lineas-curp"
    d.mkdir(parents=True, exist_ok=True)
    return d


DEFAULT_PATH = _get_config_dir() / "progreso.json"


def create_default_state() -> dict:
    return {
        "curp": "",
        "navegador": "Firefox",
        "perfil": "",
        "resultados": {
            name: {"estado": "Pendiente", "notas": "", "fecha": "", "historial": []}
            for name, _url in CARRIERS
        },
    }


def load_progress(path: Path = DEFAULT_PATH) -> dict:
    if not Path(path).exists():
        return create_default_state()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
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
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)
