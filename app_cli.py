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

<<<<<<< HEAD
from carriers import CARRIERS, buscar
from clipboard import copy_to_clipboard
from checker.perfiles import NAVEGADORES, detectar_perfiles
from storage import ESTADOS, DEFAULT_PATH, cargar, guardar, registrar_estado
from checker.runner import CheckerRunner

USAR_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ

CODIGO_ESTADO = {
=======
from carriers import CARRIERS, search_carriers
from clipboard import copy_to_clipboard
from checker.profiles import BROWSERS, detect_profiles
from storage import STATUS_OPTIONS, DEFAULT_PATH, load_progress, save_progress, record_status
from checker.runner import CheckerRunner

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ

STATUS_COLORS = {
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
    "Pendiente": "33",           # naranja/amarillo
    "Línea encontrada": "32",    # verde
    "Sin línea": "90",           # gris
    "No se pudo revisar": "31",  # rojo
}

<<<<<<< HEAD
ALIAS_ESTADO = {
    "pendiente": ESTADOS[0],
    "encontrada": ESTADOS[1],
    "sin": ESTADOS[2],
    "error": ESTADOS[3],
}

SALIR = object()


def pintar(texto: str, codigo: str) -> str:
    return f"\033[{codigo}m{texto}\033[0m" if USAR_COLOR else texto


def punto(estado: str) -> str:
    return pintar("●", CODIGO_ESTADO.get(estado, "90"))


def parsear_estado(texto: str):
    t = texto.strip().lower()
    if t in ALIAS_ESTADO:
        return ALIAS_ESTADO[t]
    for estado in ESTADOS:
        if estado.lower() == t:
            return estado
    return None


def estado_desde_resultado(resultado) -> str:
    if resultado == "positive":
        return ESTADOS[1]
    if resultado == "negative":
        return ESTADOS[2]
    return ESTADOS[3]


def mostrar_config(data: dict) -> None:
    perfil = data.get("perfil") or "sesión limpia"
    aviso = ""
    if data.get("perfil") and not Path(data["perfil"]).is_dir():
        aviso = "  [!] la carpeta no existe"
    print(f"Navegador: {data['navegador']}  |  Perfil: {perfil}{aviso}")


def mostrar_resumen(data: dict) -> None:
    """Equivale a la barra de estado de la UI."""
    resultados = data["resultados"]
    conteo = {e: 0 for e in ESTADOS}
    for r in resultados.values():
        conteo[r["estado"]] = conteo.get(r["estado"], 0) + 1
    total = len(resultados)

    print(
        f"\nRevisadas: {total - conteo['Pendiente']}/{total}  |  "
        f"Encontradas: {conteo['Línea encontrada']}  |  "
        f"Sin línea: {conteo['Sin línea']}  |  "
        f"Errores: {conteo['No se pudo revisar']}\n"
    )


def listar(data: dict, filtro: str = "", estado=None) -> None:
    """Equivale a la tabla de la UI con sus dos filtros."""
    nombres = {n for n, _u, _a in buscar(filtro)} if filtro else None

    filas = []
    for nombre, _url in CARRIERS:
        if nombres is not None and nombre not in nombres:
            continue
        r = data["resultados"][nombre]
        if estado and r["estado"] != estado:
            continue
        filas.append((nombre, r["estado"], r["notas"].replace("\n", " ")))

    if not filas:
        print("Sin resultados.")
        return

    ancho_n = max(len("Compañía"), *(len(f[0]) for f in filas))
    ancho_e = max(len(e) for e in ESTADOS)

    print(f"  {'Compañía':<{ancho_n}}  {'Estado':<{ancho_e}}  Notas")
    for nombre, est, notas in filas:
        print(f"{punto(est)} {nombre:<{ancho_n}}  {est:<{ancho_e}}  {notas}")

    mostrar_resumen(data)


def listar_perfiles(data: dict) -> None:
    perfiles = detectar_perfiles(data["navegador"])
    print(f"Perfiles de {data['navegador']}:")

    if not perfiles:
        print("  (no encontré ninguno; usa --perfil RUTA)")
        return

    for nombre, ruta in perfiles:
        marca = "*" if str(ruta) == data.get("perfil") else " "
        print(f" {marca} {nombre}  ->  {ruta}")


def configurar_interactivo(data: dict) -> None:
    print("Navegador:")
    for i, nombre in enumerate(NAVEGADORES, 1):
        print(f"  [{i}] {nombre}")

    r = input(
        f"Elige [1-{len(NAVEGADORES)}] (Enter = {data['navegador']}): "
    ).strip()

    if r.isdigit() and 1 <= int(r) <= len(NAVEGADORES):
        nuevo = NAVEGADORES[int(r) - 1]
        if nuevo != data["navegador"]:
            data["navegador"] = nuevo
            data["perfil"] = ""  

    perfiles = detectar_perfiles(data["navegador"])

    print(f"\nPerfiles de {data['navegador']}:")
    print("  [0] Sin perfil (sesión limpia)")
    for i, (nombre, ruta) in enumerate(perfiles, 1):
        print(f"  [{i}] {nombre}  ({ruta})")
    print("  [r] Escribir la ruta a mano")

    r = input("Elige (Enter = dejar como está): ").strip().lower()

    if r == "0":
        data["perfil"] = ""
    elif r.isdigit() and 1 <= int(r) <= len(perfiles):
        data["perfil"] = str(perfiles[int(r) - 1][1])
    elif r == "r":
        ruta = input("Ruta de la carpeta del perfil: ").strip()
        if ruta:
            data["perfil"] = str(Path(ruta).expanduser())


def crear_runner(data: dict) -> CheckerRunner:
    runner = CheckerRunner()
    runner.configurar(data["navegador"], data["perfil"])
    return runner


def cerrar_runner(runner: CheckerRunner) -> None:
    print("\n[>] Cerrando navegador...")
    runner.cerrar()
    print("[<] Navegador cerrado.")

def asegurar_curp(data: dict, path) -> bool:
=======
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
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
    if not data["curp"]:
        data["curp"] = input("Escribe tu CURP: ").strip().upper()

    if not data["curp"]:
        print("No hay una CURP capturada.")
        return False

    if len(data["curp"]) != 18:
        print("[!] La CURP normalmente tiene 18 caracteres.")

<<<<<<< HEAD
    guardar(data, path)
    return True


def resolver_compania(texto: str):
    texto_l = texto.strip().lower()

    for nombre, url in CARRIERS:
        if nombre.lower() == texto_l:
            return nombre, url

    coincidencias = {}
    for nombre, url, _alias in buscar(texto):
        coincidencias[nombre] = url
=======
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
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)

    if len(coincidencias) == 1:
        return next(iter(coincidencias.items()))

    if not coincidencias:
