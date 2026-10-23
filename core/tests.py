from django.test import TestCase
from prospect.utils import has_substrings_in_strings, parse_phone
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import requests
from prospect.utils import get_dimentions, text_to_image, get_phones, get_emails, is_landline, is_mobile
# Create your tests here.

class TestHasStringInList(TestCase):

    def test_single_string_match(self):
        substring = "hello"
        strings = ["Hello world", "Goodbye"]
        result = has_substrings_in_strings(substring, strings)
        self.assertTrue(result)

    def test_list_of_strings_match(self):
        substring = ["hello", "world"]
        strings = ["Hello there", "Goodbye"]
        result = has_substrings_in_strings(substring, strings)
        self.assertTrue(result)

    def test_case_sensitive_true(self):
        substring = "hello"
        strings = ["Hello world", "Goodbye"]
        result = has_substrings_in_strings(substring, strings, case_sensitive=True)
        self.assertFalse(result)

    def test_case_sensitive_false(self):
        substring = "hello"
        strings = ["Hello world", "Goodbye"]
        result = has_substrings_in_strings(substring, strings, case_sensitive=False)
        self.assertTrue(result)

    def test_multiple_strings_in_list(self):
        substrings = ["hello", "goodbye"]
        strings = ["Hello there", "Goodbye"]
        result = has_substrings_in_strings(substrings, strings)
        self.assertTrue(result)

    def test_no_match(self):
        substring = "hello"
        strings = ["Goodbye", "See you later"]
        result = has_substrings_in_strings(substring, strings)
        self.assertFalse(result)

    def test_empty_strings(self):
        substring = "hello"
        strings = []
        result = has_substrings_in_strings(substring, strings)
        self.assertFalse(result)

    def test_accents_replacement(self):
        substring = "café"
        strings = ["Cafe", "Goodbye"]
        result = has_substrings_in_strings(substring, strings)
        self.assertTrue(result)

    def test_case_and_accents(self):
        substring = "café"
        strings = ["Café", "Goodbye"]
        result = has_substrings_in_strings(substring, strings, case_sensitive=False)
        self.assertTrue(result)

    def test_multiple_strings_and_case(self):
        substrings = ["hello", "Goodbye"]
        strings = ["HELLO world", "Goodbye"]
        result = has_substrings_in_strings(substrings, strings, case_sensitive=True)
        self.assertTrue(result)

    def test123(self):
        substrings = ["contabilidade", "contador", "contabi"]
        string = "linacontabilidade@gmail.com"
        result = has_substrings_in_strings(substrings, string)
        self.assertTrue(result)


class TestPILTextWrap(TestCase):

    def test_text_wrap(self):
        phrase = "Lorem ipsum dolor sit amet consectetur adipisicing elit. Voluptatibus, atque praesentium eius, animi, distinctio officia iure doloribus incidunt recusandae ad modi unde rem optio aliquam inventore. Vero placeat unde repellat!"
        req = requests.get("https://github.com/googlefonts/roboto-2/raw/refs/heads/main/src/hinted/Roboto-Regular.ttf")
        width, height = get_dimentions("9:16", 1080, int)
        img_background = Image.new("RGBA", (width, height), "#ffffff") #3:4 
        draw_background = ImageDraw.Draw(img_background)
        main_font = ImageFont.truetype(BytesIO(req.content), size=48)
        main_text_width = 800
        main_text = text_to_image(
            draw=draw_background, 
            text=phrase,
            width=main_text_width,
            fill=f"#222", 
            font=main_font, 
            align="left",
            # outline=is_preview
        )
        main_text.show()
        print(main_text.size)
        img_background.paste(main_text, (0, 0))
        self.assertTrue(main_text.size[0] <= main_text_width)


class PhoneParserTest(TestCase):

    def test_valid_mobile_with_ddd(self):
        phone_number = "21987654321"
        result = parse_phone(phone_number)
        print("before:", phone_number)
        print("after:", result)
        self.assertEqual(result, {
            "country_code": "55",
            "ddd": "21",
            "number": "987654321"
        })

    def test_valid_mobile_without_ddd(self):
        phone_number = "987654321"
        result = parse_phone(phone_number)
        print("before:", phone_number)
        print("after:", result)
        self.assertEqual(result, {
            "country_code": "55",
            "ddd": "",
            "number": "987654321"
        })

    def test_with_symbols(self):
        phone_number = "(21) 98765-4321"
        result = parse_phone(phone_number)
        print("before:", phone_number)
        print("after:", result)

        self.assertEqual(result["ddd"], "21")
        self.assertEqual(result["number"], "987654321")

    def test_invalid_short_number(self):
        phone_number = "123"
        result = parse_phone(phone_number)
        print("before:", phone_number)
        print("after:", result)

        self.assertIsNone(result)

    def test_with_country_code(self):
        phone_number = "+55 21 98765-4321"
        result = parse_phone(phone_number)
        print("before:", phone_number)
        print("after:", result)

        self.assertEqual(result["ddd"], "21")


