# test_file_utils.py

import unittest
import os
import sys
sys.path.append(os.pardir)
from no_utils import FileUtils

class TestFileUtils(unittest.TestCase):
    def setUp(self):
        self.file_utils = FileUtils()
        self.test_dir = 'test_dir'
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, 'test_file.txt')
        self.test_file2 = os.path.join(self.test_dir, 'test_file2.txt')
        self.output_file = os.path.join(self.test_dir, 'output_file.txt')

    def tearDown(self):
        for file in [self.test_file, self.test_file2, self.output_file]:
            if os.path.exists(file):
                os.remove(file)
        os.rmdir(self.test_dir)

    def test_replace(self):
        with open(self.test_file, 'w') as f:
            f.write('Hello World')
        self.file_utils.replace(self.test_file, 'World', 'Universe')
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), 'Hello Universe')

    def test_clear(self):
        with open(self.test_file, 'w') as f:
            f.write('Hello World')
        self.file_utils.clear(self.test_file)
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), '')

    def test_append(self):
        with open(self.test_file, 'w') as f:
            f.write('Hello')
        self.file_utils.append(self.test_file, ' World')
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), 'Hello World')

    def test_content_exists(self):
        with open(self.test_file, 'w') as f:
            f.write('Hello World')
        self.assertTrue(self.file_utils.content_exists(self.test_file, 'World'))
        self.assertFalse(self.file_utils.content_exists(self.test_file, 'Universe'))

    def test_get_lines_with_content(self):
        with open(self.test_file, 'w') as f:
            f.write('Hello World\nHello Universe\nHello Python')
        lines = self.file_utils.get_lines_with_content(self.test_file, 'Hello')
        self.assertEqual(lines, ['Hello World\n', 'Hello Universe\n', 'Hello Python'])

    def test_get_lines_without_content(self):
        with open(self.test_file, 'w') as f:
            f.write('Hello World\nHello Universe\nHello Python')
        lines = self.file_utils.get_lines_without_content(self.test_file, 'Universe')
        self.assertEqual(lines, ['Hello World\n', 'Hello Python'])

    def test_remove_empty_lines(self):
        with open(self.test_file, 'w') as f:
            f.write('Hello World\n\nHello Universe\n\n')
        self.file_utils.remove_empty_lines(self.test_file)
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), 'Hello World\nHello Universe\n')

    def test_remove_last_empty_line(self):
        with open(self.test_file, 'w') as f:
            f.write('Hello World\nHello Universe\n\n')
        self.file_utils.remove_last_empty_line(self.test_file)
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), 'Hello World\nHello Universe\n')

    def test_merge_files(self):
        with open(self.test_file, 'w') as f:
            f.write('Hello World\n')
        with open(self.test_file2, 'w') as f:
            f.write('Hello Universe\n')
        self.file_utils.merge_files([self.test_file, self.test_file2], self.output_file)
        with open(self.output_file, 'r') as f:
            self.assertEqual(f.read(), 'Hello World\nHello Universe\n')

if __name__ == '__main__':
    unittest.main()