<<<<<<< HEAD
        print(f'No encontré "{texto}" en el directorio.')
    else:
        print(f'"{texto}" coincide con varias compañías:')
        for nombre in coincidencias:
            print(f"  - {nombre}")
    return None


def preguntar_estado():
    """Devuelve un estado, None (saltar) o SALIR."""
    while True:
        r = input(
=======
        print(f'No encontré "{text}" en el directorio.')
    else:
        print(f'"{text}" coincide con varias compañías:')
        for name in coincidencias:
            print(f"  - {name}")
    return None


def prompt_status():
    """Devuelve un estado, None (saltar) o SALIR."""
    while True:
        choice = input(
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
            "[1] Línea encontrada  "
            "[2] Sin línea  "
            "[3] No se pudo revisar  "
            "[s] Saltar  "
            "[q] Guardar y salir: "
        ).strip().lower()

<<<<<<< HEAD
        if r == "q":
            return SALIR
        if r == "s":
            return None
        if r in ("1", "2", "3"):
            return ESTADOS[int(r)]
=======
        if choice == "q":
            return EXIT
        if choice == "s":
            return None
        if choice in ("1", "2", "3"):
            return STATUS_OPTIONS[int(choice)]
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)

        print("Opción no válida.")


<<<<<<< HEAD
def revisar(runner, data: dict, path, nombre: str, url: str) -> bool:
=======
def check_company(runner, data: dict, path, name: str, url: str) -> bool:
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
    print(f"[>] {url}")

    if copy_to_clipboard(data["curp"]):
        print("[>] CURP copiada al portapapeles.")
    else:
        print("[!] No pude copiar la CURP al portapapeles.")

    try:
<<<<<<< HEAD
        resultado = runner.ejecutar(nombre, data["curp"])
        print(f"[<] Resultado técnico: {resultado}")

        if resultado in ("positive", "negative"):
            estado = estado_desde_resultado(resultado)
            print(f"[<] Estado: {estado}")
        else:
            print("\nNo se pudo determinar automáticamente el resultado.")
            estado = preguntar_estado()

            if estado is SALIR:
                guardar(data, path)
                print("Progreso guardado.")
                return False
            if estado is None:
                return True  # saltar sin cambiar nada

        previas = data["resultados"][nombre]["notas"]
        notas = input("Notas (Enter = conservar): ").strip() or previas

        registrar_estado(data, nombre, estado, notas)
        guardar(data, path)
        print("[✓] Progreso guardado.")
=======
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
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
        return True

    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario.")
