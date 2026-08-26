#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Líneas registradas a mi CURP — consulta guiada (portal.crt.gob.mx)

Uso:
    python main.py            # detecta automáticamente GUI o consola
    python main.py --gui      # fuerza interfaz gráfica
    python main.py --cli      # fuerza consola
    python main.py --cli --resumen
    python main.py --cli --exportar reporte.csv

Qué hace:
    Lee el directorio de compañías telefónicas publicado por el CRT y te
    ayuda a recorrerlo: abre cada portal oficial en tu navegador, copia tu
    CURP al portapapeles y guarda el estado que tú marques (línea
    encontrada / sin línea / error) para no perder el progreso.

Qué NO hace (a propósito):
    No completa CAPTCHAs ni "flujos de verificación" por ti, ni llama
    directamente los endpoints internos de cada compañía: todos esos
    portales están protegidos contra automatización porque exponen datos
    ligados a tu identidad (CURP). Esta herramienta solo organiza y agiliza
    el recorrido manual.
"""

import os
import sys


def hay_entorno_grafico() -> bool:
    if sys.platform.startswith("win") or sys.platform == "darwin":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def main():
    forzar_gui = "--gui" in sys.argv
    forzar_cli = "--cli" in sys.argv

    usar_gui = forzar_gui or (not forzar_cli and hay_entorno_grafico())

    if usar_gui:
        try:
            import app_gui
            argv = [a for a in sys.argv if a not in ("--gui", "--cli")]
            app_gui.main(argv)
            return
        except Exception as e:
            print(f"No se pudo iniciar la interfaz gráfica ({e}); usando modo consola.\n")

    import app_cli
    argv = [a for a in sys.argv[1:] if a not in ("--gui", "--cli")]
    app_cli.main(argv)


if __name__ == "__main__":
    main()
