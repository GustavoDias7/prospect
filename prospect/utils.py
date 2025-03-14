import re
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
import time
from PIL import Image, ImageFont, ImageDraw
import json, os

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


def get_phone(value: str):
    phone = ""
    
    phones = [
        re.search(r"\d{13}", value), # '9999999999999'
        re.search(r"\d{12}", value), # '999999999999'
        re.search(r"\(\d{2}\) \d{5}-\d{4}", value), # '(99) 99999-9999'
        re.search(r"\(\d{2}\) 9 \d{4}-\d{4}", value), # '(99) 9 9999-9999'
        re.search(r"\(\d{2}\)9 \d{4}-\d{4}", value), # '(99)9 9999-9999'
        re.search(r"\(\d{2}\)\d{5}-\d{4}", value), # '(99)99999-9999'
        re.search(r"\(\d{2}\)9.\d{4}-\d{4}", value), # '(99)9.9999-9999'
        re.search(r"\d{7}-\d{4}", value), # '9999999-9999'
        re.search(r"\(\d{2}\)\d{9}", value), # '(99)999999999'
        re.search(r"\d{2} \d{5}-\d{4}", value), # '99 99999-9999'
        re.search(r"\d{2} 9 \d{4}-\d{4}", value), # '99 9 9999-9999'
        re.search(r"\d{2} \d{5} \d{4}", value), # '99 99999 9999'
        re.search(r"\(\d{2}\) 9\d{4} \d{4}", value), # '(99) 99999 9999'
        re.search(r"\d{2} \d{5} - \d{4}", value), # '99 99999 - 9999'
        re.search(r"\d{2}.\d{5}-\d{4}", value), # '99.99999-9999'
        re.search(r"\d{2}.\d{9}", value), # '99.999999999'
        re.search(r"\d{2} 9\d{8}", value), # '99 999999999'
        re.search(r"\(\d{2}\) \d{9}", value), # '(99) 999999999'
        re.search(r"\(\d{2}\)9 \d{8}", value), # '(99)9 99999999'
        re.search(r"\(\d{2}\) 9 \d{8}", value), # '(99) 9 99999999'
        re.search(r"\d{2}9\d{8}", value), # '99999999999'
        re.search(r"\d{5}-\d{4}", value), # '99999-9999'
        re.search(r"\d{5} \d{4}", value), # '99999 9999'
        re.search(r"\d{9}", value), # '999999999'
        
        re.search(r"\(\d{2}\) \d{4}-\d{4}", value), # '(99) 9999-9999'
        re.search(r"\(\d{2}\)\d{4}-\d{4}", value), # '(99)9999-9999'
        re.search(r"\(\d{2}\)\d{8}", value), # '(99)99999999'
        re.search(r"\d{2}.\d{4}-\d{4}", value), # '99.9999-9999'
        re.search(r"\d{2}.\d{8}", value), # '99.99999999'
        re.search(r"\d{8}", value), # '99999999'
        re.search(r"\d{4}-\d{4}", value), # '9999-9999'
    ]
    
    for p in phones:
        if p: 
            phone = remove_non_numeric(p.group())
            break
    
    return phone

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

def has_string_in_list(string: str, string_list: list[str], case_sensitive=False) -> bool:
    result = False
    
    for item in string_list:
        norm_item = replace_accents(item)
        norm_string = replace_accents(string)
        
        if case_sensitive == False:
            norm_item = norm_item.lower()
            norm_string = norm_string.lower()
        
        if norm_item in norm_string:
            result = True
            break
    
    return result

def is_telephone(value: str) -> bool:
    if value == None: return False
    number = remove_non_numeric(value)
    return len(number) in (8, 10, 12)

def is_cellphone(value: str) -> bool:
    if value == None: return False
    number = remove_non_numeric(value)
    return len(number) in (9, 11, 13) and number[-9] == "9"

def open_tab(driver: webdriver.Firefox, search: str, index_tab: int, sleep: int | None = None):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[index_tab])
    driver.get(search)
    if type(sleep) == int: time.sleep(sleep)
    
def close_tab(driver: webdriver.Firefox, index_tab: int):
    driver.close()
    driver.switch_to.window(driver.window_handles[index_tab])
    
def selenium_click(driver: webdriver.Firefox, element: WebElement):
    driver.execute_script("arguments[0].click();", element)

# times = 1
def try_white(
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
    if x_axis > y_axis:
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
        fill: str, 
        font: ImageFont.ImageFont, 
        align: str,
        outline: bool = False
    ) -> Image.Image:
    bbox = draw.textbbox((0, 0), text, font=font)
    img = Image.new("RGBA", (bbox[2], bbox[3]), "#00000000")
    draw = ImageDraw.Draw(img)
    if outline:
        draw.rectangle(xy=((0, 0), (bbox[2]-1, bbox[3]-1)), outline="red")
    draw.text(
        (0, 0), 
        text=text,
        # anchor='mm', 
        fill=fill, 
        font=font, 
        align=align
    )
    return img
    
def group_vertically(images: tuple[Image.Image], gap) -> Image.Image:
    # get the greater x and y
    greater_x = 0
    max_y = gap
    for image in images:
        if image.size[0] > greater_x:
            greater_x = image.size[0]
        max_y = max_y + image.size[1]
    
    img = Image.new("RGBA", (greater_x, max_y), "#00000000")
    
    paste_y = 0
    for image in images:
        img.paste(image, (0, paste_y))
        paste_y = paste_y + image.size[1] + gap
    
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
    
def has_term(term: str, terms: list | tuple, case_sensitive: bool = False) -> bool:
    def handle_lower(value):
        new_value = replace_accents(value)
        return new_value.lower() if case_sensitive == False else new_value
    return any(handle_lower(item) in handle_lower(term) for item in terms)
        