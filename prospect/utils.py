import re
# from unidecode import unidecode

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
        re.search(r"\(\d{2}\) \d{4}-\d{4}", value), # '(99) 9999-9999'
        re.search(r"\(\d{2}\)\d{4}-\d{4}", value), # '(99)9999-9999'
        re.search(r"\(\d{2}\)\d{4}\d{4}", value), # '(99)99999999'
        re.search(r"\(\d{2}\) \d{5}-\d{4}", value), # '(99)999999999'
        re.search(r"\d{2} \d{5}-\d{4}", value), # '99 99999-9999'
        re.search(r"\(\d{2}\) \d{9}", value), # '(99) 999999999'
        re.search(r"\d{5}-\d{4}", value), # '99999-9999'
        re.search(r"\(\d{2}\)9 \d{8}", value), # '(99)9 99999999'
        re.search(r"\d{9}", value), # '999999999'
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