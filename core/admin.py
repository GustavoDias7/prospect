from django.contrib import admin
from django.shortcuts import render
from . import models, actions
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from django.core.exceptions import ObjectDoesNotExist
from bs4 import BeautifulSoup
import urllib.parse
from . import models
from django.template import Context, Template
from django.http import HttpResponseRedirect
from PIL import Image, ImageFont, ImageDraw
import requests
from io import BytesIO
import textwrap
from prospect.utils import resize_image, crop_horizontal_image, text_to_image, group_vertically, center_paste, get_dimentions
import os
from django.conf import settings
import cairosvg
import re
from moviepy.editor import AudioFileClip, ImageClip

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
    list_filter = ["qualified", "contacted", "archived", "followed"]
    list_display = ["id", "instagram", "cellphone_", "telephone", "website_", "website2_", "last_post_", "decider__name"]
    actions = [
        actions.get_instagram_data, 
        actions.disqualify, 
        actions.qualify, 
        actions.contacted, 
        actions.archive,
        actions.open_link,
        actions.set_contact_quality,
        actions.send_whatsapp_message,
        actions.follow_decider
    ]
    search_fields = ["id", "username", "website", "cellphone", "decider__name"]
    autocomplete_fields = ["decider", "template"]
    change_form_template = 'admin/vacancy_change_form.html'
    
    class Media:
        js = ('js/admin/instagram_contacts.js',)
    
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
    def instagram(self, obj):
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
                html1 = f'<a href="{help_text}" target="_blannk" style="font-size: 12px;">Instagram</a>'
                html = " | ".join([html1])
                help_texts["help_texts"].update({"username": mark_safe(html)}) 
                
            kwargs.update(help_texts)
                
        return super().get_formset(request, obj, **kwargs)
            
  
