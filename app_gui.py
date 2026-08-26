# -*- coding: utf-8 -*-
"""Modo gráfico (Qt / PySide6). Muestra el directorio de compañías en una
tabla, deja marcar el estado de cada una a mano después de revisar el
portal oficial (no automatiza CAPTCHAs), y guarda/exporta el progreso."""

import sys, webbrowser
from pathlib import Path  
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QDesktopServices, QAction, QIcon, QPixmap, QPainter, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QHeaderView, QFileDialog, QMessageBox, QStatusBar, QButtonGroup,
)

from carriers import CARRIERS
from storage import ESTADOS, DEFAULT_PATH, cargar, guardar

COL_COMPANIA, COL_ESTADO, COL_NOTAS, COL_ABRIR = range(4)

RESOURCES_DIR = Path(__file__).resolve().parent / "media/svg"

class IconButton(QPushButton):
    def __init__(self, text, icon, icon_position="left", parent=None):
        super().__init__(parent)

        self.setText(text)
        self.setIcon(QIcon(icon))

        if icon_position == "right":
            self.setLayoutDirection(Qt.RightToLeft)

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
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

        telefono_layout = QVBoxLayout()
        telefono_layout.addWidget(QLabel("Teléfono(s)(opcional)"))
        self.campo_telefonos = QLineEdit(", ".join(self.data.get("telefonos", [])))
        self.campo_telefonos.setPlaceholderText("Opcional, separados por coma")
        self.campo_telefonos.editingFinished.connect(self._guardar_datos_personales)
        telefono_layout.addWidget(self.campo_telefonos)
        fila_datos.addLayout(telefono_layout)
        layout.addLayout(fila_datos)


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
        
        #Barra lateral
        
        self.info_compania_qwidget = QWidget()
        self.info_compania_qwidget.setMaximumWidth(0)
        self.info_compania_qwidget.setMinimumWidth(0)
        info_compañia = QVBoxLayout(self.info_compania_qwidget)
                
        info_compañia.setContentsMargins(12, 12, 12, 12)
        info_compañia.setSpacing(8)


        detalle_compañia = QLabel("Detalles:") 
        info_compañia.addWidget(detalle_compañia)

        layout_info_compañia = QHBoxLayout()
        layout_info_compañia.setSpacing(6)

        icono = QLabel("logo")
        nombre_compañia = QLabel("Nombre Compañia")
        sitio_compañia = QPushButton("Abrir")
        layout_info_compañia.addWidget(icono)
        layout_info_compañia.addWidget(nombre_compañia)
        layout_info_compañia.addWidget(sitio_compañia)
        info_compañia.addLayout(layout_info_compañia)

        layout_estado_actual = QHBoxLayout()
        layout_estado_actual.setSpacing(6)

        estado_compañia_acutal = QLabel("Estado Actual")
        estado_compañia = QLabel("Estado")
        layout_estado_actual.addWidget(estado_compañia_acutal)
        layout_estado_actual.addWidget(estado_compañia)
        info_compañia.addLayout(layout_estado_actual)

        layout_fecha_verificacion = QHBoxLayout()
        layout_fecha_verificacion.setSpacing(6)
        
        ultima_verificacion = QLabel("Última verificación")
        fecha_verificacion = QLabel("Fecha")
        layout_fecha_verificacion.addWidget(ultima_verificacion)
        layout_fecha_verificacion.addWidget(fecha_verificacion)
        info_compañia.addLayout(layout_fecha_verificacion)

        layout_notas= QVBoxLayout()
        layout_notas.setSpacing(6)

        notas = QLabel("Notas")
        texto_nota = QLineEdit()
        texto_nota.setPlaceholderText("Añade una nota sobre esta consulta...")
        layout_notas.addWidget(notas)
        layout_notas.addWidget(texto_nota)
        info_compañia.addLayout(layout_notas)

        layout_historial = QVBoxLayout()
        layout_historial.setSpacing(6)

        historial = QLabel("Historial")
        historial_lista  = QLabel("...")
        layout_historial.addWidget(historial)
        layout_historial.addWidget(historial_lista)
        info_compañia.addLayout(layout_historial)
        
        info_compañia.addStretch()


        layout_estado = QHBoxLayout()
        estado_actual = QLabel("Estado actual")
        layout_estado.addWidget(estado_actual)


        layout_tabla_e_info.addWidget(self.info_compania_qwidget)
        self.info_compania_qwidget.setVisible(False)

        #Debe estar oculta para no molestar visualmente, sólo se abre cuando hacen click dos veces

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

    # ---------- construcción de la tabla ----------

    def _poblar_tabla(self):
        self.tabla.setRowCount(len(CARRIERS))
        for row, (nombre, url) in enumerate(CARRIERS):
            item_nombre = QTableWidgetItem(nombre)
            icono_red = QLabel()
            icono_red.setPixmap(QPixmap())
            item_nombre.setData(Qt.ItemDataRole.UserRole, url)
            self.tabla.setItem(row, COL_COMPANIA, icono_red)
            self.tabla.setItem(row, COL_COMPANIA, item_nombre)

            combo = QComboBox()
            combo.addItems(ESTADOS)
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

    def _guardar_datos_personales(self):
        self.data["curp"] = self.campo_curp.text().strip().upper()
        self.data["telefonos"] = [t.strip() for t in self.campo_telefonos.text().split(",") if t.strip()]
        guardar(self.data, DEFAULT_PATH)

    def _cambiar_estado(self, nombre, estado):
        self.data["resultados"][nombre]["estado"] = estado
        guardar(self.data, DEFAULT_PATH)
        self._actualizar_resumen()

    def _cambiar_notas(self, nombre, texto):
        self.data["resultados"][nombre]["notas"] = texto
        guardar(self.data, DEFAULT_PATH)

    def _abrir_portal(self, nombre, url):
        curp = self.campo_curp.text().strip().upper()
        if curp:
            QApplication.clipboard().setText(curp)
            self.barra_estado.showMessage(f"CURP copiada al portapapeles — abriendo {nombre}", 4000)
        else:
            self.barra_estado.showMessage(f"Abriendo {nombre} (no hay CURP capturada)", 4000)
        webbrowser.open(url)

    def _limpiar(self):
        self.campo_curp.setText("")
        self.campo_telefonos.setText("")

    def _abrir_siguiente_pendiente(self):
        for nombre, url in CARRIERS:
            if self.data["resultados"][nombre]["estado"] == "Pendiente":
                self._abrir_portal(nombre, url)
                self._seleccionar_fila(nombre)
                return
        QMessageBox.information(self, "Listo", "No quedan compañías pendientes por revisar.")

    def _seleccionar_fila(self, nombre):
        for row in range(self.tabla.rowCount()):
            if self.tabla.item(row, COL_COMPANIA).text() == nombre:
                self.tabla.selectRow(row)
                self.tabla.scrollToItem(self.tabla.item(row, COL_COMPANIA))
                break

    def _filtrar_nombre(self, texto):
        texto = texto.strip().lower()
        for row in range(self.tabla.rowCount()):
            nombre = self.tabla.item(row, COL_COMPANIA).text().lower()
            self.tabla.setRowHidden(row, texto not in nombre)

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


def main(argv=None):
    app = QApplication(argv or sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
