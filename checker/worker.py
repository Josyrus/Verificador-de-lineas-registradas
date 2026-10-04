from PySide6.QtCore import QObject, Signal, Slot

<<<<<<< HEAD
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
        
=======

class CheckerWorker(QObject):
    finished = Signal(str, str)
    error = Signal(str, str)

    def __init__(self, runner, company_name: str, curp: str, phones: list[str]):
        super().__init__()
        self.runner = runner
        self.company_name = company_name
        self.curp = curp
        self.phones = phones

    @Slot()
    def execute(self) -> None:
        try:
            result = self.runner.execute(self.company_name, self.curp, self.phones)
            self.finished.emit(self.company_name, result)
        except Exception as exc:
            self.error.emit(self.company_name, str(exc))
>>>>>>> 4197789 (Reestructuración del proyecto a un MVC funcional)
