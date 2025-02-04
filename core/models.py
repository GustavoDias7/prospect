from django.db import models
from prospect.utils import remove_non_numeric
import datetime
from pytz import timezone

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
    
    def __str__(self):
        if self.name: return self.name
        else: return f"Decider {self.id}"
        
class InstagramContact(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=13, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    qualified = models.BooleanField(default=None, help_text="Account has a website, has been inactive for an extended period, or the page is not found.", null=True, blank=True)
    decider = models.OneToOneField(to="Decider", on_delete=models.SET_NULL, null=True, blank=True)
    contacted = models.BooleanField(default=False)
    last_post = models.DateTimeField(default=None, null=True, blank=True)
    archived = models.BooleanField(default=False)
    menu = models.BooleanField(default=None, null=True, blank=True)
    
    def get_instagram_link(self):
        return f"https://www.instagram.com/{self.username}"
    
    def get_whatsapp_link(self):
        message = "Olá, tudo bem?"
        phone = remove_non_numeric(self.phone)
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
            
        return f"https://web.whatsapp.com/send/?phone={phone}&text={message}&type=phone_number&app_absent=0"
    
    def __str__(self):
        if self.username: return self.username
        else: return f"Instagram {self.id}"
        
class Website(models.Model):
    website = models.CharField(max_length=200, unique=True, null=True, blank=True)
    qualified = models.BooleanField(default=None, null=True, blank=True)
    whatsapp = models.BooleanField(default=False)
    linktree = models.BooleanField(default=False)
    