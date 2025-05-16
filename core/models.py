from django.db import models
from prospect.utils import remove_non_numeric, has_string_in_list
import datetime
from pytz import timezone
from prospect.constants import ASPECT_RATIOS, VERTICAL_ASPECT_RATIOS, DDD, COLORS, INTERACTION_CONTACTS, INTERACTION_STATUS
import random
from django.urls import reverse

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
    staff_member = models.OneToOneField(to="StaffMember", on_delete=models.SET_NULL, null=True, blank=True)
    
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
        
class StaffMember(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    type = models.ForeignKey(to="StaffMemberType", on_delete=models.SET_NULL, null=True, blank=True)
    cnpj = models.CharField(max_length=18, null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    instagram = models.CharField(max_length=30, null=True, blank=True)
    facebook = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    contacted = models.BooleanField(default=False)
    is_trusty = models.BooleanField(default=False, verbose_name="trusty")
    observation = models.TextField(max_length=400, null=True, blank=True)
    
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
    
    def greeting(self):
        if self.name:
            message = f"Olá, {self.get_first_name()} tudo bem?"
            now = datetime.datetime.now(timezone('America/Sao_Paulo'))
            
            morning = now.hour >= 6 and now.hour <= 11
            afternoon = now.hour >= 12 and now.hour <= 17
            night = now.hour >= 18
            
            if morning:
                message = f"Olá, {self.get_first_name()} bom dia!"
            elif afternoon:
                message = f"Olá, {self.get_first_name()} boa tarde!"
            elif night:
                message = f"Olá, {self.get_first_name()} boa noite!"
                
            return message
        else:
            message = f"Olá, tudo bem?"
        
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
    
    def get_cellphone_ddd(self) -> str | None:
        ddd = None
        
        try:
            if self.phone:
                if len(self.phone) in (13, 12):
                    ddd = DDD[self.phone[2:4]]
                elif len(self.phone) in (11, 10):
                    ddd = DDD[self.phone[0:2]]
        except Exception as e:
            print("DDD not found!")
            
        return ddd
            
    def __str__(self):
        if self.name: return self.name
        else: return f"Staff Member {self.id}"
        
class StaffMemberType(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        if self.name: return self.name
        else: return f"Staff member type {self.id}"
    
class Business(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    cnpj = models.CharField(max_length=18, null=True, blank=True)
    instagram_username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    facebook_username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    cellphone = models.CharField(max_length=13, null=True, blank=True)
    telephone = models.CharField(max_length=12, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    website2 = models.URLField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    qualified = models.BooleanField(default=None, help_text="Account has a website, has been inactive for an extended period, or the page is not found.", null=True, blank=True)
    staff_members = models.ManyToManyField(to=StaffMember, blank=True, related_name="staff_member")
    contacted = models.BooleanField(default=False)
    last_post = models.DateTimeField(default=None, null=True, blank=True)
    archived = models.BooleanField(default=False)
    template = models.ForeignKey("Template", null=True, blank=True, on_delete=models.SET_NULL)
    interaction = models.OneToOneField("Interaction", null=True, blank=True, on_delete=models.SET_NULL)
    
    def get_admin_change_url(self):
        return reverse(f'admin:{self._meta.app_label}_{self._meta.model_name}_change', args=[self.pk])
    
    def greeting_turn(self) -> str:
        now = datetime.datetime.now(timezone('America/Sao_Paulo'))
        
        morning = now.hour >= 6 and now.hour <= 11
        afternoon = now.hour >= 12 and now.hour <= 17
        night = now.hour >= 18
        turn = None
        
        if morning: turn = "bom dia"
        elif afternoon: turn = "boa tarde"
        elif night: turn = "boa noite"
            
        return turn
        
    def greeting(self):
        question = random.choice(["tudo bem", "tudo certo", "tudo certo por ai"])
        hello = random.choice(["oi", "olá"]).capitalize()
        
        if self.name:
            message = f"{hello} {self.name}, {question}?"
            now = datetime.datetime.now(timezone('America/Sao_Paulo'))
            
            morning = now.hour >= 6 and now.hour <= 11
            afternoon = now.hour >= 12 and now.hour <= 17
            night = now.hour >= 18
            
            if morning:
                message = f"{hello} {self.name}, bom dia!"
            elif afternoon:
                message = f"{hello} {self.name}, boa tarde!"
            elif night:
                message = f"{hello} {self.name}, boa noite!"
                
            return message
        else:
            message = f"{hello}, {question}?"
            
    def get_instagram_link(self):
        return f"https://www.instagram.com/{self.instagram_username}"
    
    def get_whatsapp_link(self, add_message: bool | None = True):
        phone = remove_non_numeric(self.cellphone or self.telephone)
        
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
        
    def get_cellphone_ddd(self) -> str | None:
        ddd = None
        phone = self.cellphone or self.telephone
        
        try:
            if phone:
                if len(phone) in (13, 12):
                    ddd = DDD[phone[2:4]]
                elif len(phone) in (11, 10):
                    ddd = DDD[phone[0:2]]
        except Exception as e:
            print("DDD not found!")
            
        return ddd
    
    def business_type(self):
        business = random.choice(["negócio", "estabelecimento"])
        message = f"do seu {business}"
        
        if self.name and self.instagram_username:
            if has_string_in_list("pizza", [self.name, self.instagram_username]):
                message = "da sua pizzaria"
            elif has_string_in_list("hambúrguer", [self.name, self.instagram_username]):
                message = "da sua hamburgueria"
            elif has_string_in_list("restaurante", [self.name, self.instagram_username]):
                message = "do seu restaurante"
            
        return message
    
    def is_tomorrow_or_later(self) -> bool:
        if self.move_date == None:
            return True
        else:
            return datetime.datetime.now().date() > self.move_date.date()
    
    def __str__(self):
        if self.instagram_username: return self.instagram_username
        else: return f"Instagram {self.id}"
    
    class Meta:
        verbose_name = "Business"
        verbose_name_plural = "Business"

 
class BusinessKanban(Business):
    def get_admin_change_url(self):
        return reverse(f'admin:{self._meta.app_label}_{self._meta.model_name}_change', args=[self.pk])
    class Meta:
        proxy = True
        verbose_name = "Business Kanban"
        verbose_name_plural = "Business Kanban"

class Interaction(models.Model):
    status = models.ForeignKey("InteractionStatus", on_delete=models.SET_NULL, null=True, blank=True)
    contact_via = models.ForeignKey("InteractionContactVia", on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True) #first interaction
    follow_up_date = models.DateTimeField(default=None, null=True, blank=True)
    observation = models.TextField(max_length=400, null=True, blank=True)
    
    def __str__(self):
        if self.status:
            return self.status.name
        else:
            return str(self.id)
        
class InteractionStatus(models.Model):
    name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name
    
class InteractionContactVia(models.Model):
    name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name
    
class Website(models.Model):
    website = models.CharField(max_length=200, unique=True, null=True, blank=True)
    qualified = models.BooleanField(default=None, null=True, blank=True)
    whatsapp = models.BooleanField(default=False)
    linktree = models.BooleanField(default=False)
    bitly = models.BooleanField(default=False)
    social_media = models.BooleanField(default=False)
    ignore = models.BooleanField(default=False)

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

class PostAudio(models.Model):
    name = models.CharField(max_length=30)
    file = models.FileField()
    
    def __str__(self):
        if self.name: return self.name
        else: return self.id

class Post(models.Model):
    phrase = models.TextField(max_length=150)
    variant = models.ForeignKey(PostVariant, default=1, null=True, on_delete=models.SET_NULL)
    hashtag = models.ForeignKey(Hashtag, null=True, on_delete=models.SET_NULL)
    posted = models.BooleanField(default=False)
    image1 = models.ImageField(null=True, blank=True)
    image1_url = models.URLField(null=True, blank=True, max_length=400)
    aspect_ratio_image1 = models.CharField(max_length=4, choices=ASPECT_RATIOS, default="16:9", null=True, blank=True)
    image2 = models.ImageField(null=True, blank=True)
    aspect_ratio_image2 = models.CharField(max_length=4, choices=ASPECT_RATIOS, default="16:9", null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    aspect_ratio_image = models.CharField(max_length=4, choices=VERTICAL_ASPECT_RATIOS, default="9:16", null=True, blank=True)
    audio = models.ForeignKey(PostAudio, null=True, blank=True, on_delete=models.SET_NULL)
    audio_url = models.URLField(null=True, blank=True, max_length=400)
    video = models.FileField(null=True, blank=True)
    video_duration = models.PositiveSmallIntegerField(default=10)
    type = models.ForeignKey(PostType, null=True, blank=True, on_delete=models.SET_NULL)
    font_size = models.PositiveSmallIntegerField(default=48)
    width = models.PositiveSmallIntegerField(default=1080)
    text_wrap = models.PositiveSmallIntegerField(default=40)
    svg = models.ForeignKey(PostSVG, null=True, blank=True, on_delete=models.SET_NULL)
    
    def save(self, *args, **kwargs):
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
            return str(self.id)

class PostGenerator(models.Model):
    phrases = models.TextField(max_length=1500)
    type = models.ForeignKey(PostType, null=True, blank=True, on_delete=models.SET_NULL)
    hashtag = models.ForeignKey(Hashtag, null=True, on_delete=models.SET_NULL)
    generated = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)
