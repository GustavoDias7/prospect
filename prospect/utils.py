from core import models
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import time
from PIL import Image, ImageFont, ImageDraw, ImageTk
import json, os
from prospect.constants import BOLD_MAP, DDD
from prospect.regex import EMAIL_PATTERN, PHONE_PATTERNS, MASKED_PHONE_PATTERNS
import random
from io import BytesIO
# import cairosvg
from moviepy.editor import VideoFileClip, AudioFileClip
import numpy as np
from moviepy.decorators import audio_video_fx
from datetime import datetime, timedelta, timezone
from django.utils.translation import gettext_lazy as _
import cv2
import urllib.parse
from tkinter import Tk, Label

@audio_video_fx
def audio_normalize(clip: AudioFileClip):
    """ Return an audio (or video) clip whose volume is normalized
        to 0db."""

    mv = clip.max_volume()
    return clip.volumex(1 / mv)

def remove_non_numeric(value:str):
    return "".join(e for e in value if e.isdigit())

def remove_non_alphanumeric(value: str):
    return "".join([e for e in value if e.isalnum()])

def fphone_number(number: str) -> str:
    is_str = number and type(number) == str
    if is_str:
        ddd = number[0:2]
        
        if len(number) == 11:
            part1 = number[2:7]
            part2 = number[7:]
        else:
            part1 = number[2:6]
            part2 = number[6:]
        
        return f"({ddd}) {part1}-{part2}"
    else:
        return ""


def get_phone(value: str) -> str:
    phone = ""
    
    phones = [
        re.search(r"\d{13}", value), # '9999999999999'
        re.search(r"\d{12}", value), # '999999999999'
        re.search(r"\(\d{2}\) \d{5}-\d{4}", value), # '(99) 99999-9999'
        re.search(r"\(\d{2}\) \d{5}.\d{4}", value), # '(99) 99999.9999'
        re.search(r"\(\d{2}\) 9 \d{4}-\d{4}", value), # '(99) 9 9999-9999'
        re.search(r"\(\d{2}\) 9 \d{4}.\d{4}", value), # '(99) 9 9999.9999'
        re.search(r"\(\d{2}\)9 \d{4}-\d{4}", value), # '(99)9 9999-9999'
        re.search(r"\(\d{2}\)9 \d{4}.\d{4}", value), # '(99)9 9999.9999'
        re.search(r"\(\d{2}\)\d{5}-\d{4}", value), # '(99)99999-9999'
        re.search(r"\(\d{2}\)\d{5}.\d{4}", value), # '(99)99999.9999'
        re.search(r"\(\d{2}\)9.\d{4}-\d{4}", value), # '(99)9.9999-9999'
        re.search(r"\(\d{2}\)9.\d{4}.\d{4}", value), # '(99)9.9999.9999'
        re.search(r"\(\d{2}\) 9.\d{4}-\d{4}", value), # '(99) 9.9999-9999'
        re.search(r"\(\d{2}\) 9.\d{4}.\d{4}", value), # '(99) 9.9999.9999'
        re.search(r"\d{7}-\d{4}", value), # '9999999-9999'
        re.search(r"\d{7}.\d{4}", value), # '9999999.9999'
        re.search(r"\(\d{2}\)\d{9}", value), # '(99)999999999'
        re.search(r"\d{2} \d{5}-\d{4}", value), # '99 99999-9999'
        re.search(r"\d{2} \d{5}.\d{4}", value), # '99 99999.9999'
        re.search(r"\d{2} 9 \d{4}-\d{4}", value), # '99 9 9999-9999'
        re.search(r"\d{2} 9 \d{4}.\d{4}", value), # '99 9 9999.9999'
        re.search(r"\d{2} 9 \d{4} \d{4}", value), # '99 9 9999 9999'
        re.search(r"\d{2} \d{5} \d{4}", value), # '99 99999 9999'
        re.search(r"\(\d{2}\) 9\d{4} \d{4}", value), # '(99) 99999 9999'
        re.search(r"\d{2} \d{5} - \d{4}", value), # '99 99999 - 9999'
        re.search(r"\d{2}.\d{5}-\d{4}", value), # '99.99999-9999'
        re.search(r"\d{2}.\d{5}.\d{4}", value), # '99.99999.9999'
        re.search(r"\d{2}-\d{5}-\d{4}", value), # '99-99999-9999'
        re.search(r"\d{2}-\d{5}.\d{4}", value), # '99-99999.9999'
        re.search(r"\d{2}.\d{9}", value), # '99.999999999'
        re.search(r"\d{2} 9\d{8}", value), # '99 999999999'
        re.search(r"\(\d{2}\) \d{9}", value), # '(99) 999999999'
        re.search(r"\(\d{2}\)9 \d{8}", value), # '(99)9 99999999'
        re.search(r"\(\d{2}\) 9 \d{8}", value), # '(99) 9 99999999'
        re.search(r"\d{2}9\d{8}", value), # '99999999999'
        re.search(r"\d{5}-\d{4}", value), # '99999-9999'
        re.search(r"\d{5}.\d{4}", value), # '99999.9999'
        re.search(r"\d{5} \d{4}", value), # '99999 9999'
        re.search(r"\d{9}", value), # '999999999'
        
        re.search(r"\(\d{2}\) \d{4}-\d{4}", value), # '(99) 9999-9999'
        re.search(r"\(\d{2}\) \d{4}.\d{4}", value), # '(99) 9999.9999'
        re.search(r"\(\d{2}\)\d{4}-\d{4}", value), # '(99)9999-9999'
        re.search(r"\(\d{2}\)\d{4}.\d{4}", value), # '(99)9999.9999'
        re.search(r"\(\d{2}\)\d{8}", value), # '(99)99999999'
        re.search(r"\d{2}.\d{4}-\d{4}", value), # '99.9999-9999'
        re.search(r"\d{2}.\d{4}.\d{4}", value), # '99.9999.9999'
        re.search(r"\d{2}-\d{4}-\d{4}", value), # '99-9999-9999'
        re.search(r"\d{2}-\d{4}.\d{4}", value), # '99-9999.9999'
        re.search(r"\d{2}.\d{8}", value), # '99.99999999'
        re.search(r"\d{8}", value), # '99999999'
        re.search(r"\d{4}-\d{4}", value), # '9999-9999'
        re.search(r"\d{4}.\d{4}", value), # '9999.9999'
    ]
    
    for p in phones:
        if p: 
            phone = remove_non_numeric(p.group())
            break
    
    return phone