class GetContactsTest(TestCase):
    def test_get_all_phone_numbers(self):
        phone_numbers = """
            (21) 98765-4321
            (11) 91234-5678
            (31) 99876-1234
            (41) 97654-3210
            (51) 93456-7890

            (21) 3456-7890
            (11) 2345-6789
            (31) 4567-8901
            (41) 5678-9012
            (51) 6789-0123

            21 98765-4321
            11 91234-5678
            31 99876-1234
            41 97654-3210

            21 3456-7890
            11 2345-6789
            31 4567-8901
            41 5678-9012

            21987654321
            11912345678
            31998761234
            41976543210

            2134567890
            1123456789
            3145678901
            4156789012

            98765-4321
            91234-5678
            99876-1234

            3456-7890
            2345-6789
            4567-8901

            98765.4321
            91234.5678
            3456.7890

            (21)98765-4321
            (11)91234.5678
            (31)3456-7890
            (41)5678.9012

            21-98765-4321
            11-91234-5678
            31-3456-7890
            41-5678-9012

            21.98765.4321
            11.91234.5678
            31.3456.7890
            41.5678.9012
        """
        result = get_phones(phone_numbers)
        for index, phone_number in enumerate(result):
            print(index, phone_number)
        self.assertEqual(True, True)

        
    def test_get_similar_landline_mobile(self):
        phone_numbers = """
            +55 (21) 98765-4321
            (21) 98765-4321
            (21) 8765-4321
        """
        result = get_phones(phone_numbers)
        for index, phone_number in enumerate(result):
            print(index, phone_number)
        self.assertEqual(result, ["21987654321", "2187654321"])

    def test_get_emails(self):
        text = """
            Contact us at test@example.com
            Another email: user123@test.co.uk
            Duplicate: test@example.com
            Invalid: test@com, @example.com, user@.com
            Mixed: NAME@DOMAIN.COM
            mailto:contact@test.com.br
        """

        result = get_emails(text)

        expected = [
            "test@example.com",
            "user123@test.co.uk",
            "NAME@DOMAIN.COM",
            "contact@test.com.br"
        ]

        self.assertEqual(result, expected)

class ValidPhoneNumbersTest(TestCase):
    def test_is_valid_landline(self):
        valid_landlines = [
            "23456789",      # 8 digits
            "34567890",
            "45678901",

            "1123456789",    # DDD + 8
            "2134567890",
            "3145678901",

            "551123456789",  # 55 + DDD + 8
            "552134567890",
            "553145678901",
            "554156789012",
        ]

        for landline in valid_landlines:
            result = is_landline(landline)
            self.assertEqual(result, True)

    def test_is_invalid_landline(self):
        invalid_landlines = [
            "1234567",        # too short
            "123456789",      # 9 digits (invalid)
            "12345678901",    # 11 digits (mobile length)

            "11912345678",    # mobile (DDD + 9 digits)
            "5511912345678",  # mobile with country code

            "0123456789",     # starts with 0 (invalid pattern)
            "001123456789",   # wrong country code format

            "abcdefgh",       # not digits
            "1234abcd",       # mixed invalid

            "9999999999999",  # too long
        ]

        for landline in invalid_landlines:
            result = is_landline(landline)
            self.assertEqual(result, False)

    def test_is_valid_mobile(self):
        valid_mobiles = [
            "912345678",      # 9 digits (no DDD)
            "923456789",
            "934567890",

            "11912345678",    # DDD + 9 digits
            "21923456789",
            "31934567890",
            "41945678901",

            "5511912345678",  # 55 + DDD + 9 digits
            "5521923456789",
            "5531934567890",
        ]

        for mobile in valid_mobiles:
            result = is_mobile(mobile)
            self.assertEqual(result, True)

    def test_is_invalid_mobile(self):
        invalid_mobiles = [
            "123456789",       # 9 digits but does not start with 9
            "812345678",       # starts with 8

            "1191234567",      # 10 digits (wrong length)
            "119123456789",    # 12 digits (wrong length)

            "11123456789",     # DDD ok, but does not start with 9 after DDD
            "2198345678",      # only 10 digits

            "551191234567",    # 12 digits (too short)
            "55119123456789",  # 14 digits (too long)

            "00912345678",     # invalid prefix
            "abcdefghijk",     # not numeric
        ]

        for mobile in invalid_mobiles:
            result = is_mobile(mobile)
            self.assertEqual(result, False)

