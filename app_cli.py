"""Modo consola.

Ofrece lo mismo que la interfaz gráfica: CURP, navegador y perfil de
sesión, lista filtrable de compañías con su estado y notas, revisión
automática con CheckerRunner y marcado manual del estado.

No automatiza CAPTCHAs ni verificaciones que requieran intervención
manual.
"""

import argparse
import csv
import os
import sys
from pathlib import Path

from carriers import CARRIERS, search_carriers
from clipboard import copy_to_clipboard
from checker.profiles import BROWSERS, detect_profiles
from storage import STATUS_OPTIONS, DEFAULT_PATH, load_progress, save_progress, record_status
from checker.runner import CheckerRunner

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ

STATUS_COLORS = {
    "Pendiente": "33",           # naranja/amarillo
    "Línea encontrada": "32",    # verde
    "Sin línea": "90",           # gris
    "No se pudo revisar": "31",  # rojo
}

STATUS_ALIASES = {
    "pendiente": STATUS_OPTIONS[0],
    "encontrada": STATUS_OPTIONS[1],
    "sin": STATUS_OPTIONS[2],
    "error": STATUS_OPTIONS[3],
}

EXIT = object()


def colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def status_indicator(status: str) -> str:
    return colorize("●", STATUS_COLORS.get(status, "90"))


def parse_status(text: str):
    t = text.strip().lower()
    if t in STATUS_ALIASES:
        return STATUS_ALIASES[t]
    for status in STATUS_OPTIONS:
        if status.lower() == t:
            return status
    return None


def status_from_result(result) -> str:
    if result == "positive":
        return STATUS_OPTIONS[1]
    if result == "negative":
        return STATUS_OPTIONS[2]
    return STATUS_OPTIONS[3]


def display_config(data: dict) -> None:
    profile = data.get("perfil") or "sesión limpia"
    aviso = ""
    if data.get("perfil") and not Path(data["perfil"]).is_dir():
        aviso = "  [!] la carpeta no existe"
    print(f"Navegador: {data['navegador']}  |  Perfil: {profile}{aviso}")


def display_summary(data: dict) -> None:
    """Equivale a la barra de estado de la UI."""
    results = data["resultados"]
    counts = {e: 0 for e in STATUS_OPTIONS}
    for choice in results.values():
        counts[choice["estado"]] = counts.get(choice["estado"], 0) + 1
    total = len(results)

    print(
        f"\nRevisadas: {total - counts['Pendiente']}/{total}  |  "
        f"Encontradas: {counts['Línea encontrada']}  |  "
        f"Sin línea: {counts['Sin línea']}  |  "
        f"Errores: {counts['No se pudo revisar']}\n"
    )


def list_companies(data: dict, filter_text: str = "", status=None) -> None:
    """Equivale a la tabla de la UI con sus dos filtros."""
    names = {n for n, _u, _a in search_carriers(filter_text)} if filter_text else None

    rows = []
    for name, _url in CARRIERS:
        if names is not None and name not in names:
            continue
        choice = data["resultados"][name]
        if status and choice["estado"] != status:
            continue
        rows.append((name, choice["estado"], choice["notas"].replace("\n", " ")))

    if not rows:
        print("Sin resultados.")
        return

    name_width = max(len("Compañía"), *(len(f[0]) for f in rows))
    status_width = max(len(e) for e in STATUS_OPTIONS)

    print(f"  {'Compañía':<{name_width}}  {'Estado':<{status_width}}  Notas")
    for name, status, notes in rows:
        print(f"{status_indicator(status)} {name:<{name_width}}  {status:<{status_width}}  {notes}")

    display_summary(data)


def list_profiles(data: dict) -> None:
    profiles = detect_profiles(data["navegador"])
    print(f"Perfiles de {data['navegador']}:")

    if not profiles:
        print("  (no encontré ninguno; usa --perfil RUTA)")
        return

    for name, path in profiles:
        marker = "*" if str(path) == data.get("perfil") else " "
        print(f" {marker} {name}  ->  {path}")


