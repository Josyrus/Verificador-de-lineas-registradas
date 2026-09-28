# -*- coding: utf-8 -*-
"""Modo gráfico (Qt / PySide6). Muestra el directorio de compañías en una
tabla, deja marcar el estado de cada una a mano después de revisar el
portal oficial (no automatiza CAPTCHAs), y guarda/exporta el progreso."""

import sys
import zlib
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QThread, QTimer
from PySide6.QtGui import QDesktopServices, QAction, QIcon, QPixmap, QPainter, QFont, QColor, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QHeaderView, QFileDialog, QMessageBox, QStatusBar, QButtonGroup,
    QPlainTextEdit,
)
from carriers import CARRIERS, PORTAL_ALIASES, buscar
from checker.perfiles import NAVEGADORES, detectar_perfiles
from storage import ESTADOS, DEFAULT_PATH, cargar, guardar, registrar_estado
from checker.worker import CheckerWorker
from checker.runner import CheckerRunner

COL_COMPANIA, COL_ESTADO, COL_NOTAS, COL_ABRIR = range(4)

RESOURCES_DIR = Path(__file__).resolve().parent / "media/svg"

COLOR_ESTADO = {
    "Pendiente": "#f5a623",          # naranja
    "Línea encontrada": "#4caf50",   # verde
    "Sin línea": "#9e9e9e",          # gris
    "No se pudo revisar": "#e57373", # rojo
}


