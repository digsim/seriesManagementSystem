from unittest import TestCase
from seriesmgmtsystem.sms.serieManagementSystem import SMS
import os

class TestCalendarEvent(TestCase):

    def test_JSON(self):
        # Like this we can get access to test resources
        cwd = os.path.dirname(os.path.abspath(__file__))
        calendarfile = os.path.join(cwd, 'resources/basic.ics')
        updateBibTex = False
        keepUnzipped = False
        keepTemp = False
        doZip  = False
        sms = SMS(updateBibTex, keepUnzipped, keepTemp, doZip);
        expected="True"
        self.assertEqual("True", expected, 'There are differences')
        
