import unittest
from wikisearch.utils import safe_filename

class TestSafeFilename(unittest.TestCase):
    def test_normal_filename(self):
        result = safe_filename('hello world')
        self.assertEqual(result, 'hello world')

    def test_replaces_invalid_characters(self):
        result = safe_filename('hello<world>:test')
        self.assertEqual(result, 'hello_world__test')

    def test_removes_leading_and_trailing_spaces(self):
        result = safe_filename('  hello world  ')
        self.assertEqual(result, 'hello world')

    def test_removes_leading_and_trailing_periods(self):
        result = safe_filename('...hello world...')
        self.assertEqual(result, 'hello world')

    def test_empty_string_returns_output(self):
        result = safe_filename('')
        self.assertEqual(result, 'output')

    def test_only_spaces_and_periods_returns_output(self):
        result = safe_filename('   ...   ')
        self.assertEqual(result, 'output')

    def test_multiple_invalid_characters(self):
        result = safe_filename('a/b\\c:d*e?f"g<h>i|j')
        self.assertEqual(result, 'a_b_c_d_e_f_g_h_i_j')

if __name__ == '__main__':
    unittest.main()