def configure_interactively(data: dict) -> None:
    print("Navegador:")
    for i, name in enumerate(BROWSERS, 1):
        print(f"  [{i}] {name}")

    choice = input(
        f"Elige [1-{len(BROWSERS)}] (Enter = {data['navegador']}): "
    ).strip()

    if choice.isdigit() and 1 <= int(choice) <= len(BROWSERS):
        new_browser = BROWSERS[int(choice) - 1]
        if new_browser != data["navegador"]:
            data["navegador"] = new_browser
            data["perfil"] = ""  

    profiles = detect_profiles(data["navegador"])

    print(f"\nPerfiles de {data['navegador']}:")
    print("  [0] Sin perfil (sesión limpia)")
    for i, (name, path) in enumerate(profiles, 1):
        print(f"  [{i}] {name}  ({path})")
    print("  [r] Escribir la ruta a mano")

    choice = input("Elige (Enter = dejar como está): ").strip().lower()

    if choice == "0":
        data["perfil"] = ""
    elif choice.isdigit() and 1 <= int(choice) <= len(profiles):
        data["perfil"] = str(profiles[int(choice) - 1][1])
    elif choice == "r":
        path = input("Ruta de la carpeta del perfil: ").strip()
        if path:
            data["perfil"] = str(Path(path).expanduser())


def create_runner(data: dict) -> CheckerRunner:
    runner = CheckerRunner()
    runner.configure(data["navegador"], data["perfil"])
    return runner


def close_runner(runner: CheckerRunner) -> None:
    print("\n[>] Cerrando navegador...")
    runner.close()
    print("[<] Navegador cerrado.")

def ensure_curp(data: dict, path) -> bool:
    if not data["curp"]:
        data["curp"] = input("Escribe tu CURP: ").strip().upper()

    if not data["curp"]:
        print("No hay una CURP capturada.")
        return False

    if len(data["curp"]) != 18:
        print("[!] La CURP normalmente tiene 18 caracteres.")

    save_progress(data, path)
    return True


def resolve_company(text: str):
    normalized_text = text.strip().lower()

    for name, url in CARRIERS:
        if name.lower() == normalized_text:
            return name, url

    coincidencias = {}
    for name, url, _alias in search_carriers(text):
        coincidencias[name] = url

    if len(coincidencias) == 1:
        return next(iter(coincidencias.items()))

    if not coincidencias:
        print(f'No encontré "{text}" en el directorio.')
    else:
        print(f'"{text}" coincide con varias compañías:')
        for name in coincidencias:
            print(f"  - {name}")
    return None


def prompt_status():
    while True:
        choice = input(
            "[1] Línea encontrada  "
            "[2] Sin línea  "
            "[3] No se pudo revisar  "
            "[s] Saltar  "
            "[q] Guardar y salir: "
        ).strip().lower()

        if choice == "q":
            return EXIT
        if choice == "s":
            return None
        if choice in ("1", "2", "3"):
            return STATUS_OPTIONS[int(choice)]

        print("Opción no válida.")


def check_company(runner, data: dict, path, name: str, url: str) -> bool:
    print(f"[>] {url}")

    if copy_to_clipboard(data["curp"]):
        print("[>] CURP copiada al portapapeles.")
    else:
        print("[!] No pude copiar la CURP al portapapeles.")

    try:
        result = runner.execute(name, data["curp"])
        print(f"[<] Resultado técnico: {result}")

        if result in ("positive", "negative"):
            status = status_from_result(result)
            print(f"[<] Estado: {status}")
        else:
            print("\nNo se pudo determinar automáticamente el resultado.")
            status = prompt_status()

            if status is EXIT:
                save_progress(data, path)
                print("Progreso guardado.")
                return False
            if status is None:
                return True  # saltar sin cambiar nada

        previous_notes = data["resultados"][name]["notas"]
        notes = input("Notas (Enter = conservar): ").strip() or previous_notes

        record_status(data, name, status, notes)
        save_progress(data, path)
        print("[OK] Progreso guardado.")
        return True

    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario.")
        save_progress(data, path)
        print("Progreso guardado.")
        return False

    except Exception as e:
        print(f"[!] Error al revisar {name}:")
        print(f"    {type(e).__name__}: {e}")

        record_status(data, name, STATUS_OPTIONS[3], f"{type(e).__name__}: {e}")
        save_progress(data, path)
        print("[!] Estado guardado como 'No se pudo revisar'.")
        return True


