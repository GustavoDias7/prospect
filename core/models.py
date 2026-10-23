from django.db import models
from prospect.utils import remove_non_numeric, get_time_offset
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
    age_range = models.CharField(max_length=30, null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    instagram = models.CharField(max_length=30, null=True, blank=True)
    facebook = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    contacted = models.BooleanField(default=False)
    is_trusty = models.BooleanField(default=False, verbose_name="trusty")
    observation = models.TextField(max_length=1000, null=True, blank=True)
    
    def get_cnpj(self):
        return remove_non_numeric(self.cnpj)

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
            return self.name.split(" ")[0].capitalize()
        else:
            return ""
    
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
    
    class Meta:
        unique_together = ('name', 'cnpj',)

    def __str__(self):
        if self.name: 
            if self.type:
                return f"{self.name} ({self.type.name})"
            else:
                return self.name
        else: return f"Staff Member {self.id}"
        
class StaffMemberType(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        if self.name: return self.name
        else: return f"Staff member type {self.id}"
    
class Business(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    name2 = models.CharField(max_length=50, null=True, blank=True)
    tags = models.ManyToManyField("Tag", blank=True)
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True)
    registration_status = models.CharField(max_length=15, null=True, blank=True)
    legal_entity_type = models.CharField(max_length=30, null=True, blank=True)
    company_port = models.CharField(max_length=30, null=True, blank=True)
    date_start_activity = models.DateTimeField(default=None, null=True, blank=True)
    capital_social = models.PositiveIntegerField(null=True, blank=True)
    instagram_username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    facebook_username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    cellphone = models.CharField(max_length=13, null=True, blank=True)
    telephone = models.CharField(max_length=12, null=True, blank=True)
    phone_numbers = models.ManyToManyField(
        "PhoneNumber",
        blank=True,
        related_name="phone_number"
    )
    website = models.URLField(max_length=200, null=True, blank=True)
    website2 = models.URLField(max_length=200, null=True, blank=True)
    domains = models.ManyToManyField(to="Domain", blank=True, related_name="domain")
    email = models.EmailField(null=True, blank=True)
    emails = models.ManyToManyField(to="Email", blank=True, related_name="email")
    cep = models.CharField(max_length=8, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    cep2 = models.CharField(max_length=8, null=True, blank=True)
    address2 = models.CharField(max_length=200, null=True, blank=True)
    staff_members = models.ManyToManyField(to=StaffMember, blank=True, related_name="staff_member")
    qualified = models.BooleanField(default=None, help_text="Account has a website, has been inactive for an extended period, or the page is not found.", null=True, blank=True)
    archived = models.BooleanField(default=False)
    favorite = models.BooleanField(default=False)
    top = models.BooleanField(default=False)
    last_post = models.DateTimeField(default=None, null=True, blank=True)
    template = models.ForeignKey("Template", null=True, blank=True, on_delete=models.SET_NULL)
    social_medias = models.ManyToManyField(to="SocialMedia", blank=True, related_name="social_media")
    # interaction = models.OneToOneField("Interaction", null=True, blank=True, on_delete=models.SET_NULL, related_name="interaction_ref")
    followers = models.PositiveIntegerField(null=True, blank=True)
    following = models.PositiveIntegerField(null=True, blank=True)
    # contacted = models.BooleanField(default=False)
    observation = models.TextField(max_length=1000, null=True, blank=True)
    
    def get_staff_members(self) -> str: 
        if len(self.staff_members.all()) > 0:
            return "\n".join(self.staff_members.all().values_list("name", flat=True))
        else:
            return "No staff member"
        
    def get_phone_numbers(self) -> str: 
        if len(self.phone_numbers.all()) > 0:
            phone_numbers = []
            for phone_number in self.phone_numbers.all():
                phone_numbers.append(phone_number.fget_full_number_whatsapp())
            return "\n".join(phone_numbers)
        else:
            return "No phone number"
        
    def get_emails(self) -> str: 
        if len(self.emails.all()) > 0:
            emails = []
            for email in self.emails.all():
                emails.append(email.address)
            return "\n".join(emails)
        else:
            return "No phone number"
        
    def get_domains(self) -> str: 
        if len(self.domains.all()) > 0:
            domains = []
            for domain in self.domains.all():
                domains.append(domain.name)
            return "\n".join(domains)
        else:
            return "No phone number"
    
    
    def get_social_medias(self) -> str: 
        if len(self.social_medias.all()) > 0:
            social_medias = []
            for social_media in self.social_medias.all():
                social_medias.append(str(social_media))
            return "\n".join(social_medias)
        else:
            return "No phone number"

    def get_cnpj(self):
        return remove_non_numeric(self.cnpj)

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
            elif len(self.cellphone) == 11 and int(self.cellphone[2]) == 9: 
                return f"({self.cellphone[0:2]}) {self.cellphone[2]} {self.cellphone[3:7]}-{self.cellphone[7:11]}"
            elif len(self.cellphone) == 9 and int(self.cellphone[0]) == 9: 
                return f"{self.cellphone[0]} {self.cellphone[1:5]}-{self.cellphone[5:9]}"
            else: 
                return self.cellphone
        else:
            return None
        
    def ftelephone(self):
        if self.telephone:
            if len(self.telephone) == 12: 
                return f"+{self.telephone[0:2]} ({self.telephone[2:4]}) {self.telephone[4:8]}-{self.telephone[8:12]}"
            elif len(self.telephone) == 10: 
                return f"({self.telephone[0:2]}) {self.telephone[2:6]}-{self.telephone[6:10]}"
            elif len(self.telephone) == 8: 
                return f"{self.telephone[0:4]}-{self.telephone[4:8]}"
            else: 
                return self.telephone
        else:
            return None
    
    def fphone(self):
        phone = self.cellphone or self.telephone
        if phone:
            if len(phone) == 12: 
                return f"+{phone[0:2]} ({phone[2:4]}) {phone[4:8]}-{phone[8:12]}"
            elif len(phone) == 13: 
                return f"+{phone[0:2]} ({phone[2:4]}) {phone[4]} {phone[5:9]}-{phone[9:13]}"
            elif len(phone) == 11 and int(phone[2]) == 9: 
                return f"({phone[0:2]}) {phone[2]} {phone[3:7]}-{phone[7:11]}"
            elif len(phone) == 10: 
                return f"({phone[0:2]}) {phone[2:6]}-{phone[6:10]}"
            elif len(phone) == 9 and int(phone[0]) == 9: 
                return f"{phone[0]} {phone[1:5]}-{phone[5:9]}"
            elif len(phone) == 8: 
                return f"{phone[0:4]}-{phone[4:8]}"
            else: 
                return phone
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
            
        return message
    
    def is_tomorrow_or_later(self) -> bool:
        if self.move_date == None:
            return True
        else:
            return datetime.datetime.now().date() > self.move_date.date()
        
    def get_kanban_url(self):
        return reverse('admin:{}_{}_change'.format(self._meta.app_label, self._meta.model_name + "kanban"), args=[self.pk])

    def title(self):
        website = self.website or self.website2
        if self.name and website:
            return self.name[0:19] if len(self.name) > 20 else self.name
        elif self.name and self.instagram_username:
            return self.name[0:19] if len(self.name) > 20 else self.name
        elif self.instagram_username:
            return f"@{self.instagram_username}"
        elif self.name:
            return self.name[0:19] if len(self.name) > 20 else self.name
        else:
            return None
    
    def get_names(self) -> str:
        names = []
        names.append(self.name or "")
        names.append(self.name2 or "")
        
        return "\n".join(names)
    
    def get_name(self) -> str:
        name = ""
        
        if self.name2:
            name = self.name2
        elif self.name:
            name = self.name
        else:
            name = f"Business {self.id}"
        
        return name
    
    def __str__(self):
        return self.get_name()

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
    observation = models.TextField(max_length=1000, null=True, blank=True)
    business = models.OneToOneField(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name="business_ref")
    
    def offset_date(self):
        return get_time_offset(self.follow_up_date)
    
    def follow_up_color(self):
        now = datetime.datetime.now(timezone('America/Sao_Paulo'))
        
        if self.follow_up_date:
            before_now = now < self.follow_up_date
            until_30min = now < self.follow_up_date + datetime.timedelta(minutes=31)
            until_1hour = now < self.follow_up_date + datetime.timedelta(hours=1)
            after_1hour = now >= self.follow_up_date - datetime.timedelta(hours=1)
            
            if before_now:
                return "yellow"
            elif until_30min:
                return "dark_green"
            elif until_1hour:
                return "lima_green"
            elif after_1hour:
                return "red"
        else:
            return ""
    
    def __str__(self):
        if self.status:
            return f"[{self.id}] {self.status.name}"
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

class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True)

    # http_status = models.PositiveSmallIntegerField(null=True, blank=True)
    connection_status = models.CharField(
        max_length=20,
        choices=[
            ("ok", "OK"),
            ("dns_error", "DNS Error"),
            ("connection_error", "Connection Error"),
            ("timeout", "Timeout"),
            ("ssl_error", "SSL Error"),
        ],
        null=True,
        blank=True,
    )

    last_check = models.DateTimeField(null=True, blank=True)

    is_https = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_banned = models.BooleanField(default=False)

    observation = models.TextField(max_length=1000, null=True, blank=True)

    def get_url(self) -> str:
        protocol = "https" if self.is_https else "http"
        return f"{protocol}://{self.name}"

    def __str__(self):
        return f"{self.get_url()} | {self.get_connection_status_display()}"

class Email(models.Model):
    address = models.EmailField(unique=True)
    last_check = models.DateTimeField(null=True, blank=True)
    is_accounting = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[
            ("unknown", "Unknown"),
            ("valid", "Valid"),
            ("invalid", "Invalid"),
            ("risky", "Risky"),
        ],
        default="unknown"
    )

    def __str__(self):
        return f"{self.address}"

SOCIAL_MEDIA_CATEGORIES = [
    ("1", "instagram"),
    ("2", "facebook"),
    ("3", "linkedin"),
    ("4", "x"),
    ("5", "tiktok"),
]
class SocialMedia(models.Model):
    username = models.CharField(max_length=50)
    category = models.CharField(max_length=1, null=True, blank=True, choices=SOCIAL_MEDIA_CATEGORIES)
    is_active = models.BooleanField(null=True, blank=True)
    observation = models.TextField(max_length=1000, null=True, blank=True)

    class Meta:
        unique_together = ("username", "category")

    def get_url(self) -> str:
        return "https://"
    
    def __str__(self):
        return f"{self.username} [{self.get_category_display()}]"


class PhoneNumber(models.Model):
    # Core fields
    country_code = models.CharField(max_length=5, default="55")   # e.g. "55"
    ddd = models.CharField(max_length=2)            # e.g. "21"
    number = models.CharField(max_length=9)        # e.g. "987654321"

    # WhatsApp
    is_whatsapp_active = models.BooleanField(null=True, blank=True)
    last_whatsapp_check = models.DateTimeField(null=True, blank=True)
    has_whatsapp_photo = models.BooleanField(null=True, blank=True)

    # Metadata
    last_call_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_generated = models.BooleanField(default=False)
    generation_type = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    derived_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="variants"
    )

    observation = models.TextField(max_length=1000, null=True, blank=True)

    class Meta:
        unique_together = ("country_code", "ddd", "number")

    def __setattr__(self, name, value):
        return super().__setattr__(name, value)

    def is_landline(self) -> bool:
        return len(self.number) == 8

    def is_mobile(self) -> bool:
        return len(self.number) == 9
    
    # check if the last 8 digits (landline part) are equal
    # even compare landline and mobile numbers
    def is_landline_part_equal(self, sec_number: str) -> bool:
        if len(sec_number) >= 8:
            return self.number[-8:] == sec_number[-8:]
        else:
            return False

    def get_landline_full_number(self) -> str | None:
        if self.number:
            if self.is_landline():
                if not self.ddd:
                    return self.number
                else:
                    return f"{self.country_code}{self.ddd}{self.number}"
            else:
                if not self.ddd:
                    return self.number[:1]
                else:
                    return f"{self.country_code}{self.ddd}{self.number[:1]}"
        else:
            return None

    def get_full_number(self):
        if not self.ddd:
            return self.number
        else:
            return f"{self.country_code}{self.ddd}{self.number}"

    def fget_full_number(self):
        uf = DDD.get(self.ddd)
        if len(self.number) == 9:
            formatted_number = f"{self.number[0]} {self.number[1:5]}-{self.number[5:9]}"
            return f"{uf} ({self.ddd}) {formatted_number}"
        elif len(self.number) == 8:
            formatted_number = f"{self.number[0:4]}-{self.number[4:8]}"
            return f"{uf} ({self.ddd}) {formatted_number}"
    
    def fget_full_number_whatsapp(self):
        wp_status = ""
        if self.is_whatsapp_active == True:
            wp_status = "🟢"
        elif self.is_whatsapp_active == False:
            wp_status = "🔴"
        elif self.is_whatsapp_active == None:
            wp_status = "⚫"

        return f"{self.fget_full_number()} {wp_status}"
        
    def get_whatsapp_link(self):
        return f"https://web.whatsapp.com/send/?phone={self.get_full_number()}"
        
    def __str__(self):
        return self.fget_full_number_whatsapp()

class VacancyCategory(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = "vacancy category"
        verbose_name_plural = "vacancy categories"
    
    def __str__(self):
        return self.name

class Template(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(max_length=2000, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class Tag(models.Model):
    title = models.CharField(max_length=20)
    
    def __str__(self):
        return self.title
    
class SubTag(models.Model):
    title = models.CharField(max_length=20)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

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
