# -*- coding: utf-8 -*-
"""Modo consola. Recorre el directorio de compañías, abre cada portal en el
navegador por defecto, copia tu CURP al portapapeles para que solo la pegues,
y guarda el estado que tú le indiques (encontrada / sin línea / error)."""

import argparse
import webbrowser

from carriers import CARRIERS, buscar
from clipboard import copy_to_clipboard
from storage import ESTADOS, cargar, guardar

OPCIONES_ESTADO = {
    "1": "Línea encontrada",
    "2": "Sin línea",
    "3": "No se pudo revisar",
    "s": None,  # saltar sin cambiar estado
}


def pedir_curp_y_telefonos(data: dict) -> None:
    if not data["curp"]:
        data["curp"] = input("Escribe tu CURP: ").strip().upper()
    if not data["telefonos"]:
        tel = input("Número(s) de línea a buscar (separados por coma, opcional): ").strip()
        data["telefonos"] = [t.strip() for t in tel.split(",") if t.strip()]


def mostrar_resumen(data: dict) -> None:
    resultados = data["resultados"]
    conteo = {e: 0 for e in ESTADOS}
    for r in resultados.values():
        conteo[r["estado"]] = conteo.get(r["estado"], 0) + 1
    total = len(resultados)
    print(f"\nProgreso: {total - conteo['Pendiente']}/{total} compañías revisadas")
    for estado in ESTADOS:
        print(f"  {estado}: {conteo.get(estado, 0)}")
    print()


def recorrer(data: dict, path, solo_pendientes: bool = True) -> None:
    pedir_curp_y_telefonos(data)
    guardar(data, path)

    pendientes = [
        (nombre, url) for nombre, url in CARRIERS
        if not solo_pendientes or data["resultados"][nombre]["estado"] == "Pendiente"
    ]

    if not pendientes:
        print("No quedan compañías pendientes. Usa --reiniciar para volver a revisar todas.")
        return

    print(f"\n{len(pendientes)} compañías por revisar. CURP: {data['curp']}")
    if data["telefonos"]:
        print(f"Buscando línea(s): {', '.join(data['telefonos'])}")
    print("En cada paso se abrirá el portal y se copiará tu CURP al portapapeles.\n")

    for i, (nombre, url) in enumerate(pendientes, 1):
        print(f"[{i}/{len(pendientes)}] {nombre}")
        print(f"  {url}")
        copiado = copy_to_clipboard(data["curp"])
        if copiado:
            print("  (CURP copiada al portapapeles, solo pégala en el formulario)")
        else:
            print(f"  (no pude copiar automáticamente, tu CURP es: {data['curp']})")
        webbrowser.open(url)

        while True:
            resp = input(
                "  Resultado -> [1] Línea encontrada  [2] Sin línea  "
                "[3] No cargó/error  [s] Saltar por ahora  [q] Guardar y salir: "
            ).strip().lower()
            if resp == "q":
                guardar(data, path)
                print("Progreso guardado. Puedes continuar después.")
                return
            if resp in OPCIONES_ESTADO:
                break
            print("  Opción no válida.")

        if OPCIONES_ESTADO[resp] is not None:
            notas = input("  Notas (opcional, ej. número/fecha de vigencia): ").strip()
            data["resultados"][nombre] = {"estado": OPCIONES_ESTADO[resp], "notas": notas}
            guardar(data, path)

    mostrar_resumen(data)


def buscar_compania(nombre_buscado: str) -> None:
    resultados = buscar(nombre_buscado)
    if not resultados:
        print(f'No encontré "{nombre_buscado}" en el directorio.')
        return
    for nombre, url, alias in resultados:
        if alias:
            print(f'"{alias}" se revisa en "{nombre}" (usa la red de Altán) -> {url}')
        else:
            print(f'{nombre} -> {url}')


def exportar_csv(data: dict, destino: str) -> None:
    import csv
    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Compañía", "Estado", "Notas"])
        for nombre, _url in CARRIERS:
            r = data["resultados"][nombre]
            w.writerow([nombre, r["estado"], r["notas"]])
    print(f"Exportado a {destino}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Consulta en qué compañías tienes líneas registradas a tu CURP "
                    "(portal.crt.gob.mx). Abre cada portal oficial y te ayuda a llevar el registro; "
                    "no evita los CAPTCHA / verificaciones de cada compañía."
    )
    parser.add_argument("--reiniciar", action="store_true", help="Vuelve a recorrer todas las compañías, no solo las pendientes")
    parser.add_argument("--resumen", action="store_true", help="Solo muestra el resumen guardado y sale")
    parser.add_argument("--exportar", metavar="ARCHIVO.csv", help="Exporta el progreso actual a CSV y sale")
    parser.add_argument("--buscar", metavar="NOMBRE", help="Busca una compañía por nombre (incluye marcas que usan la red de Altán) y sale")
    args = parser.parse_args(argv)

    from storage import DEFAULT_PATH
    data = cargar(DEFAULT_PATH)

    if args.buscar:
        buscar_compania(args.buscar)
        return
    if args.exportar:
        exportar_csv(data, args.exportar)
        return
    if args.resumen:
        mostrar_resumen(data)
        return

    recorrer(data, DEFAULT_PATH, solo_pendientes=not args.reiniciar)


if __name__ == "__main__":
    main()