def process_all(data: dict, path, pending_only: bool = True) -> None:
    if not ensure_curp(data, path):
        return

    pendientes = [
        (name, url)
        for name, url in CARRIERS
        if not pending_only
        or data["resultados"][name]["estado"] == STATUS_OPTIONS[0]
    ]

    if not pendientes:
        print(
            "No quedan compañías pendientes. "
            "Usa --reiniciar para volver a revisar todas."
        )
        return

    print(f"\n{len(pendientes)} compañías por revisar.")
    print(f"CURP: {data['curp']}")
    display_config(data)
    print()

    runner = create_runner(data)

    try:
        for i, (name, url) in enumerate(pendientes, 1):
            print("=" * 60)
            print(f"[{i}/{len(pendientes)}] {name}")

            if not check_company(runner, data, path, name, url):
                break
    finally:
        close_runner(runner)

    display_summary(data)


def open_company(data: dict, path, text: str) -> None:
    company = resolve_company(text)
    if company is None:
        return

    if not ensure_curp(data, path):
        return

    name, url = company
    display_config(data)
    print()

    runner = create_runner(data)

    try:
        print("=" * 60)
        print(name)
        check_company(runner, data, path, name, url)
    finally:
        close_runner(runner)

    display_summary(data)


def set_company_status(data: dict, path, text: str, status_text: str, notes) -> None:
    company = resolve_company(text)
    if company is None:
        return

    status = parse_status(status_text)
    if status is None:
        print("Estado no válido. Usa: pendiente, encontrada, sin o error.")
        return

    name, _url = company
    record_status(data, name, status, notes)

    save_progress(data, path)
    print(f"{status_indicator(status)} {name}: {status}")


def search_company(search_name: str) -> None:
    results = search_carriers(search_name)

    if not results:
        print(f'No encontré "{search_name}" en el directorio.')
        return

    for name, url, alias in results:
        if alias:
            print(
                f'"{alias}" se revisa en "{name}" '
                f"(usa la red de Altán) -> {url}"
            )
        else:
            print(f"{name} -> {url}")


