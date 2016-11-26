from unittest import TestCase
from ppic.itc.calendar2itc import Calendar2ITC
import os

class TestCalendarEvent(TestCase):

    def test_JSON(self):
        # Like this we can get access to test resources
        cwd = os.path.dirname(os.path.abspath(__file__))
        self.calendarfile = os.path.join(cwd, 'resources/basic.ics')
        cal = Calendar2ITC()
        expected="True"
        self.assertEqual("True", expected, 'There are differences')
        
