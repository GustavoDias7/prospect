from django.db import models
from prospect.utils import remove_non_numeric
import datetime
from pytz import timezone
from PIL import Image, ImageFont, ImageDraw
import requests
from io import BytesIO
import textwrap
from prospect.utils import resize_image
import os
from django.conf import settings
import cairosvg
import re

# Create your models here.
class Contact(models.Model):
    facebook_page = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    whatsapp = models.CharField(max_length=13, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    instagram = models.CharField(max_length=30, null=True, blank=True)
    qualified = models.BooleanField(default=None, help_text="Account has a website, has been inactive for an extended period, or the page is not found.", null=True, blank=True)
    decider = models.OneToOneField(to="Decider", on_delete=models.SET_NULL, null=True, blank=True)
    
    def get_facebook(self):
        return f"https://facebook.com{self.facebook_page}"
    
    def get_whatsapp_link(self):
        return "https://wa.me/" + remove_non_numeric(self.whatsapp)
    
    def get_website(self):
        return self.website if ("http" or "https") in self.website else f"https://{self.website}"
    
    def get_instagram_link(self):
        return "https://www.instagram.com/" + self.instagram 
    
    def __str__(self):
        if self.name: return self.name
        else: return f"Contact {self.id}"
        
class Decider(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    instagram = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    followed = models.BooleanField(default=False)
    
    def get_whatsapp_link(self, add_message: bool | None = True):
        phone = remove_non_numeric(self.phone)
        
        if add_message:
            message = "Olá, tudo bem?"
            now = datetime.datetime.now(timezone('America/Sao_Paulo'))
            
            morning = now.hour >= 6 and now.hour <= 11
            afternoon = now.hour >= 12 and now.hour <= 17
            night = now.hour >= 18
            
            if morning:
                message = "Olá, bom dia!"
            elif afternoon:
                message = "Olá, boa tarde!"
            elif night:
                message = "Olá, boa noite!"
            
            return f"https://web.whatsapp.com/send/?phone={phone}&text={message}"
        else:
            return f"https://web.whatsapp.com/send/?phone={phone}"
    
    def get_instagram_link(self):
        return f"https://www.instagram.com/{self.instagram}"
    
    def get_first_name(self):
        if self.name:
            return self.name.split(" ")[0]
    
    def fcellphone(self):
        if self.phone:
            if len(self.phone) == 13: 
                return f"+{self.phone[0:2]} ({self.phone[2:4]}) {self.phone[4]} {self.phone[5:9]}-{self.phone[9:13]}"
            if len(self.phone) == 11 and int(self.phone[2]) == 9: 
                return f"({self.phone[0:2]}) {self.phone[2]} {self.phone[3:7]}-{self.phone[7:11]}"
            elif len(self.phone) == 9 and int(self.phone[0]) == 9: 
                return f"{self.phone[0:5]}-{self.phone[5:9]}"
            else: 
                return self.phone
        else:
            return None
            
    def __str__(self):
        if self.name: return self.name
        else: return f"Decider {self.id}"
        
# class SeleniumDriver(models.Model):
#     name = models.CharField(max_length=50, null=True, blank=True)

class BusinessContact(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    cellphone = models.CharField(max_length=13, null=True, blank=True)
    telephone = models.CharField(max_length=12, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    website2 = models.URLField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    qualified = models.BooleanField(default=None, help_text="Account has a website, has been inactive for an extended period, or the page is not found.", null=True, blank=True)
    decider = models.OneToOneField(to="Decider", on_delete=models.SET_NULL, null=True, blank=True)
    contacted = models.BooleanField(default=False)
    last_post = models.DateTimeField(default=None, null=True, blank=True)
    archived = models.BooleanField(default=False)
    menu = models.BooleanField(default=None, null=True, blank=True)
    template = models.ForeignKey("Template", null=True, blank=True, on_delete=models.SET_NULL)
    followed = models.BooleanField(default=False)
    
    def get_instagram_link(self):
        return f"https://www.instagram.com/{self.username}"
    
    def get_whatsapp_link(self, add_message: bool | None = True):
        cellphone = remove_non_numeric(self.cellphone)
        
        if add_message:
            message = "Olá, tudo bem?"
            now = datetime.datetime.now(timezone('America/Sao_Paulo'))
            
            morning = now.hour >= 6 and now.hour <= 11
            afternoon = now.hour >= 12 and now.hour <= 17
            night = now.hour >= 18
            
            if morning:
                message = "Olá, bom dia!"
            elif afternoon:
                message = "Olá, boa tarde!"
            elif night:
                message = "Olá, boa noite!"
            
            return f"https://web.whatsapp.com/send/?phone={cellphone}&text={message}"
        else:
            return f"https://web.whatsapp.com/send/?phone={cellphone}"
    
    def fcellphone(self):
        if self.cellphone:
            if len(self.cellphone) == 13: 
                return f"+{self.cellphone[0:2]} ({self.cellphone[2:4]}) {self.cellphone[4]} {self.cellphone[5:9]}-{self.cellphone[9:13]}"
            if len(self.cellphone) == 11 and int(self.cellphone[2]) == 9: 
                return f"({self.cellphone[0:2]}) {self.cellphone[2]} {self.cellphone[3:7]}-{self.cellphone[7:11]}"
            elif len(self.cellphone) == 9 and int(self.cellphone[0]) == 9: 
                return f"{self.cellphone[0:5]}-{self.cellphone[5:9]}"
            else: 
                return self.cellphone
        else:
            return None
        
    def ftelephone(self):
        if self.telephone:
            if len(self.telephone) == 12: 
                return f"+{self.telephone[0:2]} ({self.telephone[2:4]}) {self.telephone[4:8]}-{self.telephone[8:12]}"
            if len(self.telephone) == 10: 
                return f"({self.telephone[0:2]}) {self.telephone[2:6]}-{self.telephone[6:10]}"
            elif len(self.telephone) == 8: 
                return f"{self.telephone[0:4]}-{self.telephone[4:8]}"
            else: 
                return self.telephone
        else:
            return None
    
    def __str__(self):
        if self.username: return self.username
        else: return f"Instagram {self.id}"
        
class Website(models.Model):
    website = models.CharField(max_length=200, unique=True, null=True, blank=True)
    qualified = models.BooleanField(default=None, null=True, blank=True)
    whatsapp = models.BooleanField(default=False)
    linktree = models.BooleanField(default=False)
    bitly = models.BooleanField(default=False)
    social_media = models.BooleanField(default=False)

class VacancyCategory(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = "vacancy category"
        verbose_name_plural = "vacancy categories"
    
    def __str__(self):
        return self.name

class Template(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    message = models.TextField(max_length=1200, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class Curriculum(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    file = models.FileField(upload_to=None, max_length=100)
    
    def __str__(self):
        return self.name

class VacancyHiring(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.name

class VacancyLevel(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Vacancy(models.Model):
    name = models.CharField(max_length=150)
    job_view = models.CharField(max_length=200, unique=True, null=True, blank=True)
    description = models.TextField(max_length=600, null=True, blank=True)
    hiring = models.ForeignKey(VacancyHiring, null=True, on_delete=models.SET_NULL)
    level = models.ForeignKey(VacancyLevel, null=True, blank=True, on_delete=models.SET_NULL)
    salary = models.SmallIntegerField(default=0)
    company = models.ForeignKey("Company", null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(VacancyCategory, null=True, on_delete=models.SET_NULL)
    curriculum = models.ForeignKey(Curriculum, null=True, blank=True, on_delete=models.SET_NULL)
    contacted = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    template = models.ForeignKey(Template, null=True, on_delete=models.SET_NULL)
    
    class Meta:
        verbose_name = "vacancy"
        verbose_name_plural = "vacancies"
    
    def __str__(self):
        return self.name

class LinkedInContact(models.Model):
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    archived = models.BooleanField(default=False)
    
    def get_linkedin_link(self):
        return f"https://www.linkedin.com/in/{self.username}"
    
    def __str__(self):
        if self.username: return self.username
        else: return f"LinkedIn {self.id}"
    
class Company(models.Model):
    name = models.CharField(max_length=50)
    website = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    linkedin = models.CharField(max_length=200, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    qualified = models.BooleanField(default=None, null=True, blank=True)
    contacted = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    template = models.ForeignKey(Template, null=True, blank=True, on_delete=models.SET_NULL)
    employer = models.ForeignKey(LinkedInContact, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        verbose_name = "company"
        verbose_name_plural = "companies"
    
    def __str__(self):
        return self.name
    
class PostSVG(models.Model):
    name = models.CharField(max_length=30)
    content = models.TextField(max_length=1500)
    
    def __str__(self):
        if self.name: return self.name
        else: return self.id
    
class PostType(models.Model):
    name = models.CharField(max_length=30)
    
    def __str__(self):
        if self.name: return self.name
        else: return self.id
        
class Hashtag(models.Model):
    name = models.CharField(max_length=30)
    content = models.TextField(max_length=150)
    
    def __str__(self):
        if self.name: return self.name
        else: return self.id
    
class PostVariant(models.Model):
    name = models.CharField(max_length=30)
    background_color = models.CharField(max_length=6)
    text_color = models.CharField(max_length=6)
    font_family = models.CharField(max_length=200)
    
    def __str__(self):
        if self.name: return self.name
        else: return self.id

class Post(models.Model):
    phrase = models.TextField(max_length=150)
    variant = models.ForeignKey(PostVariant, null=True, on_delete=models.SET_NULL)
    hashtag = models.ForeignKey(Hashtag, null=True, on_delete=models.SET_NULL)
    posted = models.BooleanField(default=False)
    background_image1 = models.ImageField(null=True, blank=True)
    background_image2 = models.ImageField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    type = models.ForeignKey(PostType, null=True, blank=True, on_delete=models.SET_NULL)
    font_size = models.PositiveSmallIntegerField(default=64)
    square_area = models.PositiveSmallIntegerField(default=1080)
    text_wrap = models.PositiveSmallIntegerField(default=30)
    svg = models.ForeignKey(PostSVG, null=True, blank=True, on_delete=models.SET_NULL)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        req = requests.get(self.variant.font_family)
            
        img = Image.new(
            "RGBA",
            (self.square_area, self.square_area),
            f"#{self.variant.background_color}"
        )
        
        if bool(self.background_image1) and bool(self.background_image2) == False:
            background_image1 = Image.open(self.background_image1)
            
            background_image1 = resize_image(background_image1, self.square_area)
            
            overlay_color = "#222222"
            overlay_img = Image.new("RGBA", (self.square_area, self.square_area), overlay_color)
            img.paste(background_image1, (0, 0)) 
            
            img = Image.blend(overlay_img, img, alpha=0.3)
        elif bool(self.background_image1) and bool(self.background_image2):
            background_image1 = Image.open(self.background_image1)
            background_image2 = Image.open(self.background_image2)
            
            background_image1 = resize_image(background_image1, self.square_area)
            background_image2 = resize_image(background_image2, self.square_area)
            
            crop_image = {
                "left": self.square_area / 4,
                "top": 0,
                "right": 3 * (self.square_area / 4),
                "bottom": self.square_area,
            }
            
            background_image1 = background_image1.crop(tuple(crop_image.values()))
            background_image2 = background_image2.crop(tuple(crop_image.values()))
            
            overlay_color = "#222222"
            overlay_img = Image.new("RGBA", (self.square_area, self.square_area), overlay_color)
            img.paste(background_image1, (0, 0)) 
            img.paste(background_image2, (int(self.square_area/2), 0))
            
            img = Image.blend(overlay_img, img, alpha=0.3)
        else:
            if self.svg == None:
                self.svg = PostSVG.objects.order_by("?").first()
            pattern = r'(fill|stroke)="#[A-Fa-f0-9]{6}"'
            replacement = f"{self.variant.text_color}"
            new_svg_template = re.sub(pattern, lambda m: f'{m.group(1)}="#{replacement}"', self.svg.content)
            filelike_obj = BytesIO(cairosvg.svg2png(new_svg_template, background_color=f"#{self.variant.background_color}"))
            background_template = Image.open(filelike_obj)
            background_template = resize_image(background_template, self.square_area)
            img.paste(background_template, (0, 0))
            
        draw = ImageDraw.Draw(img)
        
        line_height = 0 # line_height
        
        main_text = "\n".join(textwrap.wrap(self.phrase, width=self.text_wrap))
        main_text_font = ImageFont.truetype(BytesIO(req.content), size=self.font_size)
        main_text_draw_point = (self.square_area/2, self.square_area/2) # x / y
        
        draw.text(
            main_text_draw_point, 
            main_text, 
            spacing=line_height, 
            anchor='mm', 
            fill=f"#{self.variant.text_color}", 
            font=main_text_font, 
            align="center"
        )
        
        # username_font = ImageFont.truetype(BytesIO(req.content), size=40)
        # username_draw_point = (self.square_area/2, 1000) # x / y
        # draw.text(
        #     username_draw_point, 
        #     f"Curta e compartilhe", 
        #     spacing=line_height, 
        #     anchor='mm', 
        #     fill=f"#{self.variant.text_color}", 
        #     font=username_font, 
        #     align="center"
        # )
        
        image_name = f'post-{self.id}.png'
        media_path = f"./media/{image_name}"
        img.save(media_path)
        
        try:
            if bool(self.background_image1):
                os.remove(self.background_image1.path)
                self.background_image1 = None
            
            if bool(self.background_image2):
                os.remove(self.background_image2.path)
                self.background_image2 = None
        except OSError as e:
            print(e)

        self.image = image_name
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        if self.phrase:
            short_phrase = ""
            
            length = 10
            if len(self.phrase.split(" ")) > length:
                short_phrase = " ".join(self.phrase.split(" ")[:length]) + "..."
            else:
                short_phrase = " ".join(self.phrase.split(" "))
                
            return f"id {self.id}: {short_phrase}"
        else: 
            return self.id


class PostGenerator(models.Model):
    phrases = models.TextField(max_length=1500)
    
    def save(self, *args, **kwargs):
        
        phrases = self.phrases.split(";")
        
        for phrase in phrases:
            post = Post()
            post.phrase = phrase
            post.variant = PostVariant.objects.order_by("?").first()
            self.svg = PostSVG.objects.order_by("?").first()
            post.save()
        
        super().save(*args, **kwargs)
