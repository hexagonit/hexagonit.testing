from hexagonit.testing.date import static_date
from hexagonit.testing.date import static_datetime
import datetime
import unittest2 as unittest


class StaticDatetimeTest(unittest.TestCase):

    def setUp(self):
        self.orig_date = datetime.date
        self.orig_datetime = datetime.datetime

    def tearDown(self):
        datetime.date = self.orig_date
        datetime.datetime = self.orig_datetime

    def test_static_date(self):
        datetime.date = static_date(datetime.date(2007, 5, 29))
        self.assertEquals('2007-05-29', datetime.date.today().isoformat())

    def test_static_date__invalid_input(self):
        self.assertRaises(TypeError, lambda: static_date('2008-08-08'))

    def test_static_datetime(self):
        datetime.datetime = static_datetime(datetime.datetime(2007, 5, 29, 12, 32, 43))
        self.assertEquals('2007-05-29T12:32:43', datetime.datetime.now().isoformat())

    def test_static_datetime__invalid_input(self):
        self.assertRaises(TypeError, lambda: static_datetime('2008-08-08'))