def get_phones(value: str) -> list[str]:
    phones = []
    text = value

    for pattern in PHONE_PATTERNS:
        while True:
            match = re.search(pattern, text)
            if not match:
                break

            phone = match.group()
            clean = remove_non_numeric(phone)
            if (is_landline(clean) or is_mobile(clean)):
                phones.append(clean)

            # remove matched part to avoid overlap
            start, end = match.span()
            text = text[:start] + " " * (end - start) + text[end:]

    # remove duplicates
    return list(dict.fromkeys(phones))

def get_emails(text: str) -> list[str]:
    return list(dict.fromkeys(
        re.findall(EMAIL_PATTERN, text, re.IGNORECASE)
    ))

# get phones for patterns in html web pages
def get_phones_web(element: WebElement) -> list[str]:
    phones = []
    text = element.get_attribute("innerHTML")

    for pattern in MASKED_PHONE_PATTERNS:
        while True:
            match = re.search(pattern, text)
            if not match:
                break

            phone = match.group()

            if "%" in phone:
                break

            clean = remove_non_numeric(phone)
            if (is_landline(clean) or is_mobile(clean)):
                phones.append(clean)

            # remove matched part to avoid overlap
            start, end = match.span()
            text = text[:start] + " " * (end - start) + text[end:]

    # website
    whatsapp_websites = models.Website.objects.filter(whatsapp=True)
    a_tags = element.find_elements(By.CSS_SELECTOR, "a")
    for a_tag in a_tags:
        a_href = a_tag.get_attribute("href")
        if a_href:
            for ws in whatsapp_websites:
                if ws.website in a_href or ("tel:" in a_href):
                    phone = get_phone(a_href)
                    phones.append(phone)

    # remove duplicates
    return list(dict.fromkeys(phones))

