import unittest

from pyvalidator.is_isrc import is_isrc
from . import print_test_ok


class TestIsIsrc(unittest.TestCase):

    def test_valid_isrc(self) -> bool:
        self.assertTrue(is_isrc('USAT29900609'))
        self.assertTrue(is_isrc('GBAYE6800011'))
        self.assertTrue(is_isrc('USRC15705223'))
        self.assertTrue(is_isrc('USCA29500702'))
        print_test_ok()

    def test_invalid_isrc(self):
        self.assertFalse(is_isrc('USAT2990060'))
        self.assertFalse(is_isrc('SRC15705223'))
        self.assertFalse(is_isrc('US-CA29500702'))
        self.assertFalse(is_isrc('USARC15705223'))
        print_test_ok()

    def test_fail_isrc(self):
        self.assertRaises(Exception, is_isrc)
        print_test_ok()
