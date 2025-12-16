from django.test import TestCase
from .forms import AddRecordForm


class AddRecordFormValidatorTests(TestCase):
    def test_title_min_length_error(self):
        form = AddRecordForm({
            "title": "abcd",
            "quantity": 10,
            "event_date": "2025-12-13",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_title_accepts_general_text(self):
        form = AddRecordForm({
            "title": "Test-123 Русский",
            "quantity": 10,
            "event_date": "2025-12-13",
        })
        self.assertTrue(form.is_valid())

    def test_title_rejects_only_spaces(self):
        form = AddRecordForm({
            "title": "    ",
            "quantity": 10,
            "event_date": "2025-12-13",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_title_rejects_bad_symbols(self):
        form = AddRecordForm({
            "title": "Bad@Title!",
            "quantity": 10,
            "event_date": "2025-12-13",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
