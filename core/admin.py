from django.contrib import admin
from django.shortcuts import render
from . import models, actions
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from django.core.exceptions import ObjectDoesNotExist
from bs4 import BeautifulSoup
import urllib.parse
from . import models, forms
from django.template import Context, Template

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


@admin.register(models.BusinessContact)
class BusinessContactAdmin(admin.ModelAdmin):
    list_filter = ["qualified", "contacted", "archived"]
    list_display = ["id", "name_", "cellphone", "telephone", "website_", "website2_", "last_post_", "decider__name"]
    actions = [
        actions.get_instagram_data, 
        actions.disqualify, 
        actions.qualify, 
        actions.contacted, 
        actions.archive,
        actions.has_menu,
        actions.not_menu,
        actions.set_contact_quality,
        actions.send_whatsapp_message,
        actions.open_selenium
    ]
    search_fields = ["id", "username", "website", "cellphone", "decider__name"]
    autocomplete_fields = ["decider", "template"]
    form = forms.BusinessContactForm
    change_form_template = 'admin/vacancy_change_form.html'
    
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        
        try:
            business_contact = models.BusinessContact.objects.get(id=object_id)
            if business_contact.template:
                template = Template(business_contact.template.message)
                context = Context({'business_contact': business_contact})
                rendered_content = template.render(context)
                extra_context["template"] = rendered_content
            else:
                extra_context["template"] = None
        except ObjectDoesNotExist:
            extra_context["template"] = None
        
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )
    
    def get_form(self, request, obj=None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            if obj.name:
                help_text = f"https://duckduckgo.com/?t=ffab&q={obj.name}"
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"name": mark_safe(html)})
            
            if obj.cellphone:
                help_text = obj.get_whatsapp_link(add_message=False)
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"cellphone": mark_safe(html)}) 
                
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
            if "https://" in inner_text: inner_text = inner_text.replace("https://", "")
            html = f'<a href="{obj.website}" target="_blannk">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"
        
    @admin.display(description='website2')
    def website2_(self, obj):
        if obj.website2:
            leng = 30
            inner_text = obj.website2[0:leng - 1] if len(obj.website2) > leng else obj.website2
            if "https://" in inner_text: inner_text = inner_text.replace("https://", "")
            html = f'<a href="{obj.website2}" target="_blannk">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"
        
    @admin.display(description='cellphone')
    def cellphone_(self, obj):
        if obj.cellphone:
            if len(obj.cellphone) == 13: 
                link_number = obj.get_whatsapp_link(add_message=False)
                inner_text = f"+{obj.cellphone[0:2]} ({obj.cellphone[2:4]}) {obj.cellphone[4]} {obj.cellphone[5:9]}-{obj.cellphone[9:13]}"
                whatsapp = f'<a href="{link_number}" target="_blannk">{inner_text}</a>'
                return mark_safe(whatsapp)
            if len(obj.cellphone) == 11 and int(obj.cellphone[2]) == 9: 
                link_number = obj.get_whatsapp_link(add_message=False)
                inner_text = f"({obj.cellphone[0:2]}) {obj.cellphone[2]} {obj.cellphone[3:7]}-{obj.cellphone[7:11]}"
                whatsapp = f'<a href="{link_number}" target="_blannk">{inner_text}</a>'
                return mark_safe(whatsapp)
            elif len(obj.cellphone) == 9 and int(obj.cellphone[0]) == 9: 
                link_number = obj.get_whatsapp_link(add_message=False)
                inner_text = f"{obj.cellphone[0:1]} {obj.cellphone[1:5]}-{obj.cellphone[5:9]}"
                whatsapp = f'<a href="{link_number}" target="_blannk">{inner_text}</a>'
                return mark_safe(whatsapp)
            else: 
                return obj.cellphone
        else:
            return None


class BusinessContactInline(admin.StackedInline):
    model = models.BusinessContact
    form = forms.BusinessContactForm    
    
    def get_formset(self, request, obj=None, **kwargs):
        help_texts = { "help_texts": {} }
        business_contact = self.model.objects.get(decider=obj)
        if business_contact:
            if business_contact.name:
                help_text = f"https://duckduckgo.com/?t=ffab&q={business_contact.name}"
                html = f'<a href="{help_text}" target="_blannk" style="font-size: 12px;">duckduckgo</a>'
                help_texts["help_texts"].update({"name": mark_safe(html)})
            
            if business_contact.cellphone:
                hred = business_contact.get_whatsapp_link(add_message=False)
                help_text = business_contact.fcellphone()
                html = f'<a href="{hred}" target="_blannk" style="font-size: 12px;">{help_text}</a>'
                help_texts["help_texts"].update({"cellphone": mark_safe(html)}) 
                
            if business_contact.username:
                help_text = business_contact.get_instagram_link()
                html = f'<a href="{help_text}" target="_blannk" style="font-size: 12px;">{help_text}</a>'
                help_texts["help_texts"].update({"username": mark_safe(html)}) 
                
            kwargs.update(help_texts)
                
        return super().get_formset(request, obj, **kwargs)
            
  
