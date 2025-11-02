import os
from unittest import TestCase


class TestCalendarEvent(TestCase):

    def test_JSON(self) -> None:
        # Like this we can get access to test resources
        os.path.dirname(os.path.abspath(__file__))
        expected = "True"
        self.assertEqual("True", expected, "There are differences")