def replace_accents(new_string_com_acento: str) -> str:
    string = new_string_com_acento
    mapa_acentos_hex = {
        'a': r'[\xe0-\xe6]',
        'A': r'[\xc0-\xc6]',
        'e': r'[\xe8-\xeb]',
        'E': r'[\xc8-\xcb]',
        'i': r'[\xec-\xef]',
        'I': r'[\xcc-\xcf]',
        'o': r'[\xf2-\xf6]',
        'O': r'[\xd2-\xd6]',
        'u': r'[\xf9-\xfc]',
        'U': r'[\xd9-\xdc]',
        'c': r'\xe7',
        'C': r'\xc7',
        'n': r'\xf1',
        'N': r'\xd1'
    }

    for letra, expressao_regular in mapa_acentos_hex.items():
        string = re.sub(expressao_regular, letra, string)
    
    return string

# check if each substring is in each full strings
def has_substrings_in_strings(
    substrings: str | list[str],
    strings: str | list[str],
    case_sensitive: bool = False,
    normalize: bool = True
) -> bool:

    # normalize inputs
    if isinstance(substrings, str):
        substring_list = [substrings] if substrings else []
    elif isinstance(substrings, list):
        substring_list = [s for s in substrings if isinstance(s, str)]
    else:
        substring_list = []

    if isinstance(strings, str):
        string_list = [strings] if strings else []
    elif isinstance(strings, list):
        string_list = [s for s in strings if isinstance(s, str)]
    else:
        string_list = []

    # helper normalization function
    def norm(s: str) -> str:
        if normalize:
            s = replace_accents(s)
        if not case_sensitive:
            s = s.lower()
        return s

    # preprocess substrings once
    norm_substrings = [norm(sub) for sub in substring_list]

    # check
    for string in string_list:
        norm_string = norm(string)

        for sub in norm_substrings:
            if sub in norm_string:
                return True

    return False

def has_term(term: str, terms: list | tuple, case_sensitive: bool = False) -> bool:
    def handle_lower(value):
        new_value = replace_accents(value)
        return new_value.lower() if case_sensitive == False else new_value
    return any(handle_lower(item) in handle_lower(term) for item in terms)

def is_telephone(value: str) -> bool:
    if value == None: return False
    number = remove_non_numeric(value)
    return len(number) in (8, 10, 12)

def is_cellphone(value: str) -> bool:
    if value == None: return False
    number = remove_non_numeric(value)
    return len(number) in (9, 11, 13) and number[-9] == "9"

def is_landline(value: str) -> bool:
    if value == None: return False
    number = remove_non_numeric(value)
    if len(number) == 8:
        return True
    elif len(number) == 10:
        is_ddd = number[0:2] in DDD
        return is_ddd
    elif len(number) == 12:
        is_br_code = number[0:2] == "55"
        is_ddd = number[2:4] in DDD
        return is_br_code and is_ddd
    else:
        return False

def is_mobile(value: str) -> bool:
    if value == None: return False
    number = remove_non_numeric(value)

    if len(number) >= 9 and number[-9] != "9":
        return False
    elif len(number) == 9:
        return True
    elif len(number) == 11:
        is_ddd = number[0:2] in DDD
        return is_ddd
    elif len(number) == 13:
        is_br_code = number[0:2] == "55"
        is_ddd = number[2:4] in DDD
        return is_br_code and is_ddd
    else:
        return False

# times = 1
def try_while(
        callback, 
        times: int = 1, 
        sleep_initial: int | None = None, 
        sleep_before: int | None = None, 
        sleep_after: int | None = None
    ):
    
    if type(sleep_initial) == int:
        time.sleep(sleep_initial)
    
    counter = 1
    
    while counter <= times:
        if type(sleep_before) == int:
            time.sleep(sleep_before)
            
        result = callback()
        print("result:", result)
        print("counter:", counter)
        
        if type(result) != bool:
            raise TypeError("The function should return a boolean value.")
    
        if result: break
        else: counter = counter + 1
        
        if type(sleep_after) == int:
            time.sleep(sleep_after)