class IconButton(QPushButton):
    def __init__(self, text, icon, icon_position="left", parent=None):
        super().__init__(parent)

        self.setText(text)
        self.setIcon(QIcon(icon))

        if icon_position == "right":
            self.setLayoutDirection(Qt.RightToLeft)

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        self.checker_runner = CheckerRunner()
        super().__init__()
        self.threads = {} 
        self.workers = {} 
        self.setWindowTitle("Líneas registradas a mi CURP — consulta guiada")
        self.resize(920, 620)

        self.data = cargar(DEFAULT_PATH)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        fila_datos = QHBoxLayout()        

        curp_layout = QVBoxLayout()
        curp_label = QLabel("CURP: ")
        curp_layout.addWidget(curp_label)
        self.campo_curp = QLineEdit(self.data.get("curp", ""))
        self.campo_curp.setMaxLength(18)
        self.campo_curp.setPlaceholderText("Se copia al portapapeles al abrir cada portal")
        self.campo_curp.editingFinished.connect(self._guardar_datos_personales)
        curp_layout.addWidget(self.campo_curp)
        fila_datos.addLayout(curp_layout)

        perfil_layout = QVBoxLayout()
        perfil_layout.addWidget(QLabel("Navegador y perfil de sesión"))
        fila_perfil = QHBoxLayout()

        self.combo_navegador = QComboBox()
        self.combo_navegador.addItems(NAVEGADORES)
        self.combo_navegador.setCurrentText(self.data.get("navegador", NAVEGADORES[0]))
        self.combo_navegador.currentTextChanged.connect(self._cambiar_navegador)
        fila_perfil.addWidget(self.combo_navegador)

        self.combo_perfil = QComboBox()
        self.combo_perfil.setMinimumWidth(220)
        self.combo_perfil.currentIndexChanged.connect(self._cambiar_perfil)
        fila_perfil.addWidget(self.combo_perfil, 1)

        self.boton_buscar_perfil = QPushButton("Buscar…")
        self.boton_buscar_perfil.clicked.connect(self._buscar_perfil_manual)
        fila_perfil.addWidget(self.boton_buscar_perfil)

        perfil_layout.addLayout(fila_perfil)
        fila_datos.addLayout(perfil_layout)
        layout.addLayout(fila_datos) 
        self._cargar_perfiles()


        path_icono = RESOURCES_DIR / "borrar.svg"
        self.boton_limpiar = IconButton(
            "Limpiar",
            str(path_icono),
            icon_position="left"
            )
        self.boton_limpiar.clicked.connect(self._limpiar)
        fila_datos.addWidget(self.boton_limpiar)
     
        path_icono= RESOURCES_DIR / "derecha.svg"
        self.boton_siguiente = IconButton(
            "Abrir siguiente pendiente",
            str(path_icono),
            icon_position="right"
        )
        self.boton_siguiente.clicked.connect(self._abrir_siguiente_pendiente)
        fila_datos.addWidget(self.boton_siguiente)

        path_icono = RESOURCES_DIR / "descargar.svg"
        self.boton_exportar = IconButton(
            "Exportart CSV ",
            str(path_icono),
            icon_position="left"
        )
        self.boton_exportar.clicked.connect(self._exportar)
        fila_datos.addWidget(self.boton_exportar)
        
        fila_filtro = QHBoxLayout()
        self.campo_filtro = QLineEdit()
        self.campo_filtro.setPlaceholderText("Filtrar compañía…")
        self.campo_filtro.textChanged.connect(self._filtrar_nombre)
        fila_filtro.addWidget(self.campo_filtro)
        
        self.estado_combo = QComboBox()
        self.estado_combo.addItem("Todos")
        self.estado_combo.addItems(ESTADOS)
        self.estado_combo.currentTextChanged.connect(self._filtrar_estado)
        estado_texto= QLabel("Estado: ")    
        fila_filtro.addWidget (estado_texto)
        fila_filtro.addWidget(self.estado_combo)

        layout.addLayout(fila_filtro)
        
        dark_mode_button = QPushButton("Darkmode")
        #layout.addWidget()

        #Tabla
        
        layout_tabla_e_info = QHBoxLayout()
        self.tabla = QTableWidget(len(CARRIERS), 4)
        self.tabla.setHorizontalHeaderLabels(["Compañía", "Estado", "Notas", ""])
        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_COMPANIA, 
            QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_ESTADO, 
            QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_NOTAS, 
            QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(
            COL_ABRIR, 
            QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout_tabla_e_info.addWidget(self.tabla)
        
        # Panel lateral de detalles: oculto hasta que se hace clic en una fila
        self._panel_nombre = None
        self._panel_url = ""
        self.info_compania_qwidget = self._construir_panel()
        layout_tabla_e_info.addWidget(self.info_compania_qwidget)
        self.info_compania_qwidget.setVisible(False)

        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.cellClicked.connect(lambda fila, _col: self._mostrar_panel(fila))
        # con el panel abierto, moverse con las flechas también lo actualiza
        self.tabla.currentCellChanged.connect(self._fila_actual_cambio)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, activated=self._ocultar_panel)

        layout.addLayout(layout_tabla_e_info)
        
        self._poblar_tabla()

        self.barra_estado = QStatusBar()
        self.setStatusBar(self.barra_estado)
        self._actualizar_resumen()

        aviso = QLabel(
            "Esta app abre los portales oficiales de cada compañía y te ayuda a llevar el registro. "
            "No completa CAPTCHAs ni formularios por ti: cada compañía verifica la identidad a su manera."
        )
        aviso.setWordWrap(True)
        aviso.setStyleSheet("color: #666; font-size: 11px; padding-top: 4px;")
        layout.addWidget(aviso)

    # ---------- panel lateral de detalles ----------

    def _construir_panel(self):
        panel = QWidget()
        panel.setFixedWidth(300)
        v = QVBoxLayout(panel)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(8)

        cab = QHBoxLayout()
        titulo = QLabel("<b>Detalles</b>")
        cerrar = QPushButton("✕")
        cerrar.setFlat(True)
        cerrar.setFixedWidth(28)
        cerrar.setToolTip("Cerrar (Esc)")
        cerrar.clicked.connect(self._ocultar_panel)
        cab.addWidget(titulo)
        cab.addStretch()
        cab.addWidget(cerrar)
        v.addLayout(cab)

        fila = QHBoxLayout()
        fila.setSpacing(6)
        self.panel_avatar_layout = QHBoxLayout()
        self.panel_nombre = QLabel("")
        self.panel_nombre.setWordWrap(True)
        self.panel_nombre.setStyleSheet("font-weight: bold;")
        self.panel_abrir = QPushButton("Abrir")
        self.panel_abrir.clicked.connect(
            lambda: self._panel_nombre and self._abrir_portal(self._panel_nombre, self._panel_url)
        )
        fila.addLayout(self.panel_avatar_layout)
        fila.addWidget(self.panel_nombre, 1)
        fila.addWidget(self.panel_abrir)
        v.addLayout(fila)

        self.panel_url_label = QLabel("")
        self.panel_url_label.setOpenExternalLinks(True)
        self.panel_url_label.setWordWrap(True)
        self.panel_url_label.setStyleSheet("font-size: 11px;")
        v.addWidget(self.panel_url_label)

        # Redes ALTÁN agrupa decenas de proveedores: lista con scroll y altura acotada
        self.panel_alias = QPlainTextEdit()
        self.panel_alias.setReadOnly(True)
        self.panel_alias.setMaximumHeight(90)
        self.panel_alias.setFrameShape(QPlainTextEdit.Shape.NoFrame)
        self.panel_alias.setStyleSheet("background: transparent; color: #666; font-size: 11px;")
        v.addWidget(self.panel_alias)

        self.panel_estado = QLabel("")
        self.panel_estado.setTextFormat(Qt.TextFormat.RichText)
        self.panel_fecha = QLabel("")
        for etiqueta, valor in (("Estado actual", self.panel_estado),
                                ("Última verificación", self.panel_fecha)):
            f = QHBoxLayout()
            f.setSpacing(6)
            f.addWidget(QLabel(etiqueta))
            f.addStretch()
            f.addWidget(valor)
            v.addLayout(f)

        v.addWidget(QLabel("Notas"))
        self.panel_notas = QLineEdit()
        self.panel_notas.setPlaceholderText("Añade una nota sobre esta consulta...")
        self.panel_notas.editingFinished.connect(self._panel_guardar_notas)
        v.addWidget(self.panel_notas)

        v.addWidget(QLabel("Historial"))
        self.panel_historial = QLabel("")
        self.panel_historial.setTextFormat(Qt.TextFormat.RichText)
        self.panel_historial.setWordWrap(True)
        self.panel_historial.setAlignment(Qt.AlignmentFlag.AlignTop)
        v.addWidget(self.panel_historial)

        v.addStretch()
        return panel

    def _datos_fila(self, fila):
        contenedor = self.tabla.cellWidget(fila, COL_COMPANIA)
        if contenedor is None:
            return None
        return contenedor.property("nombre"), contenedor.property("url")

    def _mostrar_panel(self, fila):
        datos = self._datos_fila(fila)
        if datos is None:
            return
        nombre, url = datos
        if nombre != self._panel_nombre:
            self.panel_notas.clearFocus()  # guarda la nota pendiente de la compañía anterior
            self._panel_nombre, self._panel_url = nombre, url
            # el avatar se recrea porque un QLabel no puede estar en dos layouts
            while self.panel_avatar_layout.count():
                w = self.panel_avatar_layout.takeAt(0).widget()
                if w is not None:
                    w.deleteLater()
            self.panel_avatar_layout.addWidget(self.crear_avatar(nombre))
            self.panel_nombre.setText(nombre)
            self.panel_url_label.setText(f'<a href="{url}">{url}</a>')
            alias = [a for a, portal in PORTAL_ALIASES.items() if portal == nombre]
            self.panel_alias.setPlainText(
                f"Incluye {len(alias)} proveedores: " + ", ".join(alias) if alias else "")
            self.panel_alias.setVisible(bool(alias))
        self._refrescar_panel()
        self.info_compania_qwidget.setVisible(True)

    def _fila_actual_cambio(self, fila, _col, _fila_prev, _col_prev):
        if fila >= 0 and self.info_compania_qwidget.isVisible():
            self._mostrar_panel(fila)

    def _ocultar_panel(self):
        self.panel_notas.clearFocus()
        self.info_compania_qwidget.setVisible(False)
        self._panel_nombre = None

    @staticmethod
    def _formatear_fecha(iso):
        try:
            return datetime.fromisoformat(iso).strftime("%d/%m/%Y %H:%M")
        except (TypeError, ValueError):
            return "Nunca"

    def _refrescar_panel(self):
        if not self._panel_nombre:
            return
        r = self.data["resultados"][self._panel_nombre]
        self.panel_estado.setText(self.texto_estado_con_punto(r["estado"]))
        self.panel_fecha.setText(self._formatear_fecha(r.get("fecha")))
        if not self.panel_notas.hasFocus():
            self.panel_notas.setText(r["notas"])
        historial = r.get("historial", [])
        if historial:
            self.panel_historial.setText("<br>".join(
                f'{self._formatear_fecha(h["fecha"])} — {self.texto_estado_con_punto(h["estado"])}'
                for h in reversed(historial[-10:])
            ))
        else:
            self.panel_historial.setText("Sin registros todavía.")

    def _panel_guardar_notas(self):
        if self._panel_nombre:
            self._cambiar_notas(self._panel_nombre, self.panel_notas.text())

    def _sincronizar_notas_tabla(self, nombre, texto):
        for row in range(self.tabla.rowCount()):
            c = self.tabla.cellWidget(row, COL_COMPANIA)
            if c is not None and c.property("nombre") == nombre:
                w = self.tabla.cellWidget(row, COL_NOTAS)
                if w is not None and w.text() != texto:
                    w.setText(texto)
                break

    # ---------- construcción de la tabla ----------

    def _poblar_tabla(self):
        self.tabla.setRowCount(len(CARRIERS))
        for row, (nombre, url) in enumerate(CARRIERS):

            contenedor = QWidget()
            layout = QHBoxLayout(contenedor)
            layout.setContentsMargins(5, 0, 5, 0)
            layout.addWidget(self.crear_avatar(nombre))
            layout.addWidget(QLabel(nombre))

            alias = [alias for alias,
                portal in PORTAL_ALIASES.items()
                if portal == nombre
                ] 
            if alias:
                aclaracion = QLabel()
                aclaracion.setPixmap(QIcon(str(RESOURCES_DIR / "aclaracion.svg")).pixmap(20, 20))
                
                
                texto_aclaracion = (
                    f"{nombre} son todos aquellos proveedores de red virtuales "
                    f"que reutilizan la misma infraestructura: "
                    + ", ".join(alias)
                )
                aclaracion.setToolTip(texto_aclaracion)
                layout.addWidget(aclaracion)
                layout.addStretch()

            contenedor.setProperty("nombre", nombre)
            contenedor.setProperty("url", url)

            self.tabla.setCellWidget(row, COL_COMPANIA, contenedor)

            combo = QComboBox()
            combo = QComboBox()
            for estado in ESTADOS:
                combo.addItem(self.crear_icono_punto(COLOR_ESTADO[estado]), estado)
            combo.setIconSize(QSize(10, 10))
            estado_actual = self.data["resultados"][nombre]["estado"]
            combo.setCurrentText(estado_actual)
            estado_actual = self.data["resultados"][nombre]["estado"]
            combo.setCurrentText(estado_actual)
            combo.currentTextChanged.connect(lambda texto, n=nombre: self._cambiar_estado(n, texto))
            self.tabla.setCellWidget(row, COL_ESTADO, combo)

            notas = QLineEdit(self.data["resultados"][nombre]["notas"])
            notas.editingFinished.connect(lambda n=nombre, w=notas: self._cambiar_notas(n, w.text()))
            self.tabla.setCellWidget(row, COL_NOTAS, notas)

            boton = QPushButton("Abrir")
            boton.clicked.connect(lambda _, n=nombre, u=url: self._abrir_portal(n, u))
            self.tabla.setCellWidget(row, COL_ABRIR, boton)

    # ---------- acciones ----------
    def crear_icono_punto(self, color: str, size: int = 10) -> QIcon:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, size, size)
        painter.end()
        return QIcon(pixmap)


    def crear_avatar(self,nombre):
        size =20
        label = QLabel()
        label.setFixedSize(size, size)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if nombre == "Redes ALTÁN" or nombre == "Freedompop":
            label.setPixmap(QIcon(str(RESOURCES_DIR / "señal.svg")).pixmap(size, size))
            return label

        # Inicial
        inicial = nombre[0].upper()

        colores = [
        "#E57373",  # rojo
        "#64B5F6",  # azul
        "#81C784",  # verde
        "#FFB74D",  # naranja
        "#BA68C8",  # púrpura
        "#4DB6AC",  # verde azulado (teal)
        "#F06292",  # rosa
        "#9575CD",  # violeta
        "#4FC3F7",  # azul claro
        "#AED581",  # verde lima
        "#FFD54F",  # amarillo
        "#A1887F",  # marrón
        "#90A4AE",  # gris azulado
        "#7986CB",  # índigo
        "#4DD0E1",  # cian
        "#DCE775",  # lima claro
        "#FF8A65",  # naranja profundo
        "#F06060",  # rojo coral
        "#BDBDBD",  # gris
        "#FFF176",  # amarillo claro
    ]

        pixmap = QPixmap(size, size)
        pixmap.fill(colores[zlib.crc32(nombre.encode()) % len(colores)])

        painter = QPainter(pixmap)

        font = QFont()
        font.setBold(True)
        font.setPointSize(size // 2)

        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.white)

        painter.drawText(
            pixmap.rect(),
            Qt.AlignmentFlag.AlignCenter,
            inicial
        )

        painter.end()

        label.setPixmap(pixmap)

        return label


    def _guardar_datos_personales(self):
        self.data["curp"] = self.campo_curp.text().strip().upper()
        guardar(self.data, DEFAULT_PATH)

    def _cambiar_estado(self, nombre, estado):
        registrar_estado(self.data, nombre, estado)
        guardar(self.data, DEFAULT_PATH)
        self._actualizar_resumen()
        if nombre == self._panel_nombre:
            self._refrescar_panel()

    def _cambiar_notas(self, nombre, texto):
        self.data["resultados"][nombre]["notas"] = texto
        guardar(self.data, DEFAULT_PATH)
        self._sincronizar_notas_tabla(nombre, texto)
        if nombre == self._panel_nombre:
            if self.panel_notas.text() != texto:  # la nota se editó desde la tabla
                self.panel_notas.setText(texto)
            self._refrescar_panel()

    def _abrir_portal(self, nombre, url):
        curp = self.campo_curp.text().strip().upper()
        if not curp:
            self.barra_estado.showMessage("No hay una CURP capturada.", 4000)
            return

        QApplication.clipboard().setText(curp)
        self.checker_runner.configurar(
            self.data.get("navegador", NAVEGADORES[0]),
            self.data.get("perfil", ""),
        )
        thread = QThread()
        worker = CheckerWorker(
            self.checker_runner,
            nombre,
            curp,
            [],
        )
        worker.moveToThread(thread)

        thread.started.connect(worker.ejecutar)
        worker.terminado.connect(self.checker_terminado)
        worker.error.connect(self.checker_error)

        worker.terminado.connect(thread.quit)
        worker.error.connect(thread.quit)

        worker.terminado.connect(worker.deleteLater)
        worker.error.connect(worker.deleteLater)

        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._limpiar_thread(nombre))

        self.threads[nombre] = thread
        self.workers[nombre] = worker

        thread.start()

    def _cargar_perfiles(self):
        navegador = self.combo_navegador.currentText()
        guardado = self.data.get("perfil", "")

        self.combo_perfil.blockSignals(True)
        self.combo_perfil.clear()
        self.combo_perfil.addItem("Sin perfil (sesión limpia)", "")
        for nombre, ruta in detectar_perfiles(navegador):
            self.combo_perfil.addItem(nombre, str(ruta))

        idx = self.combo_perfil.findData(guardado)
        if guardado and idx == -1: 
            self.combo_perfil.addItem(Path(guardado).name, guardado)
            idx = self.combo_perfil.count() - 1
        self.combo_perfil.setCurrentIndex(max(idx, 0))
        self.combo_perfil.setToolTip(guardado)
        self.combo_perfil.blockSignals(False)

    def _cambiar_navegador(self, navegador):
        self.data["navegador"] = navegador
        self.data["perfil"] = ""
        self._cargar_perfiles()
        self._aplicar_perfil()

    def _cambiar_perfil(self, _indice):
        self.data["perfil"] = self.combo_perfil.currentData() or ""
        self.combo_perfil.setToolTip(self.data["perfil"])
        self._aplicar_perfil()

    def _buscar_perfil_manual(self):
        carpeta = QFileDialog.getExistingDirectory(
            self, "Elige la carpeta del perfil", str(Path.home())
        )
        if not carpeta:
            return
        self.data["perfil"] = carpeta
        self._cargar_perfiles()
        self._aplicar_perfil()

    def _aplicar_perfil(self):
        guardar(self.data, DEFAULT_PATH)
        self.checker_runner.cerrar()

    def checker_terminado(self, nombre, resultado):
        print(f"[<] Resultado de {nombre}: {resultado}")

        if resultado == "positive":
            estado = ESTADOS[1]  # "Línea encontrada"
        elif resultado == "negative":
            estado = ESTADOS[2]  # "Sin línea"
        else:
            estado = ESTADOS[3]  # "No se pudo revisar"

        self._cambiar_estado(nombre, estado)
        self._actualizar_combo_fila(nombre, estado)
        QTimer.singleShot(2500, self.checker_runner.cerrar)

    def _actualizar_combo_fila(self, nombre, estado):
        for row in range(self.tabla.rowCount()):
            contenedor = self.tabla.cellWidget(row, COL_COMPANIA)
            if contenedor is None:
                continue
            if contenedor.property("nombre") == nombre:
                combo = self.tabla.cellWidget(row, COL_ESTADO)
                combo.blockSignals(True)
                combo.setCurrentText(estado)
                combo.blockSignals(False)
                break

    def _limpiar_thread(self, nombre):
        thread = self.threads.get(nombre)
        if thread is not None:
            thread.wait() 
        self.threads.pop(nombre, None)
        self.workers.pop(nombre, None)
            
    def checker_error(self, nombre, mensaje):
        print(f"[!] Error en {nombre}: {mensaje}")

        estado = ESTADOS[3] 
        self._cambiar_estado(nombre, estado)
        self._actualizar_combo_fila(nombre, estado)

        self.barra_estado.showMessage(f"Error al revisar {nombre}: {mensaje}", 6000)
        

    def _limpiar(self):
        self.campo_curp.setText("")

    def _abrir_siguiente_pendiente(self):
        for nombre, url in CARRIERS:
            if self.data["resultados"][nombre]["estado"] == "Pendiente":
                self._abrir_portal(nombre, url)
                self._seleccionar_fila(nombre)
                return
        QMessageBox.information(self, "Listo", "No quedan compañías pendientes por revisar.")

    def _seleccionar_fila(self, nombre):
        for row in range(self.tabla.rowCount()):
            contenedor = self.tabla.cellWidget(row, COL_COMPANIA)
            if contenedor.property("nombre") == nombre:
                self.tabla.selectRow(row)
                self.tabla.scrollTo(self.tabla.model().index(row, COL_COMPANIA))
                break
    @staticmethod
    def texto_estado_con_punto(estado: str) -> str:
        color = COLOR_ESTADO.get(estado, "#9e9e9e")
        return f'<span style="color:{color};">●</span>&nbsp;{estado}'

    def _filtrar_nombre(self, texto):
        resultados = buscar(texto)
        nombres_encontrados = {
            nombre
            for nombre, url, alias in resultados
        }
        for row in range(self.tabla.rowCount()):

            contenedor = self.tabla.cellWidget(row, COL_COMPANIA)
            nombre = contenedor.property("nombre")

            self.tabla.setRowHidden(
                row,
                nombre not in nombres_encontrados
            )
        

    def _filtrar_estado(self, estado):
        estado = estado.strip().lower()
        for row in range(self.tabla.rowCount()):
            combo = self.tabla.cellWidget(row, COL_ESTADO)
            if combo is None:
                self.tabla.setRowHidden(row, True)
                continue
            estado_fila = combo.currentText().strip().lower()
            self.tabla.setRowHidden(
                row,
                estado != "todos" and estado_fila  != estado
            )
        
    def _exportar(self):
        destino, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar CSV",
            "lineas_curp.csv",
            "CSV (*.csv)")
        if not destino:
            return
        import csv
        with open(destino, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Compañía", "Estado", "Notas"])
            for nombre, _url in CARRIERS:
                r = self.data["resultados"][nombre]
                w.writerow([nombre, r["estado"], r["notas"]])
        self.barra_estado.showMessage(f"Exportado a {destino}", 5000)

    def _actualizar_resumen(self):
        conteo = {e: 0 for e in ESTADOS}
        for r in self.data["resultados"].values():
            conteo[r["estado"]] = conteo.get(r["estado"], 0) + 1
        total = len(self.data["resultados"])
        self.barra_estado.showMessage(
            f"Revisadas: {total - conteo['Pendiente']}/{total}  |  "
            f"Encontradas: {conteo['Línea encontrada']}  |  "
            f"Sin línea: {conteo['Sin línea']}  |  "
            f"Errores: {conteo['No se pudo revisar']}"
        )

    def closeEvent(self, event):
        self.checker_runner.cerrar()
        event.accept()

def main(argv=None):
    app = QApplication(argv or sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
