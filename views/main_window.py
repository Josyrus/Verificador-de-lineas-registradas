from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPlainTextEdit, QPushButton, QStatusBar,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView,
)

from carriers import PORTAL_ALIASES
from checker.profiles import BROWSERS
from storage import STATUS_OPTIONS
from views.widgets import IconButton, RESOURCE_DIR, STATUS_COLORS, avatar, status_icon

COL_COMPANY, COL_STATUS, COL_NOTES, COL_OPEN = range(4)


class MainWindow(QMainWindow):

    curp_changed = Signal(str)
    browser_changed = Signal(str)
    profile_changed = Signal(str)
    manual_profile_requested = Signal()
    clear_requested = Signal()
    open_company_requested = Signal(str)
    next_requested = Signal()
    batch_requested = Signal(str)
    status_changed = Signal(str, str)
    notes_changed = Signal(str, str)
    name_filter_changed = Signal(str)
    status_filter_changed = Signal(str)
    export_requested = Signal()

    def __init__(self, companies, data: dict):
        super().__init__()
        self.companies = companies
        self.data = data
        self._panel_company = None
        self._panel_url = ""
        self._build_ui()
        self.render_all()

    def _build_ui(self) -> None:
        self.setWindowTitle("Líneas registradas a mi CURP — consulta guiada")
        self.resize(920, 620)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        top = QHBoxLayout()
        curp_layout = QVBoxLayout()
        curp_layout.addWidget(QLabel("CURP:"))
        self.curp_input = QLineEdit(self.data.get("curp", ""))
        self.curp_input.setMaxLength(18)
        self.curp_input.setPlaceholderText("Se copia al portapapeles al abrir cada portal")
        self.curp_input.editingFinished.connect(lambda: self.curp_changed.emit(self.curp_input.text()))
        curp_layout.addWidget(self.curp_input)
        top.addLayout(curp_layout)

        profile_layout = QVBoxLayout()
        profile_layout.addWidget(QLabel("Navegador y perfil de sesión"))
        profile_row = QHBoxLayout()
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(BROWSERS)
        self.browser_combo.setCurrentText(self.data.get("navegador", BROWSERS[0]))
        self.browser_combo.currentTextChanged.connect(self.browser_changed)
        profile_row.addWidget(self.browser_combo)

        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(220)
        self.profile_combo.currentIndexChanged.connect(self._emit_profile)
        profile_row.addWidget(self.profile_combo, 1)

        self.profile_button = QPushButton("Buscar…")
        self.profile_button.clicked.connect(self.manual_profile_requested)
        profile_row.addWidget(self.profile_button)
        profile_layout.addLayout(profile_row)
        top.addLayout(profile_layout)

        self.clear_button = IconButton("Limpiar", "borrar.svg")
        self.clear_button.clicked.connect(self.clear_requested)
        top.addWidget(self.clear_button)

        self.batch_mode = QComboBox()
        self.batch_mode.addItem("Abrir Siguiente", "one")
        self.batch_mode.addItem("Ejecutar Automatizador de sitios", "all")
        top.addWidget(self.batch_mode)

        self.start_button = IconButton("Iniciar", "derecha.svg", right_icon=True)
        self.start_button.clicked.connect(self._emit_batch)
        top.addWidget(self.start_button)

        self.export_button = IconButton("Exportar CSV", "descargar.svg")
        self.export_button.clicked.connect(self.export_requested)
        top.addWidget(self.export_button)
        root.addLayout(top)

        filters = QHBoxLayout()
        self.name_filter = QLineEdit()
        self.name_filter.setPlaceholderText("Filtrar compañía…")
        self.name_filter.textChanged.connect(self.name_filter_changed)
        filters.addWidget(self.name_filter)
        filters.addWidget(QLabel("Estado:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("Todos")
        self.status_filter.addItems(STATUS_OPTIONS)
        self.status_filter.currentTextChanged.connect(self.status_filter_changed)
        filters.addWidget(self.status_filter)
        root.addLayout(filters)

        table_layout = QHBoxLayout()
        self.table = QTableWidget(len(self.companies), 4)
        self.table.setHorizontalHeaderLabels(["Compañía", "Estado", "Notas", ""])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(COL_COMPANY, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(COL_STATUS, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(COL_NOTES, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(COL_OPEN, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.cellClicked.connect(lambda row, _col: self.show_company(row))
        table_layout.addWidget(self.table)

        self.detail_panel = self._build_detail_panel()
        table_layout.addWidget(self.detail_panel)
        self.detail_panel.setVisible(False)
        root.addLayout(table_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        root.addWidget(QLabel("Esta app abre los portales oficiales de cada compañía y te ayuda a llevar el registro."))
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, activated=self.hide_detail_panel)

    def _build_detail_panel(self):
        panel = QWidget()
        panel.setFixedWidth(300)
        layout = QVBoxLayout(panel)

        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Detalles</b>"))
        header.addStretch()
        close = QPushButton("✕")
        close.setFlat(True)
        close.clicked.connect(self.hide_detail_panel)
        header.addWidget(close)
        layout.addLayout(header)

        company_row = QHBoxLayout()
        self.detail_avatar = QHBoxLayout()
        company_row.addLayout(self.detail_avatar)
        self.detail_name = QLabel()
        self.detail_name.setWordWrap(True)
        company_row.addWidget(self.detail_name, 1)
        open_button = QPushButton("Abrir")
        open_button.clicked.connect(lambda: self._panel_company and self.open_company_requested.emit(self._panel_company))
        company_row.addWidget(open_button)
        layout.addLayout(company_row)

        self.detail_url = QLabel()
        self.detail_url.setOpenExternalLinks(True)
        self.detail_url.setWordWrap(True)
        layout.addWidget(self.detail_url)
        self.detail_status = QLabel()
        layout.addWidget(self.detail_status)
        self.detail_date = QLabel()
        layout.addWidget(self.detail_date)
        layout.addWidget(QLabel("Notas"))
        self.detail_notes = QLineEdit()
        self.detail_notes.editingFinished.connect(self._save_detail_notes)
        layout.addWidget(self.detail_notes)
        layout.addWidget(QLabel("Historial"))
        self.detail_history = QLabel()
        self.detail_history.setWordWrap(True)
        layout.addWidget(self.detail_history)
        layout.addStretch()
        return panel

    def _emit_profile(self) -> None:
        self.profile_changed.emit(self.profile_combo.currentData() or "")

    def _emit_batch(self) -> None:
        self.batch_requested.emit(self.batch_mode.currentData())

    def _save_detail_notes(self) -> None:
        if self._panel_company:
            self.notes_changed.emit(self._panel_company, self.detail_notes.text())

    def load_profiles(self, profiles, selected: str) -> None:
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profile_combo.addItem("Sin perfil (sesión limpia)", "")
        for name, path in profiles:
            self.profile_combo.addItem(name, str(path))
        index = self.profile_combo.findData(selected)
        if selected and index < 0:
            self.profile_combo.addItem(Path(selected).name, selected)
            index = self.profile_combo.count() - 1
        self.profile_combo.setCurrentIndex(max(index, 0))
        self.profile_combo.setToolTip(selected)
        self.profile_combo.blockSignals(False)

    def render_all(self) -> None:
        self.curp_input.setText(self.data.get("curp", ""))
        self._populate_table()
        self.update_summary()

    def _populate_table(self) -> None:
        self.table.setRowCount(len(self.companies))
        for row, company in enumerate(self.companies):
            name, url = company.name, company.url
            container = QWidget()
            row_layout = QHBoxLayout(container)
            row_layout.setContentsMargins(5, 0, 5, 0)
            row_layout.addWidget(avatar(name))
            row_layout.addWidget(QLabel(name))
            aliases = [alias for alias, portal in PORTAL_ALIASES.items() if portal == name]
            if aliases:
                info = QLabel()
                info.setPixmap(QIcon(str(RESOURCE_DIR / "aclaracion.svg")).pixmap(20, 20))
                info.setToolTip(
                    f"{name} es el portal compartido por: {', '.join(aliases)}"
                )
                row_layout.addWidget(info)
            row_layout.addStretch()
            container.setProperty("name", name)
            container.setProperty("url", url)
            self.table.setCellWidget(row, COL_COMPANY, container)

            result = self.data["resultados"][name]
            status_combo = QComboBox()
            for status in STATUS_OPTIONS:
                status_combo.addItem(status_icon(status), status)
            status_combo.setIconSize(QSize(10, 10))
            status_combo.setCurrentText(result["estado"])
            status_combo.currentTextChanged.connect(lambda value, n=name: self.status_changed.emit(n, value))
            self.table.setCellWidget(row, COL_STATUS, status_combo)

            notes = QLineEdit(result["notas"])
            notes.editingFinished.connect(lambda n=name, w=notes: self.notes_changed.emit(n, w.text()))
            self.table.setCellWidget(row, COL_NOTES, notes)

            button = QPushButton("Abrir")
            button.clicked.connect(lambda _checked=False, n=name: self.open_company_requested.emit(n))
            self.table.setCellWidget(row, COL_OPEN, button)

    def show_company(self, row: int) -> None:
        container = self.table.cellWidget(row, COL_COMPANY)
        if container is None:
            return
        name = container.property("name")
        self._panel_company = name
        self._panel_url = container.property("url")
        while self.detail_avatar.count():
            item = self.detail_avatar.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.detail_avatar.addWidget(avatar(name))
        self.detail_name.setText(name)
        self.detail_url.setText(f'<a href="{self._panel_url}">{self._panel_url}</a>')
        aliases = [a for a, portal in PORTAL_ALIASES.items() if portal == name]
        if aliases:
            self.detail_url.setToolTip("Portal compartido por: " + ", ".join(aliases))
        self.detail_panel.setVisible(True)
        self.refresh_detail()

    def hide_detail_panel(self) -> None:
        self.detail_panel.setVisible(False)
        self._panel_company = None

    def refresh_detail(self) -> None:
        if not self._panel_company:
            return
        result = self.data["resultados"][self._panel_company]
        status = result["estado"]
        color = STATUS_COLORS.get(status, "#9e9e9e")
        self.detail_status.setText(f'<span style="color:{color};">●</span>&nbsp;{status}')
        self.detail_date.setText(f"Última verificación: {self._format_date(result.get('fecha'))}")
        if not self.detail_notes.hasFocus():
            self.detail_notes.setText(result["notas"])
        history = result.get("historial", [])
        self.detail_history.setText(
            "<br>".join(
                f"{self._format_date(item.get('fecha'))} — {item.get('estado', '')}"
                for item in reversed(history[-10:])
            ) or "Sin registros todavía."
        )

    @staticmethod
    def _format_date(value) -> str:
        try:
            return datetime.fromisoformat(value).strftime("%d/%m/%Y %H:%M")
        except (TypeError, ValueError):
            return "Nunca"

    def update_row_status(self, name: str, status: str) -> None:
        for row in range(self.table.rowCount()):
            container = self.table.cellWidget(row, COL_COMPANY)
            if container and container.property("name") == name:
                combo = self.table.cellWidget(row, COL_STATUS)
                combo.blockSignals(True)
                combo.setCurrentText(status)
                combo.blockSignals(False)
                break
        self.refresh_detail()

    def update_row_notes(self, name: str, notes: str) -> None:
        for row in range(self.table.rowCount()):
            container = self.table.cellWidget(row, COL_COMPANY)
            if container and container.property("name") == name:
                editor = self.table.cellWidget(row, COL_NOTES)
                if editor.text() != notes:
                    editor.setText(notes)
                break
        self.refresh_detail()

    def select_company(self, name: str) -> None:
        for row in range(self.table.rowCount()):
            container = self.table.cellWidget(row, COL_COMPANY)
            if container and container.property("name") == name:
                self.table.selectRow(row)
                self.table.scrollTo(self.table.model().index(row, COL_COMPANY))
                self.show_company(row)
                return

    def apply_name_filter(self, names: set[str]) -> None:
        for row in range(self.table.rowCount()):
            container = self.table.cellWidget(row, COL_COMPANY)
            name = container.property("name") if container else ""
            self.table.setRowHidden(row, name not in names)

    def apply_status_filter(self, status: str) -> None:
        normalized = status.strip().lower()
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, COL_STATUS)
            current = combo.currentText().strip().lower() if combo else ""
            hidden = normalized != "todos" and current != normalized
            self.table.setRowHidden(row, hidden)

    def update_summary(self, summary=None) -> None:
        if summary is None:
            summary = {}
            for result in self.data["resultados"].values():
                summary[result["estado"]] = summary.get(result["estado"], 0) + 1
        total = len(self.data["resultados"])
        pending = summary.get("Pendiente", 0)
        self.status_bar.showMessage(
            f"Revisadas: {total - pending}/{total} | "
            f"Encontradas: {summary.get('Línea encontrada', 0)} | "
            f"Sin línea: {summary.get('Sin línea', 0)} | "
            f"Errores: {summary.get('No se pudo revisar', 0)}"
        )

    def set_batch_active(self, active: bool) -> None:
        self.start_button.setText("Detener" if active else "Iniciar")
        self.batch_mode.setEnabled(not active)

    def show_message(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    def ask_export_path(self):
        return QFileDialog.getSaveFileName(self, "Exportar CSV", "lineas_curp.csv", "CSV (*.csv)")[0]

    @property
    def selected_company(self) -> str | None:
        return self._panel_company

    def set_status_message(self, message: str, timeout: int = 0) -> None:
        self.status_bar.showMessage(message, timeout)