def resize_image(image: Image.Image, length: int) -> Image.Image:
    # length = image.size[0] if image.size[0] >= image.size[1] else image.size[1]
    # length = max_length if length >= max_length else length
    
    if image.size[0] < image.size[1]:
        # The image is in portrait mode. Height is bigger than width.

        # This makes the width fit the LENGTH in pixels while conserving the ration.
        resized_image = image.resize((length, int(image.size[1] * (length / image.size[0]))))

        required_loss = (resized_image.size[1] - length)

        # Crop the height of the image so as to keep the center part.
        resized_image = resized_image.crop(
            box=(0, required_loss / 2, length, resized_image.size[1] - required_loss / 2))

        # We now have a length*length pixels image.
        return resized_image
    else:
        # This image is in landscape mode or already squared. The width is bigger than the heihgt.

        # This makes the height fit the LENGTH in pixels while conserving the ration.
        resized_image = image.resize((int(image.size[0] * (length / image.size[1])), length))

        # Amount of pixel to lose in total on the width of the image.
        required_loss = resized_image.size[0] - length

        # Crop the width of the image so as to keep 1080 pixels of the center part.
        resized_image = resized_image.crop(
            box=(required_loss / 2, 0, resized_image.size[0] - required_loss / 2, length))

        # We now have a length*length pixels image.
        return resized_image
    
def crop_horizontal_image(
        image: Image.Image, 
        aspect_ratio: tuple[int, int],
        resize_width: int | None = None
    ) -> Image.Image:
    
    x_axis = image.size[0]
    y_axis = image.size[1]
    
    w_aspect_ratio = aspect_ratio[0]
    y_aspect_ratio = aspect_ratio[1]
    
    # check horizontal dementions
    if x_axis >= y_axis:
        # get the height
        # calculate the height -> 16 . x = width . 9 -> x = width . 9 / 16
        height = (x_axis * y_aspect_ratio) / w_aspect_ratio
        cropped_image = None
        if height < y_axis:
            required_loss = y_axis - height
            cropped_image = image.crop(
                box=(0, required_loss / 2, x_axis, y_axis - required_loss / 2)
            )
        elif height > y_axis:
            # calculate the width 16 . height = x . 9
            width = (y_axis * w_aspect_ratio) / y_aspect_ratio
            required_loss = x_axis - width
            cropped_image = image.crop(
                box=(required_loss / 2, 0, x_axis - required_loss / 2, y_axis)
            )
        else:
            cropped_image = image
        
        resizes_image = cropped_image.resize((
            int(resize_width),
            int((resize_width * y_aspect_ratio) / w_aspect_ratio)
        ))
        
        return resizes_image
    else:
        return image
    


def text_to_image(
        draw: ImageDraw.ImageDraw, 
        text: str, 
        width: int,
        fill: str, 
        font: ImageFont.ImageFont, 
        align: str,
        outline: bool = False
    ) -> Image.Image:
    
    available_width = width
    wrapped_text = ""
    
    space_bbox = draw.textbbox((0, 0), " ", font=font)
    space_img = Image.new("RGBA", (space_bbox[2], space_bbox[3]), "#00000000")
    
    splitted_text = text.strip().split(" ")
    for index, word in enumerate(splitted_text):
        word_bbox = draw.textbbox((0, 0), word, font=font)
        word_img = Image.new("RGBA", (word_bbox[2], word_bbox[3]), "#00000000")
        word_width = word_img.size[0]
        space_width = space_img.size[0]
        
        if "\n" in word:
            available_width = width
            
        if (word_width + space_width) <= available_width:
            wrapped_text = wrapped_text + word
            
            if index + 1 < len(splitted_text):
                wrapped_text = wrapped_text + " "
                available_width = available_width - word_width - space_width
        elif word_width <= available_width:
            wrapped_text = wrapped_text + word
            available_width = available_width - word_width
        elif word_width > available_width:
            wrapped_text = wrapped_text + "\n" + word
            available_width = width - word_width
            
            if (word_width + space_width) <= available_width:
                wrapped_text = wrapped_text + " "
                available_width = available_width - space_width
            
            # if available_width is negative (word_width > width[width of main container])
            # reset and start from the top
            if available_width < 0:
                available_width = width
        
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    img = Image.new("RGBA", (bbox[2], bbox[3]), "#00000000")
    draw = ImageDraw.Draw(img)
    if outline: draw.rectangle(xy=((0, 0), (bbox[2]-1, bbox[3]-1)), outline="red")
    draw.text(
        (0, 0), 
        text=wrapped_text,
        # anchor='mm', 
        fill=fill, 
        font=font, 
        align=align
    )
    return img
    
