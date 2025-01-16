from django.contrib import admin
from django.shortcuts import render
from . import models, actions
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from bs4 import BeautifulSoup
import urllib.parse
from . import models

@admin.register(models.Contact)
class ContactAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ["id", "facebook_page_", "phone_", "email", "website_", "instagram_"]
    actions = [actions.get_datas, actions.disqualify]
    list_filter = ["qualified"]
    
    def import_action(self, request):
        context = {}
        
        if request.method == "GET":
            fb_pages = models.Contact.objects.filter(qualified=None)
            context["fb_pages"] = fb_pages
            
        if request.method == "POST":
            facebook_pages = request.FILES.get("facebook_pages")
            file = facebook_pages.read()
            soup = BeautifulSoup(file, "html.parser")
            links = soup.find_all("a", attrs={"role": "presentation"})
            
            fb_pages = []
            for link in links:
                href = urllib.parse.urlparse(link.get("href"))
                path_query = f'{href.path}?{href.query}' if href.query else href.path
                fb_page = models.Contact(facebook_page=path_query)
                fb_pages.append(fb_page)
                
            print(f"{len(fb_pages)}, contacts found.")
            
            try:
                models.Contact.objects.bulk_create(fb_pages, ignore_conflicts=True)
            except Exception as e:
                print(e)
            
            fb_pages = models.Contact.objects.filter(qualified=None)
            
            print(f"{len(fb_pages)}, contacts inserted.")
            
            context["fb_pages"] = fb_pages
        
        return render(request, "admin/import_contact.html", context)
    
    def get_form(self, request, obj=None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            if obj.name:
                help_text = f"https://duckduckgo.com/?t=ffab&q={obj.name}+site%3Ainstagram.com&ia=web"
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"name": mark_safe(html)})
                
            if obj.facebook_page:
                help_text = obj.get_facebook()
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"facebook_page": mark_safe(html)}) 
            
            if obj.whatsapp:
                help_text = obj.get_whatsapp_link()
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"whatsapp": mark_safe(html)}) 
                
            if obj.instagram:
                help_text = obj.get_instagram_link()
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"instagram": mark_safe(html)}) 
                
            kwargs.update(help_texts)
                
        return super().get_form(request, obj, **kwargs)
    
    @admin.display(description='website')
    def website_(self, obj):
        if obj.website:
            inner_text = obj.website[0:14] if len(obj.website) > 15 else obj.website
            link = obj.get_website()
            html = f'<a href="{link}" target="_blannk">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"
    
    @admin.display(description='instagram')
    def instagram_(self, obj):
        if obj.instagram:
            link = obj.get_instagram_link()
            html = f'<a href="{link}" target="_blannk">{obj.instagram}</a>'
            return mark_safe(html)
        else:
            return "-"
    
    @admin.display(description='phone')
    def phone_(self, obj):
        if obj.whatsapp:
            link_number = obj.get_whatsapp_link()
            whatsapp = f'<a href="{link_number}" target="_blannk">{obj.whatsapp}</a>'
            if len(obj.whatsapp) == 11: 
                return mark_safe(whatsapp)
            else: 
                return obj.whatsapp
        else:
            return "-"
        
    @admin.display(description='facebook page')
    def facebook_page_(self, obj):
        if obj.facebook_page:
            inner_text = obj.name if obj.name else obj.facebook_page
            inner_text = inner_text[0:19] if len(inner_text) > 20 else inner_text
            html = f'<a href="{obj.get_facebook()}" target="_blannk">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"
        

@admin.register(models.Decider)
class DeciderAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "phone", "email", "instagram"]