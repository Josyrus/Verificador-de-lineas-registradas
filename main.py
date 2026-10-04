from __future__ import annotations

import os
import sys


def has_graphical_environment() -> bool:
    if sys.platform.startswith(("win", "darwin")):
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def main() -> None:
    force_gui = "--gui" in sys.argv
    force_cli = "--cli" in sys.argv
    use_gui = force_gui or (not force_cli and has_graphical_environment())
    argv = [arg for arg in sys.argv[1:] if arg not in {"--gui", "--cli"}]

    if use_gui:
        try:
            from app_gui import main as gui_main
            gui_main(argv)
            return
        except Exception as exc:
            print(f"No se pudo iniciar la interfaz gráfica ({exc}); usando modo consola.\n")

    from app_cli import main as cli_main
    cli_main(argv)


if __name__ == "__main__":
    main()
