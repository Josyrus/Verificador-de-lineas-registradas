# -*- coding: utf-8 -*-

"""Modo consola.

Recorre el directorio de compañías, abre los portales configurados
mediante CheckerRunner, ejecuta la consulta automáticamente y guarda
el resultado.

No automatiza CAPTCHAs ni verificaciones que requieran intervención
manual.
"""

import argparse
import csv

from carriers import CARRIERS, buscar
from clipboard import copy_to_clipboard
from storage import ESTADOS, cargar, guardar
from checker.runner import CheckerRunner


OPCIONES_ESTADO = {
    "1": "Línea encontrada",
    "2": "Sin línea",
    "3": "No se pudo revisar",
    "s": None,
}


def pedir_curp_y_telefonos(data: dict) -> None:
    """Solicita la CURP y teléfonos si todavía no están guardados."""

    if not data["curp"]:
        data["curp"] = input("Escribe tu CURP: ").strip().upper()

    if not data["telefonos"]:
        tel = input(
            "Número(s) de línea a buscar "
            "(separados por coma, opcional): "
        ).strip()

        data["telefonos"] = [
            t.strip()
            for t in tel.split(",")
            if t.strip()
        ]


def mostrar_resumen(data: dict) -> None:
    """Muestra el estado actual de todas las compañías."""

    resultados = data["resultados"]

    conteo = {
        estado: 0
        for estado in ESTADOS
    }

    for resultado in resultados.values():
        estado = resultado["estado"]
        conteo[estado] = conteo.get(estado, 0) + 1

    total = len(resultados)

    print(
        f"\nProgreso: "
        f"{total - conteo['Pendiente']}/{total} "
        f"compañías revisadas"
    )

    for estado in ESTADOS:
        print(
            f"  {estado}: "
            f"{conteo.get(estado, 0)}"
        )

    print()


def mostrar_resultado(resultado: str) -> str:
    """Convierte el resultado del CheckerRunner en un estado."""

    if resultado == "positive":
        return "Línea encontrada"

    if resultado == "negative":
        return "Sin línea"

    return "No se pudo revisar"


def recorrer(
    data: dict,
    path,
    solo_pendientes: bool = True,
) -> None:

    pedir_curp_y_telefonos(data)

    guardar(data, path)

    pendientes = [
        (nombre, url)
        for nombre, url in CARRIERS
        if (
            not solo_pendientes
            or data["resultados"][nombre]["estado"]
            == "Pendiente"
        )
    ]

    if not pendientes:
        print(
            "No quedan compañías pendientes. "
            "Usa --reiniciar para volver a revisar todas."
        )
        return

    print(
        f"\n{len(pendientes)} compañías por revisar."
    )

    print(
        f"CURP: {data['curp']}"
    )

    if data["telefonos"]:
        print(
            "Buscando línea(s): "
            + ", ".join(data["telefonos"])
        )

    print()

    runner = CheckerRunner()

    try:

        for i, (nombre, url) in enumerate(
            pendientes,
            1
        ):

            print("=" * 60)

            print(
                f"[{i}/{len(pendientes)}] "
                f"{nombre}"
            )

            print(
                f"[>] {url}"
            )

            # -------------------------------------------------
            # Copiar CURP
            # -------------------------------------------------

            copiado = copy_to_clipboard(
                data["curp"]
            )

            if copiado:
                print(
                    "[>] CURP copiada al portapapeles."
                )
            else:
                print(
                    "[!] No pude copiar la CURP "
                    "al portapapeles."
                )

            # -------------------------------------------------
            # Ejecutar checker
            # -------------------------------------------------

            try:

                resultado = runner.ejecutar(
                    nombre,
                    data["curp"],
                    data["telefonos"],
                )

                print(
                    f"[<] Resultado técnico: "
                    f"{resultado}"
                )

                estado = mostrar_resultado(
                    resultado
                )

                print(
                    f"[<] Estado: {estado}"
                )

                # ---------------------------------------------
                # Permitir saltar un resultado automático
                # ---------------------------------------------

                if resultado not in (
                    "positive",
                    "negative",
                ):

                    print(
                        "\nNo se pudo determinar "
                        "automáticamente el resultado."
                    )

                    while True:

                        respuesta = input(
                            "[1] Línea encontrada  "
                            "[2] Sin línea  "
                            "[3] No se pudo revisar  "
                            "[s] Saltar  "
                            "[q] Guardar y salir: "
                        ).strip().lower()

                        if respuesta == "q":
                            guardar(data, path)
                            print(
                                "Progreso guardado."
                            )
                            return

                        if respuesta in OPCIONES_ESTADO:
                            break

                        print(
                            "Opción no válida."
                        )

                    if respuesta == "s":
                        continue

                    estado = OPCIONES_ESTADO[
                        respuesta
                    ]

                # ---------------------------------------------
                # Notas
                # ---------------------------------------------

                notas = input(
                    "Notas (opcional): "
                ).strip()

                data["resultados"][nombre] = {
                    "estado": estado,
                    "notas": notas,
                }

                guardar(data, path)

                print(
                    "[✓] Progreso guardado."
                )

            except KeyboardInterrupt:

                print(
                    "\n\nInterrumpido por el usuario."
                )

                guardar(data, path)

                print(
                    "Progreso guardado."
                )

                return

            except Exception as e:

                print(
                    f"[!] Error al revisar "
                    f"{nombre}:"
                )

                print(
                    f"    {type(e).__name__}: {e}"
                )

                data["resultados"][nombre] = {
                    "estado": "No se pudo revisar",
                    "notas": (
                        f"{type(e).__name__}: {e}"
                    ),
                }

                guardar(data, path)

                print(
                    "[!] Estado guardado como "
                    "'No se pudo revisar'."
                )

    finally:

        print(
            "\n[>] Cerrando navegador..."
        )

        runner.cerrar()

        print(
            "[<] Navegador cerrado."
        )

    mostrar_resumen(data)


