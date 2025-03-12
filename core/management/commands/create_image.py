from django.core.management.base import BaseCommand
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import requests
from io import BytesIO
import textwrap
from django.conf import settings
from prospect.utils import resize_image

def ReduceOpacity(im: Image, opacity: float):
    """
    Returns an image with reduced opacity.
    Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/362879
    """
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

class Command(BaseCommand):
    def handle(self, *args, **options):
        req = requests.get("https://github.com/googlefonts/roboto-2/raw/refs/heads/main/src/hinted/Roboto-Regular.ttf")
        
        square_area = 1080
        
        background1 = Image.open(settings.BASE_DIR / "pizza7.jpg")
        background2 = Image.open(settings.BASE_DIR / "burger.jpg")
        
        background1 = resize_image(background1, square_area)
        background2 = resize_image(background2, square_area)
        
        crop_image = {
            "left": square_area / 4,
            "top": 0,
            "right": 3 * (square_area / 4),
            "bottom": square_area,
        }
        
        background1 = background1.crop(tuple(crop_image.values()))
        background2 = background2.crop(tuple(crop_image.values()))
        
        overlay = "#222222"
        solid_color_img = Image.new("RGBA", (square_area, square_area), overlay)
        img = Image.new("RGBA", (square_area, square_area))
        img.paste(background1, (0, 0)) 
        img.paste(background2, (int(square_area/2), 0))
        
        img = Image.blend(solid_color_img, img, alpha=0.3)

        draw = ImageDraw.Draw(img)
        
        line_height = 0 # line_height
        text_color = "white"
        
        main_text = "Lorem ipsum dolor sit amet. Rem veniam fugit eos tempora dolorem et corrupti dolore."
        main_text = "\n".join(textwrap.wrap(main_text, width=30))
        main_text_font = ImageFont.truetype(BytesIO(req.content), size=64)
        main_text_draw_point = (square_area/2, square_area/2) # x / y
        
        draw.text(main_text_draw_point, main_text, spacing=line_height, anchor='mm', fill=text_color, font=main_text_font, align="center")# font=font
        
        username = "@site.netdelivery"
        username_font = ImageFont.truetype(BytesIO(req.content), size=40)
        username_draw_point = (square_area/2, 1000) # x / y
        draw.text(username_draw_point, username, spacing=line_height, anchor='mm', fill=text_color, font=username_font, align="center")# font=font
        
        img.save('test_image.png')

