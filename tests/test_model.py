import tempfile
import unittest
from pathlib import Path

from application.model import AppModel
from storage import STATUS_OPTIONS


class AppModelTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "progress.json"
        self.model = AppModel(self.path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_new_model_contains_all_companies_as_pending(self):
        self.assertGreater(len(self.model.companies), 0)
        self.assertEqual(self.model.summary()[STATUS_OPTIONS[0]], len(self.model.companies))

    def test_status_change_is_persisted(self):
        company = self.model.companies[0].name
        self.model.set_status(company, STATUS_OPTIONS[1])

        reloaded = AppModel(self.path)
        self.assertEqual(reloaded.result(company)["estado"], STATUS_OPTIONS[1])
        self.assertTrue(reloaded.result(company)["fecha"])

    def test_notes_are_persisted(self):
        company = self.model.companies[0].name
        self.model.set_notes(company, "nota de prueba")

        reloaded = AppModel(self.path)
        self.assertEqual(reloaded.result(company)["notas"], "nota de prueba")


if __name__ == "__main__":
    unittest.main()
