from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from carriers import CARRIERS, search_carriers
from storage import DEFAULT_PATH, STATUS_OPTIONS, load_progress, save_progress, record_status


@dataclass(frozen=True)
class Company:
    name: str
    url: str


class AppModel:

    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        self.path = Path(path)
        self.companies = tuple(Company(name, url) for name, url in CARRIERS)
        self._companies_by_name = {company.name: company for company in self.companies}
        self.data = load_progress(self.path)

    @property
    def curp(self) -> str:
        return self.data.get("curp", "")

    @curp.setter
    def curp(self, value: str) -> None:
        self.data["curp"] = value.strip().upper()
        self.save()

    @property
    def browser(self) -> str:
        return self.data.get("navegador", "Firefox")

    @browser.setter
    def browser(self, value: str) -> None:
        self.data["navegador"] = value
        self.data["perfil"] = ""
        self.save()

    @property
    def profile(self) -> str:
        return self.data.get("perfil", "")

    @profile.setter
    def profile(self, value: str) -> None:
        self.data["perfil"] = value
        self.save()

    def save(self) -> None:
        save_progress(self.data, self.path)

    def company(self, name: str) -> Company:
        return self._companies_by_name[name]

    def result(self, name: str) -> dict:
        return self.data["resultados"][name]

    def set_status(self, name: str, status: str) -> None:
        if status not in STATUS_OPTIONS:
            raise ValueError(f"Estado no válido: {status}")
        record_status(self.data, name, status)
        self.save()

    def set_notes(self, name: str, notes: str) -> None:
        self.result(name)["notas"] = notes
        self.save()

    def summary(self) -> Counter:
        return Counter(result["estado"] for result in self.data["resultados"].values())

    def pending(self, automated_only: bool = False, automated_names: Iterable[str] = ()) -> list[Company]:
        automated = set(automated_names)
        return [
            company
            for company in self.companies
            if self.result(company.name)["estado"] == STATUS_OPTIONS[0]
            and (not automated_only or company.name in automated)
        ]

    def search(self, text: str) -> set[str]:
        return {name for name, _url, _alias in search_carriers(text)}

    def export_csv(self, destination: Path) -> None:
        with Path(destination).open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Compañía", "Estado", "Notas"])
            for company in self.companies:
                result = self.result(company.name)
                writer.writerow([company.name, result["estado"], result["notas"]])