<<<<<<< HEAD
        guardar(data, path)
=======
        save_progress(data, path)
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
        print("Progreso guardado.")
        return False

    except Exception as e:
<<<<<<< HEAD
        print(f"[!] Error al revisar {nombre}:")
        print(f"    {type(e).__name__}: {e}")

        registrar_estado(data, nombre, ESTADOS[3], f"{type(e).__name__}: {e}")
        guardar(data, path)
=======
        print(f"[!] Error al revisar {name}:")
        print(f"    {type(e).__name__}: {e}")

        record_status(data, name, STATUS_OPTIONS[3], f"{type(e).__name__}: {e}")
        save_progress(data, path)
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
        print("[!] Estado guardado como 'No se pudo revisar'.")
        return True


<<<<<<< HEAD
def recorrer(data: dict, path, solo_pendientes: bool = True) -> None:
    if not asegurar_curp(data, path):
        return

    pendientes = [
        (nombre, url)
        for nombre, url in CARRIERS
        if not solo_pendientes
        or data["resultados"][nombre]["estado"] == ESTADOS[0]
=======
def process_all(data: dict, path, pending_only: bool = True) -> None:
    if not ensure_curp(data, path):
        return

    pendientes = [
        (name, url)
        for name, url in CARRIERS
        if not pending_only
        or data["resultados"][name]["estado"] == STATUS_OPTIONS[0]
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
    ]

    if not pendientes:
        print(
            "No quedan compañías pendientes. "
            "Usa --reiniciar para volver a revisar todas."
        )
        return

    print(f"\n{len(pendientes)} compañías por revisar.")
    print(f"CURP: {data['curp']}")
<<<<<<< HEAD
    mostrar_config(data)
    print()

    runner = crear_runner(data)

    try:
        for i, (nombre, url) in enumerate(pendientes, 1):
            print("=" * 60)
            print(f"[{i}/{len(pendientes)}] {nombre}")

            if not revisar(runner, data, path, nombre, url):
                break
    finally:
        cerrar_runner(runner)

    mostrar_resumen(data)


def abrir_una(data: dict, path, texto: str) -> None:
    compania = resolver_compania(texto)
    if compania is None:
        return

    if not asegurar_curp(data, path):
        return

    nombre, url = compania
    mostrar_config(data)
    print()

    runner = crear_runner(data)

    try:
        print("=" * 60)
        print(nombre)
        revisar(runner, data, path, nombre, url)
    finally:
        cerrar_runner(runner)

    mostrar_resumen(data)


def marcar(data: dict, path, texto: str, estado_txt: str, notas) -> None:
    compania = resolver_compania(texto)
    if compania is None:
        return

    estado = parsear_estado(estado_txt)
    if estado is None:
        print("Estado no válido. Usa: pendiente, encontrada, sin o error.")
        return

    nombre, _url = compania
    registrar_estado(data, nombre, estado, notas)

    guardar(data, path)
    print(f"{punto(estado)} {nombre}: {estado}")


def buscar_compania(nombre_buscado: str) -> None:
    resultados = buscar(nombre_buscado)

    if not resultados:
        print(f'No encontré "{nombre_buscado}" en el directorio.')
        return

    for nombre, url, alias in resultados:
        if alias:
            print(
                f'"{alias}" se revisa en "{nombre}" '
                f"(usa la red de Altán) -> {url}"
            )
        else:
            print(f"{nombre} -> {url}")


def exportar_csv(data: dict, destino: str) -> None:
    with open(destino, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Compañía", "Estado", "Notas"])

        for nombre, _url in CARRIERS:
            r = data["resultados"][nombre]
            writer.writerow([nombre, r["estado"], r["notas"]])

    print(f"Exportado a {destino}")


# ---------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------

def crear_parser() -> argparse.ArgumentParser:
=======
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
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
    parser = argparse.ArgumentParser(
        description=(
            "Consulta en qué compañías tienes líneas registradas a tu "
            "CURP. Sin argumentos revisa las compañías pendientes."
        )
    )

    revision = parser.add_argument_group("revisión")
    revision.add_argument(
<<<<<<< HEAD
        "--reiniciar", action="store_true",
        help="Vuelve a revisar todas las compañías, no solo las pendientes.",
    )
    revision.add_argument(
        "--abrir", metavar="NOMBRE",
        help="Revisa solo esa compañía.",
    )
    revision.add_argument(
        "--marcar", nargs=2, metavar=("COMPAÑÍA", "ESTADO"),
        help="Cambia el estado a mano: pendiente, encontrada, sin o error.",
    )
    revision.add_argument(
        "--notas", metavar="TEXTO",
=======
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
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
        help="Notas para usar junto con --marcar.",
    )

    consulta = parser.add_argument_group("consulta")
    consulta.add_argument(
<<<<<<< HEAD
        "--lista", action="store_true",
        help="Muestra la tabla de compañías con estado y notas.",
    )
    consulta.add_argument(
        "--filtro", metavar="TEXTO",
        help="Filtra la lista por nombre de compañía.",
    )
    consulta.add_argument(
        "--estado", metavar="ESTADO",
        help="Filtra la lista por estado: pendiente, encontrada, sin o error.",
    )
    consulta.add_argument(
        "--resumen", action="store_true",
        help="Solo muestra el resumen guardado y sale.",
    )
    consulta.add_argument(
        "--buscar", metavar="NOMBRE",
        help="Busca una compañía por nombre y sale.",
    )
    consulta.add_argument(
        "--exportar", metavar="ARCHIVO.csv",
=======
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
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
        help="Exporta el progreso actual a CSV y sale.",
    )

    ajustes = parser.add_argument_group("ajustes")
    ajustes.add_argument(
<<<<<<< HEAD
        "--navegador", type=str.capitalize, choices=NAVEGADORES,
        help="Navegador a usar (al cambiarlo se quita el perfil).",
    )
    ajustes.add_argument(
        "--perfil", metavar="RUTA",
        help="Carpeta del perfil de sesión. 'ninguno' para sesión limpia.",
    )
    ajustes.add_argument(
        "--perfiles", action="store_true",
        help="Lista los perfiles detectados del navegador actual y sale.",
    )
    ajustes.add_argument(
        "--configurar", action="store_true",
        help="Elige navegador y perfil de forma interactiva.",
    )
    ajustes.add_argument(
        "--limpiar", action="store_true",
=======
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
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
        help="Borra la CURP guardada y sale.",
    )

    return parser


def main(argv=None):
<<<<<<< HEAD
    parser = crear_parser()
    args = parser.parse_args(argv)

    data = cargar(DEFAULT_PATH)
=======
    parser = create_parser()
    args = parser.parse_args(argv)

    data = load_progress(DEFAULT_PATH)
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
    data.setdefault("navegador", "Firefox")
    data.setdefault("perfil", "")

    estado_filtro = None
<<<<<<< HEAD
    if args.estado:
        estado_filtro = parsear_estado(args.estado)
        if estado_filtro is None:
            parser.error("--estado: usa pendiente, encontrada, sin o error.")

    # --- navegador y perfil (se guardan, igual que en la UI) ---
    cambio_config = (
        args.navegador is not None
        or args.perfil is not None
        or args.configurar
    )

    if args.navegador and args.navegador != data["navegador"]:
        data["navegador"] = args.navegador
        data["perfil"] = ""

    if args.perfil is not None:
        perfil = args.perfil.strip()
        if perfil.lower() in ("", "ninguno"):
            data["perfil"] = ""
        else:
            data["perfil"] = str(Path(perfil).expanduser())

    if args.configurar:
        configurar_interactivo(data)

    if cambio_config:
        guardar(data, DEFAULT_PATH)
        mostrar_config(data)

    if args.perfiles:
        listar_perfiles(data)
        return

    # Solo se cambió la configuración: no se lanza ninguna revisión
    if cambio_config and not (args.abrir or args.reiniciar):
        return

    # --- consultas ---
    if args.buscar:
        buscar_compania(args.buscar)
        return

    if args.exportar:
        exportar_csv(data, args.exportar)
        return

    if args.resumen:
        mostrar_resumen(data)
        return

    if args.lista or args.filtro or args.estado:
        listar(data, args.filtro or "", estado_filtro)
        return

    # --- acciones sobre los datos ---
    if args.limpiar:
        data["curp"] = ""
        guardar(data, DEFAULT_PATH)
        print("CURP borrada.")
        return

    if args.marcar:
        marcar(data, DEFAULT_PATH, args.marcar[0], args.marcar[1], args.notas)
        return

    # --- revisión ---
    if args.abrir:
        abrir_una(data, DEFAULT_PATH, args.abrir)
        return

    recorrer(data, DEFAULT_PATH, solo_pendientes=not args.reiniciar)
=======
    if args.status:
        estado_filtro = parse_status(args.status)
        if estado_filtro is None:
            parser.error("--estado: usa pendiente, encontrada, sin o error.")

    #  navegador y perfil (se guardan, igual que en la UI) 
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

    # --- revisión ---
    if args.open_company:
        open_company(data, DEFAULT_PATH, args.open_company)
        return

    process_all(data, DEFAULT_PATH, pending_only=not args.restart)
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)


if __name__ == "__main__":
    main()