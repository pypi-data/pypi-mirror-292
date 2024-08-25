import unittest

from hs3.diff import make_patch, get, remove_substrings

class TestHS3Diff(unittest.TestCase):

    def test_simple_diff(self):
        src = {"key1": "value1", "key2": "value2"}
        dst = {"key1": "value1", "key2": "value3"}
        expected_patch = [{'op': 'replace', 'path': ['key2'], 'orig': 'value2', 'new': 'value3'}]
        self.assertEqual(make_patch(src, dst, ignore=[], precision=6), expected_patch)

    def test_add_key(self):
        src = {"key1": "value1"}
        dst = {"key1": "value1", "key2": "value2"}
        expected_patch = [{'op': 'add', 'path': ['key2'], 'value': 'value2'}]
        self.assertEqual(make_patch(src, dst, ignore=[], precision=6), expected_patch)

    def test_remove_key(self):
        src = {"key1": "value1", "key2": "value2"}
        dst = {"key1": "value1"}
        expected_patch = [{'op': 'remove', 'path': ['key2'], 'value': 'value2'}]
        self.assertEqual(make_patch(src, dst, ignore=[], precision=6), expected_patch)

    def test_diff_with_lists(self):
        src = {"list_key": [1, 2, 3]}
        dst = {"list_key": [1, 2, 4]}
        expected_patch = [{'op': 'replace', 'path': ['list_key', '2'], 'orig': 3, 'new': 4}]
        self.assertEqual(make_patch(src, dst, ignore=[], precision=6), expected_patch)

    def test_float_diff_with_precision(self):
        src = {"key": 1.000001}
        dst = {"key": 1.000002}
        
        # Set precision to 6 to detect differences at the sixth decimal place
        expected_patch = [{'op': 'replace', 'path': ['key'], 'orig': 1.000001, 'new': 1.000002}]
        self.assertEqual(make_patch(src, dst, ignore=[], precision=6), expected_patch)
        
        # Optionally, you can also test with precision 5 to ensure no difference is detected:
        expected_patch = []
        self.assertEqual(make_patch(src, dst, ignore=[], precision=5), expected_patch)

    def test_ignore_key(self):
        src = {"key1": "value1", "key2": "value2"}
        dst = {"key1": "value1", "key2": "value3"}
        # If we ignore 'key2', no patch should be created
        expected_patch = []
        self.assertEqual(make_patch(src, dst, ignore=['key2'], precision=6), expected_patch)
        
    def test_get_function(self):
        js = {"key1": {"key2": {"key3": "value"}}}
        path = ["key1", "key2", "key3"]
        self.assertEqual(get(js, path), "value")

    def test_remove_substrings(self):
        s = "hello world"
        substrings = ["world"]
        self.assertEqual(remove_substrings(s, substrings), "hello ")

if __name__ == '__main__':
    unittest.main()