def export_csv(data: dict, destination: str) -> None:
    with open(destination, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Compañía", "Estado", "Notas"])

        for name, _url in CARRIERS:
            choice = data["resultados"][name]
            writer.writerow([name, choice["estado"], choice["notas"]])

    print(f"Exportado a {destination}")

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Consulta en qué compañías tienes líneas registradas a tu "
            "CURP. Sin argumentos revisa las compañías pendientes."
        )
    )

    revision = parser.add_argument_group("revisión")
    revision.add_argument(
        "--reiniciar", dest="restart", action="store_true",
        help="Vuelve a revisar todas las compañías, no solo las pendientes.",
    )
    revision.add_argument(
        "--abrir", dest="open_company", metavar="NOMBRE",
        help="Revisa solo esa compañía.",
    )
    revision.add_argument(
        "--marcar", dest="set_company_status", nargs=2, metavar=("COMPAÑÍA", "ESTADO"),
        help="Cambia el estado a mano: pendiente, encontrada, sin o error.",
    )
    revision.add_argument(
        "--notas", dest="notes", metavar="TEXTO",
        help="Notas para usar junto con --marcar.",
    )

    consulta = parser.add_argument_group("consulta")
    consulta.add_argument(
        "--lista", dest="list_companies", action="store_true",
        help="Muestra la tabla de compañías con estado y notas.",
    )
    consulta.add_argument(
        "--filtro", dest="filter_text", metavar="TEXTO",
        help="Filtra la lista por nombre de compañía.",
    )
    consulta.add_argument(
        "--estado", dest="status", metavar="ESTADO",
        help="Filtra la lista por estado: pendiente, encontrada, sin o error.",
    )
    consulta.add_argument(
        "--resumen", dest="summary", action="store_true",
        help="Solo muestra el resumen guardado y sale.",
    )
    consulta.add_argument(
        "--buscar", dest="search_carriers", metavar="NOMBRE",
        help="Busca una compañía por nombre y sale.",
    )
    consulta.add_argument(
        "--exportar", dest="export_path", metavar="ARCHIVO.csv",
        help="Exporta el progreso actual a CSV y sale.",
    )

    ajustes = parser.add_argument_group("ajustes")
    ajustes.add_argument(
        "--navegador", dest="browser", type=str.capitalize, choices=BROWSERS,
        help="Navegador a usar (al cambiarlo se quita el perfil).",
    )
    ajustes.add_argument(
        "--perfil", dest="profile", metavar="RUTA",
        help="Carpeta del perfil de sesión. 'ninguno' para sesión limpia.",
    )
    ajustes.add_argument(
        "--perfiles", dest="profiles", action="store_true",
        help="Lista los perfiles detectados del navegador actual y sale.",
    )
    ajustes.add_argument(
        "--configurar", dest="configure", action="store_true",
        help="Elige navegador y perfil de forma interactiva.",
    )
    ajustes.add_argument(
        "--limpiar", dest="clear", action="store_true",
        help="Borra la CURP guardada y sale.",
    )

    return parser


def main(argv=None):
    parser = create_parser()
    args = parser.parse_args(argv)

    data = load_progress(DEFAULT_PATH)
    data.setdefault("navegador", "Firefox")
    data.setdefault("perfil", "")

    estado_filtro = None
    if args.status:
        estado_filtro = parse_status(args.status)
        if estado_filtro is None:
            parser.error("--estado: usa pendiente, encontrada, sin o error.")

    cambio_config = (
        args.browser is not None
        or args.profile is not None
        or args.configure
    )

    if args.browser and args.browser != data["navegador"]:
        data["navegador"] = args.browser
        data["perfil"] = ""

    if args.profile is not None:
        profile = args.profile.strip()
        if profile.lower() in ("", "ninguno"):
            data["perfil"] = ""
        else:
            data["perfil"] = str(Path(profile).expanduser())

    if args.configure:
        configure_interactively(data)

    if cambio_config:
        save_progress(data, DEFAULT_PATH)
        display_config(data)

    if args.profiles:
        list_profiles(data)
        return

    # Solo se cambió la configuración: no se lanza ninguna revisión
    if cambio_config and not (args.open_company or args.restart):
        return

    # --- consultas ---
    if args.search_carriers:
        search_company(args.search_carriers)
        return

    if args.export_path:
        export_csv(data, args.export_path)
        return

    if args.summary:
        display_summary(data)
        return

    if args.list_companies or args.filter_text or args.status:
        list_companies(data, args.filter_text or "", estado_filtro)
        return

    if args.clear:
        data["curp"] = ""
        save_progress(data, DEFAULT_PATH)
        print("CURP borrada.")
        return

    if args.set_company_status:
        set_company_status(data, DEFAULT_PATH, args.set_company_status[0], args.set_company_status[1], args.notes)
        return

    if args.open_company:
        open_company(data, DEFAULT_PATH, args.open_company)
        return

    process_all(data, DEFAULT_PATH, pending_only=not args.restart)


if __name__ == "__main__":
    main()