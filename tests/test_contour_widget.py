from unittest import TestCase

import src.widgets.contour_widget as contour_widget


class ValidateTest(TestCase):
    def test_validate_valid_cases(self):
        cases = ["1", "23.4", "1,23.4", "12,3,4", "-5", "-5,-10"]
        for case in cases:
            self.assertTrue(
                contour_widget.validate_list_entry(case),
                f"Expected {case} to pass validation",
            )

    def test_validate_invalid_cases(self):
        cases = ["", "234,", "a", "1a2", "5-1"]
        for case in cases:
            self.assertFalse(
                contour_widget.validate_list_entry(case),
                f"Expected {case} to fail validation",
            )