def group_vertically(images: tuple[Image.Image], gap: int, align: str = "left") -> Image.Image:
    # setup the width and height of the group element
    # grow the width and height when recognize a greater value
    group_x = 0
    group_y = 0
    for index, image in enumerate(images):
        if image.size[0] > group_x:
            group_x = image.size[0]
        group_y = group_y + image.size[1]
        add_gap = index + 1 != len(images)
        if add_gap: group_y = group_y + gap
    
    img = Image.new("RGBA", (group_x, group_y), "#00000000")
    
    paste_y = 0
    for image in images:
        paste_x = 0
        
        if align == "center":
            paste_x = int((group_x - image.size[0]) / 2)
        elif align == "right":
            paste_x = group_x - image.size[0]
            
        img.paste(image, (paste_x, paste_y))
        paste_y = paste_y + image.size[1] + gap
    
    return img

def group_horizontally(images: tuple[Image.Image], gap: int, align: str = "top") -> Image.Image:
    # setup the width and height of the group element
    # grow the width and height when recognize a greater value
    group_x = 0
    group_y = 0
    for index, image in enumerate(images):
        if image.size[1] > group_y:
            group_y = image.size[1]
        group_x = group_x + image.size[0]
        add_gap = index + 1 != len(images)
        if add_gap: group_x = group_x + gap
    
    img = Image.new("RGBA", (group_x, group_y), "#00000000")
    
    paste_x = 0
    for image in images:
        paste_y = 0
        
        if align == "center":
            paste_y = int((group_y - image.size[1]) / 2)
        elif align == "bottom":
            paste_y = group_y - image.size[1]
            
        img.paste(image, (paste_x, paste_y))
        paste_x = paste_x + image.size[0] + gap
    
    return img

def center_paste(
        container: Image.Image, 
        child: Image.Image, 
        x: bool | int, 
        y: bool | int
    ) -> Image.Image:
    result_x = 0
    result_y = 0
    
    if type(x) == bool and x:
        container_x = container.size[0]
        child_x = child.size[0]
        result_x = int((container_x - child_x) / 2)
    elif type(x) == int and x > 0:
        result_x = x
    if  type(y) == bool and y:
        container_y = container.size[1]
        child_y = child.size[1]
        result_y = int((container_y - child_y) / 2)
    elif type(y) == int and y > 0:
        result_y = y
        
    return container.paste(child, (result_x, result_y), child)

