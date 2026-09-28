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

from carriers import CARRIERS, buscar
from clipboard import copy_to_clipboard
from checker.perfiles import NAVEGADORES, detectar_perfiles
from storage import ESTADOS, DEFAULT_PATH, cargar, guardar, registrar_estado
from checker.runner import CheckerRunner

USAR_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ

CODIGO_ESTADO = {
    "Pendiente": "33",           # naranja/amarillo
    "Línea encontrada": "32",    # verde
    "Sin línea": "90",           # gris
    "No se pudo revisar": "31",  # rojo
}

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
    if not data["curp"]:
        data["curp"] = input("Escribe tu CURP: ").strip().upper()

    if not data["curp"]:
        print("No hay una CURP capturada.")
        return False

    if len(data["curp"]) != 18:
        print("[!] La CURP normalmente tiene 18 caracteres.")

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

    if len(coincidencias) == 1:
        return next(iter(coincidencias.items()))

    if not coincidencias:
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
            "[1] Línea encontrada  "
            "[2] Sin línea  "
            "[3] No se pudo revisar  "
            "[s] Saltar  "
            "[q] Guardar y salir: "
        ).strip().lower()

        if r == "q":
            return SALIR
        if r == "s":
            return None
        if r in ("1", "2", "3"):
            return ESTADOS[int(r)]

        print("Opción no válida.")


def revisar(runner, data: dict, path, nombre: str, url: str) -> bool:
    print(f"[>] {url}")

    if copy_to_clipboard(data["curp"]):
        print("[>] CURP copiada al portapapeles.")
    else:
        print("[!] No pude copiar la CURP al portapapeles.")

    try:
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
        return True

    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario.")
        guardar(data, path)
        print("Progreso guardado.")
        return False

    except Exception as e:
        print(f"[!] Error al revisar {nombre}:")
        print(f"    {type(e).__name__}: {e}")

        registrar_estado(data, nombre, ESTADOS[3], f"{type(e).__name__}: {e}")
        guardar(data, path)
        print("[!] Estado guardado como 'No se pudo revisar'.")
        return True


def recorrer(data: dict, path, solo_pendientes: bool = True) -> None:
    if not asegurar_curp(data, path):
        return

    pendientes = [
        (nombre, url)
        for nombre, url in CARRIERS
        if not solo_pendientes
        or data["resultados"][nombre]["estado"] == ESTADOS[0]
    ]

    if not pendientes:
        print(
            "No quedan compañías pendientes. "
            "Usa --reiniciar para volver a revisar todas."
        )
        return

    print(f"\n{len(pendientes)} compañías por revisar.")
    print(f"CURP: {data['curp']}")
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
    parser = argparse.ArgumentParser(
        description=(
            "Consulta en qué compañías tienes líneas registradas a tu "
            "CURP. Sin argumentos revisa las compañías pendientes."
        )
    )

    revision = parser.add_argument_group("revisión")
    revision.add_argument(
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
        help="Notas para usar junto con --marcar.",
    )

    consulta = parser.add_argument_group("consulta")
    consulta.add_argument(
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
        help="Exporta el progreso actual a CSV y sale.",
    )

    ajustes = parser.add_argument_group("ajustes")
    ajustes.add_argument(
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
        help="Borra la CURP guardada y sale.",
    )

    return parser


def main(argv=None):
    parser = crear_parser()
    args = parser.parse_args(argv)

    data = cargar(DEFAULT_PATH)
    data.setdefault("navegador", "Firefox")
    data.setdefault("perfil", "")

    estado_filtro = None
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


if __name__ == "__main__":
    main()