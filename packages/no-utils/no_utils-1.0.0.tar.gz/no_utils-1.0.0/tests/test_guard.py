# test_guard.py

import unittest
import sys
import os
sys.path.append(os.pardir)
from no_utils import Guard

class TestGuard(unittest.TestCase):
    def setUp(self):
        self.guard = Guard()

    def test_against_none(self):
        with self.assertRaises(ValueError):
            self.guard.against_none(None, throw_exception=True, force_exit=False)
        
        with self.assertRaises(SystemExit):
            self.guard.against_none(None, throw_exception=False, force_exit=True)

    def test_against_empty(self):
        with self.assertRaises(ValueError):
            self.guard.against_empty([], throw_exception=True, force_exit=False)
        
        with self.assertRaises(SystemExit):
            self.guard.against_empty([], throw_exception=False, force_exit=True)

    def test_against_empty_str(self):
        with self.assertRaises(ValueError):
            self.guard.against_empty_str("", throw_exception=True, force_exit=False)
        
        with self.assertRaises(SystemExit):
            self.guard.against_empty_str("", throw_exception=False, force_exit=True)

if __name__ == '__main__':
    unittest.main()