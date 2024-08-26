import unittest

from pyvalidator.is_json import is_json
from . import print_test_ok


class TestIsJson(unittest.TestCase):

    def test_valid_json(self):
        self.assertTrue(is_json('{ "key": "value" }'))
        self.assertTrue(is_json('{}'))
        print_test_ok()

    def test_invalid_json(self):
        self.assertFalse(is_json('{ key: "value" }'))
        self.assertFalse(is_json('{ \'key\': \'value\' }'))
        self.assertFalse(is_json('null'))
        self.assertFalse(is_json('1234'))
        self.assertFalse(is_json('11.1'))
        self.assertFalse(is_json('nope'))
        self.assertFalse(is_json('None'))
        self.assertFalse(is_json('false'))
        self.assertFalse(is_json('true'))
        print_test_ok()

    def test_valid_json_allow_primitives(self):
        self.assertTrue(is_json('{ "key": "value" }', { "allow_primitives": True }))
        self.assertTrue(is_json('{}', { "allow_primitives": True }))
        self.assertTrue(is_json('false', { "allow_primitives": True }))
        self.assertTrue(is_json('true', { "allow_primitives": True }))
        print_test_ok()

    def test_invalid_json_allow_primitives(self):
        self.assertFalse(is_json('{ key: "value" }', { "allow_primitives": True }))
        self.assertFalse(is_json('{ \'key\': \'value\' }', { "allow_primitives": True }))
        self.assertFalse(is_json('{ "key": value }', { "allow_primitives": True }))
        self.assertFalse(is_json('1234', { "allow_primitives": True }))
        self.assertFalse(is_json('nope', { "allow_primitives": True }))
        self.assertFalse(is_json('None', { "allow_primitives": True }))
        print_test_ok()
