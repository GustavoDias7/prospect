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
    
@admin.register(models.InstagramContact)
class InstagramContactAdmin(admin.ModelAdmin):
    list_filter = ["qualified", "contacted", "archived"]
    list_display = ["id", "name_", "phone_", "website_", "last_post_", "decider__name", "menu"]
    actions = [
        actions.get_instagram_data, 
        actions.disqualify, 
        actions.qualify, 
        actions.contacted, 
        actions.archive,
        actions.has_menu,
        actions.not_menu,
        actions.handle_bitly_linktree
    ]
    search_fields = ["id", "username", "website", "phone"]
    
    def get_form(self, request, obj=None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            if obj.name:
                help_text = f"https://duckduckgo.com/?t=ffab&q={obj.name}"
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"name": mark_safe(html)})
            
            if obj.phone:
                help_text = obj.get_whatsapp_link()
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"phone": mark_safe(html)}) 
                
            if obj.username:
                help_text = obj.get_instagram_link()
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"username": mark_safe(html)}) 
                
            kwargs.update(help_texts)
                
        return super().get_form(request, obj, **kwargs)
    
    @admin.display(description='instagram')
    def name_(self, obj):
        if obj.name:
            inner_text = obj.name[0:19] if len(obj.name) > 20 else obj.name
            html = f'<a href="{obj.get_instagram_link()}" target="_blannk">{inner_text}</a>'
            return mark_safe(html)
        elif obj.username:
            inner_text = obj.username
            html = f'<a href="{obj.get_instagram_link()}" target="_blannk">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"
        
    @admin.display(description='last post')
    def last_post_(self, obj):
        if obj.last_post:
            return obj.last_post.strftime("%b. %d, %Y")
        else:
            return "-"

    @admin.display(description='website')
    def website_(self, obj):
        if obj.website:
            leng = 30
            inner_text = obj.website[0:leng - 1] if len(obj.website) > leng else obj.website
            html = f'<a href="{obj.website}" target="_blannk">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"
        
    @admin.display(description='phone')
    def phone_(self, obj):
        if obj.phone:
            if len(obj.phone) == 13: 
                link_number = obj.get_whatsapp_link()
                inner_text = f"+{obj.phone[0:2]} ({obj.phone[2:4]}) {obj.phone[4]} {obj.phone[5:9]}-{obj.phone[9:13]}"
                whatsapp = f'<a href="{link_number}" target="_blannk">{inner_text}</a>'
                return mark_safe(whatsapp)
            if len(obj.phone) == 11 and int(obj.phone[2]) == 9: 
                link_number = obj.get_whatsapp_link()
                inner_text = f"({obj.phone[0:2]}) {obj.phone[2]} {obj.phone[3:7]}-{obj.phone[7:11]}"
                whatsapp = f'<a href="{link_number}" target="_blannk">{inner_text}</a>'
                return mark_safe(whatsapp)
            elif len(obj.phone) == 9 and int(obj.phone[0]) == 9: 
                link_number = obj.get_whatsapp_link()
                inner_text = f"{obj.phone[0:5]}-{obj.phone[5:9]}"
                whatsapp = f'<a href="{link_number}" target="_blannk">{inner_text}</a>'
                return mark_safe(whatsapp)
            else: 
                return obj.phone
        else:
            return "-"
        
@admin.register(models.Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_filter = ["qualified"]
    list_display = ["id", "website", "qualified", "whatsapp", "linktree"]