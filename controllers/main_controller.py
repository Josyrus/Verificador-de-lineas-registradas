from __future__ import annotations

import webbrowser
from pathlib import Path

from PySide6.QtCore import QObject, QThread, QTimer
from PySide6.QtWidgets import QApplication

from application.model import AppModel
from application.services import BatchController, CheckerService
from carriers import PORTAL_ALIASES
from checker.runner import CONFIGS
from checker.worker import CheckerWorker
from clipboard import copy_to_clipboard
from storage import STATUS_OPTIONS


class MainController(QObject):

    def __init__(self, model: AppModel, view) -> None:
        super().__init__(view)
        self.model = model
        self.view = view
        self.checker = CheckerService()
        self.batch = BatchController()
        self.threads: dict[str, QThread] = {}
        self.workers: dict[str, CheckerWorker] = {}
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.checker.close)
        self._connect_view()
        self._load_profiles()

    def _connect_view(self) -> None:
        self.view.curp_changed.connect(self._save_curp)
        self.view.browser_changed.connect(self._change_browser)
        self.view.profile_changed.connect(self._change_profile)
        self.view.manual_profile_requested.connect(self._choose_profile)
        self.view.clear_requested.connect(self._clear_curp)
        self.view.open_company_requested.connect(self.open_company)
        self.view.batch_requested.connect(self.handle_batch)
        self.view.status_changed.connect(self.change_status)
        self.view.notes_changed.connect(self.change_notes)
        self.view.name_filter_changed.connect(self.filter_by_name)
        self.view.status_filter_changed.connect(self.view.apply_status_filter)
        self.view.export_requested.connect(self.export_csv)

    def _save_curp(self, value: str) -> None:
        self.model.curp = value

    def _change_browser(self, browser: str) -> None:
        self.model.browser = browser
        self._load_profiles()
        self.checker.close()

    def _change_profile(self, profile: str) -> None:
        self.model.profile = profile
        self.checker.close()

    def _choose_profile(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        path = QFileDialog.getExistingDirectory(self.view, "Elige la carpeta del perfil", str(Path.home()))
        if not path:
            return
        self.model.profile = path
        self._load_profiles()
        self.checker.close()

    def _load_profiles(self) -> None:
        profiles = self.checker.profiles(self.model.browser)
        self.view.load_profiles(profiles, self.model.profile)

    def _clear_curp(self) -> None:
        self.view.curp_input.clear()
        self.model.curp = ""

    def _validate_curp(self) -> str | None:
        curp = self.model.curp.strip().upper()
        if not curp:
            self.view.set_status_message("No hay una CURP capturada.", 4000)
            return None
        return curp

    def change_status(self, name: str, status: str) -> None:
        self.model.set_status(name, status)
        self.view.data = self.model.data
        self.view.update_row_status(name, status)
        self.view.update_summary(self.model.summary())

    def change_notes(self, name: str, notes: str) -> None:
        self.model.set_notes(name, notes)
        self.view.data = self.model.data
        self.view.update_row_notes(name, notes)

    def open_company(self, name: str) -> None:
        curp = self._validate_curp()
        if curp is None:
            return
        if self.threads:
            self.view.set_status_message("Ya hay una revisión automatizada en curso.", 4000)
            return

        company = self.model.company(name)
        QApplication.clipboard().setText(curp)
        copy_to_clipboard(curp)

        if name not in CONFIGS:
            webbrowser.open(company.url)
            self.view.set_status_message(
                f"{name}: sin automatización. CURP copiada; revisa el portal y marca el estado a mano.",
                6000,
            )
            return

        self.checker.configure(self.model.browser, self.model.profile)
        thread = QThread(self)
        worker = CheckerWorker(self.checker.runner, name, curp, [])
        worker.moveToThread(thread)

        thread.started.connect(worker.execute)
        worker.finished.connect(self._check_finished)
        worker.error.connect(self._check_error)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.error.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda n=name, t=thread: self._cleanup_thread(n, t))

        self.threads[name] = thread
        self.workers[name] = worker
        self.close_timer.stop()
        thread.start()

    def _check_finished(self, name: str, result: str) -> None:
        status = self._status_from_result(result)
        self.change_status(name, status)
        self.close_timer.start(2500)
        self._advance_batch(name)

    def _check_error(self, name: str, message: str) -> None:
        self.change_status(name, STATUS_OPTIONS[3])
        self.view.set_status_message(f"Error al revisar {name}: {message}", 6000)
        self._advance_batch(name)

    def _cleanup_thread(self, name: str, thread: QThread) -> None:
        current = self.threads.get(name)
        if current is not thread:
            return
        self.threads.pop(name, None)
        self.workers.pop(name, None)
        self._advance_batch(name)

    @staticmethod
    def _status_from_result(result: str) -> str:
        return {
            "positive": STATUS_OPTIONS[1],
            "negative": STATUS_OPTIONS[2],
        }.get(result, STATUS_OPTIONS[3])

    def handle_batch(self, mode: str) -> None:
        if self.batch.active:
            self.batch.stop()
            self.view.set_batch_active(False)
            self.view.set_status_message("Lote detenido.", 5000)
            return

        if mode == "all":
            automated = [name for name in CONFIGS if self.model.result(name)["estado"] == STATUS_OPTIONS[0]]
            automated = [company.name for company in self.model.companies if company.name in automated]
            if not automated:
                self.view.show_message("Sin configuraciones", "No hay compañías pendientes con automatización.")
                return
            self.batch.start(automated)
            self.view.set_batch_active(True)
            self._process_next_batch()
            return

        pending = self.model.pending()
        if not pending:
            self.view.show_message("Listo", "No quedan compañías pendientes por revisar.")
            return
        self.view.select_company(pending[0].name)
        self.open_company(pending[0].name)

    def _process_next_batch(self) -> None:
        name = self.batch.current()
        if name is None:
            self.view.set_batch_active(False)
            self.view.set_status_message("Lote de revisión automática terminado.", 5000)
            return
        self.view.select_company(name)
        self.view.set_status_message(f"Lote: revisando {name} ({self.batch.remaining} restantes)")
        self.open_company(name)

    def _advance_batch(self, name: str) -> None:
        if not self.batch.active:
            return
        self.batch.complete(name)
        QTimer.singleShot(400, self._process_next_batch)

    def filter_by_name(self, text: str) -> None:
        self.view.apply_name_filter(self.model.search(text))

    def export_csv(self) -> None:
        destination = self.view.ask_export_path()
        if not destination:
            return
        self.model.export_csv(Path(destination))
        self.view.set_status_message(f"Exportado a {destination}", 5000)

    def close(self) -> None:
        self.batch.stop()
        self.checker.close()
