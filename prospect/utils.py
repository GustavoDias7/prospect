import re
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
import time
from PIL import Image
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


def resize_image(image: Image, max_length: int) -> Image:
    length = image.size[0] if image.size[0] >= image.size[1] else image.size[1]
    length = max_length if length >= max_length else length
    
    if image.size[0] < image.size[1]:
        # The image is in portrait mode. Height is bigger than width.

        # This makes the width fit the LENGTH in pixels while conserving the ration.
        resized_image = image.resize((length, int(image.size[1] * (length / image.size[0]))))

        # Amount of pixel to lose in total on the height of the image.
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
        