from django.test import TestCase
from prospect.utils import has_string_in_list
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import requests
from prospect.utils import get_dimentions, text_to_image
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