# -*- coding: utf-8 -*-
"""Copiar texto al portapapeles en Windows/macOS/Linux sin dependencias
externas obligatorias. Se usa sobre todo desde el modo consola; el modo
GUI usa el portapapeles de Qt directamente."""

import subprocess
import sys

def copy_to_clipboard(text: str) -> bool:
    """Intenta copiar `text` al portapapeles. Regresa True si lo logró."""
    try:
        if sys.platform == "darwin":
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-8"))
            return p.returncode == 0
        elif sys.platform.startswith("win"):
            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
            p.communicate(text.encode("utf-16le"))
            return p.returncode == 0
        else:
            # Linux: probar wl-copy (Wayland), luego xclip, luego xsel
            for cmd in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
                try:
                    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                    p.communicate(text.encode("utf-8"))
                    if p.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
            return False
    except Exception:
        return False