@admin.register(models.Decider)
class DeciderAdmin(admin.ModelAdmin):
    list_display = ["id", "name_", "phone_", "email", "instagram"]
    search_fields = ["id", "name", "email"]
    form = forms.DeciderForm
    inlines = [BusinessContactInline]
    
    def get_form(self, request, obj=None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            if obj.name:
                help_text1 = f"https://casadosdados.com.br/solucao/cnpj?q={obj.name}"
                html1 = f'<a href="{help_text1}" target="_blannk" style="font-size: 12px;">casadosdados</a>'
                help_text2 = f"https://duckduckgo.com/?t=ffab&q={obj.name}"
                html2 = f'<a href="{help_text2}" target="_blannk" style="font-size: 12px;">duckduckgo</a>'
                html = f"{html1} | {html2}"
                help_texts["help_texts"].update({"name": mark_safe(html)})
            
            if obj.phone:
                href = obj.get_whatsapp_link(add_message=False)
                help_text = obj.fcellphone()
                html = f'<a href="{href}" target="_blannk" style="font-size: 12px;">{help_text}</a>'
                help_texts["help_texts"].update({"phone": mark_safe(html)}) 
                
            if obj.instagram:
                help_text = obj.get_instagram_link()
                html = f'<a href="{help_text}" target="_blannk" style="font-size: 12px;">{help_text}</a>'
                help_texts["help_texts"].update({"instagram": mark_safe(html)}) 
                
            kwargs.update(help_texts)
                
        return super().get_form(request, obj, **kwargs)

    @admin.display(description='name')
    def name_(self, obj):
        if obj.name:
            link = f"https://casadosdados.com.br/solucao/cnpj?q={obj.name}"
            html = f'<a href="{link}" target="_blannk">{obj.name}</a>'
            return mark_safe(html)
        else:
            return None
    
    @admin.display(description='phone')
    def phone_(self, obj):
        if obj.phone:
            if len(obj.phone) == 13 and int(obj.phone[4]) == 9: 
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
    search_fields = ["website"]
    list_display = ["id", "website", "qualified", "whatsapp", "linktree", "bitly", "social_media"]

@admin.register(models.Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_filter = ["archived", "contacted"]
    list_display = ["name", "link", "description", "category", "company"]
    autocomplete_fields = ["category", "company", "template", "curriculum", "level"]
    change_form_template = 'admin/vacancy_change_form.html'
    actions = [actions.archive, actions.contacted, actions.open_selenium]
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        
        try:
            vacancy = models.Vacancy.objects.get(id=object_id)
            if vacancy.template:
                template = Template(vacancy.template.message)
                context = Context({'company': vacancy.company})
                rendered_content = template.render(context)
                extra_context["template"] = rendered_content
            else:
                extra_context["template"] = None
        except ObjectDoesNotExist:
            extra_context["template"] = None
        
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["id", "name_", "linkedin_", "email", "phone"]
    search_fields = ["name"]
    list_filter = ["qualified", "contacted", "archived"]
    autocomplete_fields = ["template", "employer"]
    change_form_template = 'admin/vacancy_change_form.html'
    actions = [actions.qualify, actions.disqualify, actions.archive, actions.get_email_from_link]
    
    def get_form(self, request, obj=None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            if obj.linkedin:
                help_text = obj.linkedin
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"linkedin": mark_safe(html)}) 
            
            if obj.website:
                help_text = obj.website
                html = f'<a href="{help_text}" target="_blannk">{help_text}</a>'
                help_texts["help_texts"].update({"website": mark_safe(html)}) 
                
            kwargs.update(help_texts)
                
        return super().get_form(request, obj, **kwargs)
    
    @admin.display(description='name')
    def name_(self, obj):
        if obj.name:
            length = 30
            inner_text = obj.name[0:length - 1] if len(obj.name) > length else obj.name
            html = f'<a href="{obj.website}" target="_blannk">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"

    @admin.display(description='linkedin')
    def linkedin_(self, obj):
        if obj.linkedin:
            length = 30
            inner_text = obj.linkedin[0:length - 1] if len(obj.linkedin) > length else obj.linkedin
            html = f'<a href="{obj.linkedin}" target="_blannk">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        
        try:
            company = models.Company.objects.get(id=object_id)
            if company.template:
                template = Template(company.template.message)
                context = Context({'company': company})
                rendered_content = template.render(context)
                extra_context["template"] = rendered_content
            else:
                extra_context["template"] = None
        except ObjectDoesNotExist:
            extra_context["template"] = None
        
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

@admin.register(models.VacancyCategory)
class VacancyCategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    
@admin.register(models.Template)
class TemplateAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    form = forms.TemplateForm
    
    
    def get_form(self, request, obj=None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            if obj.message:
                max_length = models.Template._meta.get_field('message').max_length
                help_texts["help_texts"].update({"message": f"Max length: {max_length}"}) 
                
            kwargs.update(help_texts)
                
        return super().get_form(request, obj, **kwargs)
    
@admin.register(models.Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    search_fields = ["name"]

@admin.register(models.VacancyLevel)
class VacancyLevelAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    
@admin.register(models.LinkedInContact)
class LinkedInContactAdmin(admin.ModelAdmin):
    list_display = ["id", "name_"]
    list_filter = ["archived"]
    search_fields = ["username"]
    actions = [actions.get_linkedin_data, actions.archive, actions.open_selenium]
    
    @admin.display(description='linkedin')
    def name_(self, obj):
        if obj.username:
            inner_text = obj.username
            html = f'<a href="{obj.get_linkedin_link()}" target="_blannk">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"