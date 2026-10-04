from PySide6.QtCore import QObject, Signal, Slot


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
