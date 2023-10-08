from unittest import TestCase

from src.widgets.contour_widget import validate_list_entry


class ValidateTest(TestCase):
    def test_validate_valid_cases(self):
        cases = ["1", "23.4", "1,23.4", "12,3,4", "-5", "-5,-10"]
        for case in cases:
            self.assertTrue(
                validate_list_entry(case), f"Expected {case} to pass validation"
            )

    def test_validate_invalid_cases(self):
        cases = ["", "234,", "a", "1a2", "5-1"]
        for case in cases:
            self.assertFalse(
                validate_list_entry(case), f"Expected {case} to fail validation"
            )