def rounded_corners(im: Image.Image, rad: int):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def generate_rectangle(
    size: tuple[int, int],
    border_width: int,
    border_color: str,
    fill_color: str,
    border_radius: int
) -> Image.Image:
    width = size[0]
    height = size[1]
    
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect 
            x="{border_width / 2}" 
            y="{border_width / 2}" 
            rx="{border_radius}" 
            ry="{border_radius}"
            width="{width - border_width}" 
            height="{height - border_width}"
            fill="{fill_color}"
            stroke="{border_color}"
            stroke-width="{border_width}" 
            stroke-linejoin="round"
        />
    </svg>'''

    # Convert SVG to PNG using cairosvg
    # png_bytes = cairosvg.svg2png(bytestring=svg.encode('utf-8'))

    # Load PNG into a Pillow Image
    # image = Image.open(BytesIO(png_bytes)).convert("RGBA")
    
    # return 
    return None

def save_cookies(driver: webdriver.Firefox, filename: str):
    # Get and store cookies after login
    cookies = driver.get_cookies()

    # Store cookies in a file
    with open(f'{filename}.json', 'w') as file:
        json.dump(cookies, file)
        
    print('New Cookies saved successfully')


def load_cookies(driver: webdriver.Firefox, filename: str):
    # Check if cookies file exists
    if f'{filename}.json' in os.listdir():

        # Load cookies to a vaiable from a file
        with open(f'{filename}.json', 'r') as file:
            cookies = json.load(file)
        
        driver.delete_all_cookies()

        # Set stored cookies to maintain the session
        for cookie in cookies:
            driver.add_cookie(cookie)
        
        # driver.refresh() # Refresh Browser after login
    
def get_dimentions(aspect_ratio: str, width: int, type: int | None = None):
    numerator, denominator = aspect_ratio.split(":")
    result = (float(width), width * int(denominator) / int(numerator))
    if type == int:
        return (int(result[0]), int(result[1]))
    else:
        return result

def convert_to_bold(input_text):
    return ''.join([BOLD_MAP.get(char, char) for char in input_text])

def boldify(input_text, upper_case: bool = False):
    def replace_match(match):
        text = match.group(1)
        if upper_case: text = text.upper()
        return convert_to_bold(text)

    modified_text = re.sub(r'\*\*(.*?)\*\*', replace_match, input_text)
    return modified_text

def log_link(uri, label=None):
    if label is None: 
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST 
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)

def choice_items(array):
    copy = array[:]  # Make a shallow copy of the list
    random.shuffle(copy)  # Shuffle the copy in-place

    phrase = copy[0] if copy else ""

    # Look for a pattern like "{option1|option2|...}"
    match = re.search(r"{([^}]+)}", phrase)
    if match:
        options = match.group(1).split('|')
        random_word = random.choice(options)
        phrase = phrase.replace(match.group(0), random_word)

    return phrase


def normalize_audio(clip_path: str, target_dBFS=-1.0, sample_duration=5, fps=44100) -> VideoFileClip:
    """
    Normalize the audio of a video clip to a target dBFS level.
    """
    # Extract the audio as an array
    clip = VideoFileClip(clip_path)
    audio = clip.audio

    # Only analyze the first few seconds to avoid large memory usage
    sample_clip = audio.subclip(0, min(sample_duration, clip.duration))
    audio_array = sample_clip.to_soundarray(fps=fps)

    # Ensure audio array is 2D (samples, channels)
    if audio_array.ndim == 1:
        audio_array = np.expand_dims(audio_array, axis=1)

    peak = np.max(np.abs(audio_array))
    if peak == 0:
        print("Audio is silent. Skipping normalization.")
        return clip

    # Calculate gain factor
    target_linear = 10 ** (target_dBFS / 20.0)
    factor = target_linear / peak

    print(f"Peak: {peak:.4f} → Gain factor: {factor:.4f}")

    # Apply volume adjustment
    normalized_audio = audio.volumex(factor)
    return clip.set_audio(normalized_audio)

def is_multiple_of(a, b, eps=1e-10):
    return abs(a % b) < eps

def get_time_offset(my_datetime: datetime):
    time = None
    if datetime.now(timezone.utc) > my_datetime:
        time = datetime.now(timezone.utc) - my_datetime
    else:
        time = my_datetime - datetime.now(timezone.utc)
        
    result = ""
    
    if time.days == 0:
        hours = int(time.total_seconds()/60.0/60.0)
        
        if hours == 0:
            minutes = int(time.total_seconds()/60.0)
            
            if minutes == 0:
                seconds = int(time.total_seconds())
                result = _(f"{seconds}s")
            else:
                result = _(f"{minutes} min")
            
        else: 
            result = _(f"{hours}h")
        
    elif time.days == 1:
        result = _(f"{time.days} day")
    elif time.days >= 2 and time.days <= 30:
        result = _(f"{time.days} days")
    else:
        months = int(time.days / 30)
        if months == 1:
            result = _(f"{months} month")
        elif months >= 2 and months <= 12:
            result = _(f"{months} months")
        else:
            years = int(months / 12)
            if years == 1:
                result = _(f"{years} year")
            elif years >= 2:
                result = _(f"{years} years")
            
    return result

def parse_phone(phone_number: str) -> dict:
    if not phone_number:
        return None

    digits = re.sub(r'\D', '', phone_number)

    if len(digits) < 8:
        return None

    country_code = "55"
    ddd = ""
    number = ""

    if len(digits) in [8, 9]:
        number = digits

    elif len(digits) in [10, 11]:
        ddd = digits[:2]
        number = digits[2:]

    elif len(digits) in [12, 13] and digits.startswith("55"):
        ddd = digits[2:4]
        number = digits[4:]

    else:
        return None

    return {
        "country_code": country_code,
        "ddd": ddd,
        "number": number,
    }

def show_image(path):
    img = cv2.imread(path)
    cv2.imshow("Preview", img)
    cv2.moveWindow("Preview", 0, 0)
    cv2.waitKey(1)  # waits until you press a key
    cv2.destroyAllWindows()

def extract_social_usernames(text: str):
    data = {
        "linkedin": [],
        "instagram": [],
        "facebook": []
    }

    # LinkedIn
    linkedin_pattern = r'(?:https?://)?(?:[\w]+\.)?linkedin\.com/company/([\w\-\.]+)'
    
    # Instagram
    instagram_pattern = r'(?:https?://)?(?:www\.)?instagram\.com/([\w\._]+)'
    
    # Facebook
    facebook_pattern = r'(?:https?://)?(?:www\.)?facebook\.com/([\w\.]+)'

    ig_blacklist = {'p', 'reel', 'stories', 'explore', 'accounts', 'tv', 'policies'}
    fb_blacklist = {'pages', 'groups', 'events', 'marketplace', 'watch', 'login', 'share', 'tr', 'sharer'}

    # Extract
    data["linkedin"] = list(set(re.findall(linkedin_pattern, text)))

    data["instagram"] = list({
        u for u in re.findall(instagram_pattern, text)
        if u.lower() not in ig_blacklist
    })

    data["facebook"] = list({
        u for u in re.findall(facebook_pattern, text)
        if u.lower() not in fb_blacklist
    })

    return data

def get_path(name) -> dict:
        screenshot_temp_path = "temp"
        file_ext = ".png"
        filename = f"{name}{file_ext}"
        path = os.path.join(screenshot_temp_path, filename)
        return path

def open_image(name: str, driver: webdriver.Firefox) -> Tk: 
    root = Tk()
    root.geometry("1300x800+0+0")
    path = get_path(name)
    driver.save_screenshot(path)
    img = Image.open(path)
    img = ImageTk.PhotoImage(img)
    label = Label(root, image=img)
    label.pack()
    root.update()
    return root

# selenium utils

# open a new tab and search on tab
def open_tab(driver: webdriver.Firefox, search: str, index_tab: int = 0):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[index_tab])
    driver.get(search)
    
def close_tab(driver: webdriver.Firefox, index_tab: int):
    driver.close()
    driver.switch_to.window(driver.window_handles[index_tab])

def selenium_click(driver: webdriver.Firefox, element: WebElement, sleep: int | None = None):
    driver.execute_script("arguments[0].click();", element)
    if type(sleep) == int: time.sleep(sleep)

def open_whatsapp_sidebar(driver: webdriver.Firefox) -> webdriver.Firefox:
    try:
        # open chat sidebar "Profile details" 
        role_buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
        if role_buttons and len(role_buttons) >= 1:
            for role_button in role_buttons:
                title_attr = role_button.get_attribute("title")
                terms = ("Profile details", "Dados do perfil")
                # if has_string_in_list(title_attr, terms):
                #     driver.execute_script("arguments[0].click();", role_button)
                #     break
    except Exception as e:
        print(e)
        print("open_whatsapp_sidebar")
    
    return driver

def get_whatsapp_sidebar_data(driver: webdriver.Firefox) -> dict:
    result = {'urls': [], 'emails': [], 'address': None}
    
    try:
        # get urls and emails from sidebar
        links = driver.find_elements(By.CSS_SELECTOR, "section a")
        if links and len(links) >= 1:
            for link in links:
                url = link.get_attribute("href")

                if "maps.google.com" in url:
                    result["address"] = url
                elif "http" in url:
                    result["urls"].append(url)
                elif "mailto" in url:
                    email = url.replace("mailto:", "")
                    result["emails"].append(email)
    except Exception as e:
        print(e)
        print("get_whatsapp_sidebar_data")

    return result


