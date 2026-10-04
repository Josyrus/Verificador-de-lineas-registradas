from __future__ import annotations

import zlib
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QPushButton


RESOURCE_DIR = Path(__file__).resolve().parent.parent / "media" / "svg"

STATUS_COLORS = {
    "Pendiente": "#f5a623",
    "Línea encontrada": "#4caf50",
    "Sin línea": "#9e9e9e",
    "No se pudo revisar": "#e57373",
}

AVATAR_COLORS = [
    "#E57373", "#64B5F6", "#81C784", "#FFB74D", "#BA68C8",
    "#4DB6AC", "#F06292", "#9575CD", "#4FC3F7", "#AED581",
    "#FFD54F", "#A1887F", "#90A4AE", "#7986CB", "#4DD0E1",
    "#DCE775", "#FF8A65", "#F06060", "#BDBDBD", "#FFF176",
]


class IconButton(QPushButton):
    def __init__(self, text: str, icon_name: str, *, right_icon: bool = False, parent=None):
        super().__init__(text, parent)
        self.setIcon(QIcon(str(RESOURCE_DIR / icon_name)))
        if right_icon:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)


def status_icon(status: str, size: int = 10) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(STATUS_COLORS.get(status, "#9e9e9e")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(0, 0, size, size)
    painter.end()
    return QIcon(pixmap)


def avatar(name: str, size: int = 20) -> QLabel:
    label = QLabel()
    label.setFixedSize(size, size)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    if name in {"Redes ALTÁN", "Freedompop"}:
        label.setPixmap(QIcon(str(RESOURCE_DIR / "señal.svg")).pixmap(size, size))
        return label

    pixmap = QPixmap(size, size)
    color = AVATAR_COLORS[zlib.crc32(name.encode()) % len(AVATAR_COLORS)]
    pixmap.fill(color)

    painter = QPainter(pixmap)
    font = QFont()
    font.setBold(True)
    font.setPointSize(max(1, size // 2))
    painter.setFont(font)
    painter.setPen(Qt.GlobalColor.white)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, name[0].upper())
    painter.end()

    label.setPixmap(pixmap)
    return label
