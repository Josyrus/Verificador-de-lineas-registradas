from PySide6.QtCore import QObject, Signal, Slot

class CheckerWorker(QObject):
    terminado = Signal(str,str)
    error = Signal(str,str)

    def __init__(self,runner, nombre, curp, telefonos):
        super().__init__()
        self.runner = runner
        self.nombre = nombre
        self.curp = curp
        self.telefonos = telefonos 
        
        
    @Slot()
    def ejecutar(self):
        try:
            resultado = self.runner.ejecutar(
                self.nombre,
                self.curp,
                self.telefonos
            )

            print(f"[DEBUG Worker] {resultado}")

            self.terminado.emit(self.nombre, resultado)
        except Exception as e:
            self.error.emit(self.nombre, str(e))
        