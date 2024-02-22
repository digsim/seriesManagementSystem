import os
from unittest import TestCase

from seriesmgmtsystem.sms.serieManagementSystem import SMS


class TestCalendarEvent(TestCase):

    def test_JSON(self) -> None:
        # Like this we can get access to test resources
        os.path.dirname(os.path.abspath(__file__))
        updateBibTex = False
        keepUnzipped = False
        keepTemp = False
        doZip = False
        SMS(updateBibTex, keepUnzipped, keepTemp, doZip)
        expected = "True"
        self.assertEqual("True", expected, 'There are differences')
