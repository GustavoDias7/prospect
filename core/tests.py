from django.test import TestCase
from prospect.utils import has_string_in_list

# Create your tests here.

class TestHasStringInList(TestCase):

    def test_single_string_match(self):
        string = "hello"
        string_list = ["Hello world", "Goodbye"]
        result = has_string_in_list(string, string_list)
        self.assertTrue(result)

    def test_list_of_strings_match(self):
        string = ["hello", "world"]
        string_list = ["Hello there", "Goodbye"]
        result = has_string_in_list(string, string_list)
        self.assertTrue(result)

    def test_case_sensitive_true(self):
        string = "hello"
        string_list = ["Hello world", "Goodbye"]
        result = has_string_in_list(string, string_list, case_sensitive=True)
        self.assertFalse(result)

    def test_case_sensitive_false(self):
        string = "hello"
        string_list = ["Hello world", "Goodbye"]
        result = has_string_in_list(string, string_list, case_sensitive=False)
        self.assertTrue(result)

    def test_multiple_strings_in_list(self):
        string = ["hello", "goodbye"]
        string_list = ["Hello there", "Goodbye"]
        result = has_string_in_list(string, string_list)
        self.assertTrue(result)

    def test_no_match(self):
        string = "hello"
        string_list = ["Goodbye", "See you later"]
        result = has_string_in_list(string, string_list)
        self.assertFalse(result)

    def test_empty_string_list(self):
        string = "hello"
        string_list = []
        result = has_string_in_list(string, string_list)
        self.assertFalse(result)

    def test_accents_replacement(self):
        string = "café"
        string_list = ["Cafe", "Goodbye"]
        result = has_string_in_list(string, string_list)
        self.assertTrue(result)

    def test_case_and_accents(self):
        string = "café"
        string_list = ["Café", "Goodbye"]
        result = has_string_in_list(string, string_list, case_sensitive=False)
        self.assertTrue(result)

    def test_multiple_strings_and_case(self):
        string = ["hello", "Goodbye"]
        string_list = ["HELLO world", "Goodbye"]
        result = has_string_in_list(string, string_list, case_sensitive=True)
        self.assertTrue(result)