@admin.register(models.Decider)
class DeciderAdmin(admin.ModelAdmin):
    list_display = ["id", "name_", "phone_", "email", "instagram_"]
    search_fields = ["id", "name", "email"]
    list_filter = ["followed"]
    inlines = [BusinessContactInline]
    actions = [actions.follow_decider, actions.open_link]
    
    class Media:
        js = ('js/admin/decider.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            if obj.name:
                help_text1 = f"https://casadosdados.com.br/solucao/cnpj?q={obj.name}"
                html1 = f'<a href="{help_text1}" target="_blannk" style="font-size: 12px;">casadosdados</a>'
                help_text2 = f"https://duckduckgo.com/?t=ffab&q={obj.name}"
                html2 = f'<a href="{help_text2}" target="_blannk" style="font-size: 12px;">duckduckgo</a>'
                html = f"{html1} | {html2} | <a href='/' id='id_name_copy'>Copy name</a>"
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
    
    @admin.display(description='instagram')
    def instagram_(self, obj):
        if obj.instagram:
            link = obj.get_instagram_link()
            html = f'<a href="{link}" target="_blannk">{obj.instagram}</a>'
            return mark_safe(html)
        else:
            return "-"
@admin.register(models.Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_filter = ["qualified"]
    search_fields = ["website"]
    list_display = ["id", "website", "qualified", "whatsapp", "linktree", "bitly", "social_media"]

@admin.register(models.Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_filter = ["archived", "contacted", "category__name"]
    list_display = ["name", "job_view_", "level", "category", "company", "hiring"]
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
        
    @admin.display(description='link')
    def job_view_(self, obj):
        if obj.job_view:
            href = f"https://www.linkedin.com/jobs/view/{obj.job_view}/"
            html = f'<a href="{href}" target="_blannk">Open vacancy</a>'
            return mark_safe(html)
        else:
            return None

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
    
@admin.register(models.VacancyHiring)
class VacancyHiringAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    
@admin.register(models.Template)
class TemplateAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    
    class Media:
        js = ('js/admin/template.js',)
    
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

@admin.register(models.PostType)
class PostTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/admin/hashtag.js',)

@admin.register(models.PostVariant)
class PostVariantAdmin(admin.ModelAdmin):
    change_form_template = 'admin/postvariant_change_form.html'
    class Media:
        js = ('js/admin/post_variant.js',)
        
@admin.register(models.PostAudio)
class PostAudioAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    change_form_template = 'admin/post_change_form.html'
    actions = [actions.not_posted]
    list_display = ["id", "phrase", "posted", "type__name"]
    fieldsets = (
        (None, {
           'fields': ('phrase', 'hashtag', 'posted', 'type')
        }),
        ('Images', {
            'fields': ('variant', 'image1', 'aspect_ratio_image1', 'image2', 'aspect_ratio_image2', 'svg'),
        }),
        ('Font', {
            'fields': ('font_size', 'text_wrap'),
        }),
        ('Media', {
            'fields': ('image', 'width', 'aspect_ratio_image', 'audio', 'video', 'video_duration'),
        }),
    )
    class Media:
        js = ('js/admin/post.js',)
        
    def get_form(self, request, obj=None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            if obj.hashtag:
                help_texts["help_texts"].update({"hashtag": obj.hashtag.content})
                
            kwargs.update(help_texts)
                
        return super().get_form(request, obj, **kwargs)
        
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        
        try:
            post = self.model.objects.get(id=object_id)
            extra_context["post"] = post
        except:
            extra_context["post"] = None
        
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )
        
    def response_change(self, request, obj: models.Post):
        is_preview = bool(request.POST.get("preview"))
        is_image = bool(request.POST.get("generate_image_post"))
        is_video = bool(request.POST.get("generate_video"))
        
        if (is_image or is_preview) and obj:
            req = requests.get(obj.variant.font_family)
            height = get_dimentions(obj.aspect_ratio_image, obj.width)[1]
            
            if bool(obj.image1) and bool(obj.image2) == False:
                img_background = Image.new("RGBA", (obj.width, int(height)), "#ffffff") #3:4 
                draw_background = ImageDraw.Draw(img_background)
                
                if is_preview:
                    loss = int(height) - obj.width
                    draw_background.rectangle(xy=((0, loss/2),(obj.width-1, (obj.width + loss / 2) - 1)), outline="red")
                    
                    height2 = int(get_dimentions("3:4", obj.width)[1])
                    loss2 = int(height) - height2
                    draw_background.rectangle(xy=((0, loss2/2),(obj.width-1, (height2 + loss2/ 2) - 1)), outline="red")
                
                padding = 32
                gap_y = 64
                
                main_text = ""
                for text in request.POST.get("phrase").split('\n'):
                    main_text = main_text + "\n".join(textwrap.wrap(text, width=obj.text_wrap)) + "\n"
                
                main_font = ImageFont.truetype(BytesIO(req.content), size=obj.font_size)
                img_text = text_to_image(
                    draw=draw_background, 
                    text=main_text,
                    fill=f"#222", 
                    font=main_font, 
                    align="left",
                    outline=is_preview
                )
                
                image1 = Image.open(obj.image1)
                aspect_ratio_image1 = obj.aspect_ratio_image1.split(":")
                image1 = crop_horizontal_image(
                    image=image1, 
                    aspect_ratio=(int(aspect_ratio_image1[0]), int(aspect_ratio_image1[1])) , 
                    resize_width=obj.width - padding * 2
                )
                
                grouped_image = group_vertically(images=(img_text, image1,), gap=gap_y)
                center_paste(img_background, grouped_image, x=True, y=True)
            else:
                img_background = Image.new(
                    "RGBA",
                    (obj.width, obj.width),
                    f"#{obj.variant.background_color}"
                )
            
                if bool(obj.image1) and bool(obj.image2):
                    image1 = Image.open(obj.image1)
                    image2 = Image.open(obj.image2)
                    
                    image1 = resize_image(image1, obj.width)
                    image2 = resize_image(image2, obj.width)
                    
                    crop_image = {
                        "left": obj.width / 4,
                        "top": 0,
                        "right": 3 * (obj.width / 4),
                        "bottom": obj.width,
                    }
                    
                    image1 = image1.crop(tuple(crop_image.values()))
                    image2 = image2.crop(tuple(crop_image.values()))
                    
                    overlay_color = "#222222"
                    overlay_img = Image.new("RGBA", (obj.width, obj.width), overlay_color)
                    img_background.paste(image1, (0, 0)) 
                    img_background.paste(image2, (int(obj.width/2), 0))
                    
                    img_background = Image.blend(overlay_img, img_background, alpha=0.3)
                else:
                    if obj.svg == None:
                        obj.svg = models.PostSVG.objects.order_by("?").first()
                    pattern = r'(fill|stroke)="#[A-Fa-f0-9]{6}"'
                    replacement = f"{obj.variant.text_color}"
                    new_svg_template = re.sub(pattern, lambda m: f'{m.group(1)}="#{replacement}"', obj.svg.content)
                    filelike_obj = BytesIO(cairosvg.svg2png(new_svg_template, background_color=f"#{obj.variant.background_color}"))
                    background_template = Image.open(filelike_obj)
                    background_template = resize_image(background_template, obj.width)
                    img_background.paste(background_template, (0, 0))
                
                draw_background = ImageDraw.Draw(img_background)
                
                line_height = 0 # line_height
                
                main_text = "\n".join(textwrap.wrap(obj.phrase, width=obj.text_wrap))
                main_font = ImageFont.truetype(BytesIO(req.content), size=obj.font_size)
                main_text_draw_point = (obj.width/2, obj.width/2) # x / y
                
                draw_background.text(
                    main_text_draw_point, 
                    main_text, 
                    spacing=line_height, 
                    anchor='mm', 
                    fill=f"#{obj.variant.text_color}", 
                    font=main_font, 
                    align="center"
                )
            
            image_name = f'post-{obj.id}.png'
            media_path = f"./media/{image_name}"
            img_background.save(media_path)
            
            # if not is_preview:
            #     try:
            #         if bool(obj.image1):
            #             os.remove(obj.image1.path)
            #             obj.image1 = None
                    
            #         if bool(obj.image2):
            #             os.remove(obj.image2.path)
            #             obj.image2 = None
            #     except OSError as e:
            #         print(e)

            obj.image = image_name
            obj.save()
            return HttpResponseRedirect(".")
        elif is_video and obj:
            audio_clip = AudioFileClip(obj.audio.file.path)
            image_clip = ImageClip(obj.image.path)
            video_clip = image_clip.set_audio(audio_clip)
            if obj.video_duration > 0 and audio_clip.duration > obj.video_duration:
                audio_clip.duration = obj.video_duration
                video_clip.duration = obj.video_duration
            else:
                video_clip.duration = audio_clip.duration
                obj.video_duration = audio_clip.duration
            video_clip.fps = 24
            video_path = os.path.join(settings.BASE_DIR, "media", f"post-{obj.id}.mp4")
            video_clip.write_videofile(video_path)
            obj.video = f"post-{obj.id}.mp4"
            obj.save()
            return HttpResponseRedirect(".")
            
        return super().response_change(request, obj)
        
@admin.register(models.PostGenerator)
class PostGeneratorAdmin(admin.ModelAdmin):
    list_display = ["id"]
    change_form_template = "admin/post_generator_change_form.html"
    
    class Media:
        js = ('js/admin/post.js',)
        
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        
        try:
            post = self.model.objects.get(id=object_id)
            extra_context["post"] = post
        except:
            extra_context["post"] = None
        
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def response_change(self, request, obj):
        if "generate_post" in request.POST and obj and obj.generated != True:
            try:
                phrases = obj.phrases.split(";")
                print(phrases)
                
                for phrase in phrases:
                    if len(phrase) > 0:
                        post = models.Post()
                        post.phrase = phrase
                        post.variant = models.PostVariant.objects.order_by("?").first()
                        post.svg = models.PostSVG.objects.order_by("?").first()
                        post.type = obj.type
                        post.save()
                
                obj.generated = True
                obj.save()
            except ObjectDoesNotExist:
                pass
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

@admin.register(models.PostSVG)
class PostSVGAdmin(admin.ModelAdmin):
    
    class Media:
        js = ('js/admin/post_svg.js',)