def buscar_compania(
    nombre_buscado: str
) -> None:

    resultados = buscar(
        nombre_buscado
    )

    if not resultados:

        print(
            f'No encontré "{nombre_buscado}" '
            "en el directorio."
        )

        return

    for nombre, url, alias in resultados:

        if alias:

            print(
                f'"{alias}" se revisa en '
                f'"{nombre}" '
                f"(usa la red de Altán) -> "
                f"{url}"
            )

        else:

            print(
                f"{nombre} -> {url}"
            )


def exportar_csv(
    data: dict,
    destino: str,
) -> None:

    with open(
        destino,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "Compañía",
                "Estado",
                "Notas",
            ]
        )

        for nombre, _url in CARRIERS:

            resultado = (
                data["resultados"]
                [nombre]
            )

            writer.writerow(
                [
                    nombre,
                    resultado["estado"],
                    resultado["notas"],
                ]
            )

    print(
        f"Exportado a {destino}"
    )


def main(argv=None):

    parser = argparse.ArgumentParser(
        description=(
            "Consulta en qué compañías tienes "
            "líneas registradas a tu CURP. "
            "Utiliza los portales configurados "
            "en CheckerRunner."
        )
    )

    parser.add_argument(
        "--reiniciar",
        action="store_true",
        help=(
            "Vuelve a revisar todas las compañías, "
            "no solo las pendientes."
        ),
    )

    parser.add_argument(
        "--resumen",
        action="store_true",
        help=(
            "Solo muestra el resumen guardado "
            "y sale."
        ),
    )

    parser.add_argument(
        "--exportar",
        metavar="ARCHIVO.csv",
        help=(
            "Exporta el progreso actual a CSV "
            "y sale."
        ),
    )

    parser.add_argument(
        "--buscar",
        metavar="NOMBRE",
        help=(
            "Busca una compañía por nombre "
            "y sale."
        ),
    )

    args = parser.parse_args(argv)

    from storage import DEFAULT_PATH

    data = cargar(DEFAULT_PATH)

    if args.buscar:

        buscar_compania(
            args.buscar
        )

        return

    if args.exportar:

        exportar_csv(
            data,
            args.exportar
        )

        return

    if args.resumen:

        mostrar_resumen(data)

        return

    recorrer(
        data,
        DEFAULT_PATH,
        solo_pendientes=not args.reiniciar,
    )


if __name__ == "__main__":
    main()