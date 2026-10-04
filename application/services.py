from __future__ import annotations

from checker.profiles import detect_profiles
from checker.runner import CheckerRunner


class CheckerService:

    def __init__(self) -> None:
        self.runner = CheckerRunner()

    def configure(self, browser: str, profile: str) -> None:
        self.runner.configure(browser, profile)

    def run(self, company_name: str, curp: str):
        return self.runner.execute(company_name, curp)

    def close(self) -> None:
        self.runner.close()

    @staticmethod
    def profiles(browser: str):
        return detect_profiles(browser)


class BatchController:

    def __init__(self) -> None:
        self._queue: list[str] = []
        self.active = False

    def start(self, names: list[str]) -> None:
        self._queue = list(names)
        self.active = bool(self._queue)

    def stop(self) -> None:
        self._queue.clear()
        self.active = False

    def current(self) -> str | None:
        return self._queue[0] if self._queue else None

    def complete(self, name: str) -> None:
        if self._queue and self._queue[0] == name:
            self._queue.pop(0)
        if not self._queue:
            self.active = False

    @property
    def remaining(self) -> int:
        return len(self._queue)
