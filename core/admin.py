from django.contrib import admin, messages
from django.shortcuts import render
from . import models, actions
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from django.core.exceptions import ObjectDoesNotExist
from bs4 import BeautifulSoup
import urllib.parse
from . import models
from . import forms
from django.template import Context, Template
from django.http import HttpResponseRedirect
from PIL import Image, ImageFont, ImageDraw, ImageOps
import requests
from io import BytesIO
import textwrap
from prospect.utils import resize_image, crop_horizontal_image, text_to_image, group_vertically, group_horizontally, center_paste, get_dimentions, has_string_in_list, boldify, rounded_corners, generate_rectangle, audio_normalize
from prospect.regex import WEBSITE_PATTERN
import os
from django.conf import settings
import cairosvg
import re
from moviepy.editor import AudioFileClip, ImageClip
from moviepy.audio.fx import audio_normalize, volumex
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from datetime import datetime
from django.utils import timezone

# data, rate = sf.read("test.wav") # load audio (with shape (samples, channels))
# meter = pyln.Meter(rate) # create BS.1770 meter
# loudness = meter.integrated_loudness(data) # measure loudness
import html
from django.middleware.csrf import get_token

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
                html = f'<a href="{help_text}" target="_blank">{help_text}</a>'
                help_texts["help_texts"].update({"name": mark_safe(html)})
                
            if obj.facebook_page:
                help_text = obj.get_facebook()
                html = f'<a href="{help_text}" target="_blank">{help_text}</a>'
                help_texts["help_texts"].update({"facebook_page": mark_safe(html)}) 
            
            if obj.whatsapp:
                help_text = obj.get_whatsapp_link()
                html = f'<a href="{help_text}" target="_blank">{help_text}</a>'
                help_texts["help_texts"].update({"whatsapp": mark_safe(html)}) 
                
            if obj.instagram:
                help_text = obj.get_instagram_link()
                html = f'<a href="{help_text}" target="_blank">{help_text}</a>'
                help_texts["help_texts"].update({"instagram": mark_safe(html)}) 
                
            kwargs.update(help_texts)
                
        return super().get_form(request, obj, **kwargs)
    
    @admin.display(description='website')
    def website_(self, obj):
        if obj.website:
            inner_text = obj.website[0:14] if len(obj.website) > 15 else obj.website
            link = obj.get_website()
            html = f'<a href="{link}" target="_blank">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"
    
    @admin.display(description='instagram')
    def instagram_(self, obj):
        if obj.instagram:
            link = obj.get_instagram_link()
            html = f'<a href="{link}" target="_blank">{obj.instagram}</a>'
            return mark_safe(html)
        else:
            return "-"
    
    @admin.display(description='phone')
    def phone_(self, obj):
        if obj.whatsapp:
            link_number = obj.get_whatsapp_link()
            whatsapp = f'<a href="{link_number}" target="_blank">{obj.whatsapp}</a>'
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
            html = f'<a href="{obj.get_facebook()}" target="_blank">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"

# class Kanban():
    
    
        
    
@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_filter = ["qualified", "contacted", "archived"]
    list_display = ["id", "instagram", "cellphone_", "telephone", "website_", "website2_", "last_post_"]
    actions = [
        actions.test_chunk,
        actions.get_instagram_data, 
        actions.disqualify, 
        actions.qualify, 
        actions.contacted, 
        actions.archive,
        actions.open_link,
        actions.set_contact_quality,
        actions.check_whatsapp_websites,
        actions.follow,
        actions.open_selenium,
        actions.check_search_engine
    ]
    search_fields = ["id", "instagram_username", "website", "cellphone"]
    autocomplete_fields = ["template", "interaction"]
    change_form_template = 'admin/businesscontact_change_form.html'
    change_list_template = 'admin/businesscontact_change_list.html'
    filter_horizontal = ('staff_members',)
    form = forms.BusinessContactForm
    kanban_layout = False
    kanban_columns = {
        "qualified": {"verbose_name": "qualified", "max_length": None, "filter": "qualified_filter"},
        "follow_up": {"verbose_name": "follow up", "max_length": None, "filter": "follow_up_filter"},
        "no_reply": {"verbose_name": "no reply", "max_length": None, "filter": "no_reply_filter"},
        "maybe_in_the_future": {"verbose_name": "maybe in the future", "max_length": None, "filter": "maybe_in_the_future_filter"},
        "meeting": {"verbose_name": "meeting", "max_length": None, "filter": "meeting_filter"},
        "finish": {"verbose_name": "finish", "max_length": None, "filter": "finish_filter"},
    }
    
    def qualified_filter(self, response):
        qs = response.context_data['cl'].queryset
        qs = qs.filter(qualified=True, archived=False, contacted=False, interaction__isnull=True)
        return qs
    
    def follow_up_filter(self, response):
        qs = response.context_data['cl'].queryset
        qs = qs.filter(qualified=True, archived=False, interaction__isnull=False, interaction__status__name="Follow up")
        qs = qs.order_by('interaction__follow_up_date')
        return qs
    
    def no_reply_filter(self, response):
        qs = response.context_data['cl'].queryset
        qs = qs.filter(qualified=True, archived=False, interaction__isnull=False, interaction__status__name="No reply")
        qs = qs.order_by('interaction__follow_up_date')
        return qs
    
    def maybe_in_the_future_filter(self, response):
        qs = response.context_data['cl'].queryset
        qs = qs.filter(qualified=True, archived=False, interaction__isnull=False, interaction__status__name="Maybe in the future")
        qs = qs.order_by('interaction__follow_up_date')
        return qs
    
    def meeting_filter(self, response):
        qs = response.context_data['cl'].queryset
        qs = qs.filter(qualified=True, archived=False, interaction__isnull=False, interaction__status__name="Meeting")
        return qs
    
    def finish_filter(self, response):
        qs = response.context_data['cl'].queryset
        qs = qs.filter(qualified=True, archived=False, interaction__isnull=False, interaction__status__name="Finish")
        return qs
    
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        response.context_data['kanban_layout'] = self.kanban_layout
        response.context_data['kanban_columns'] = self.kanban_columns
        for category, objects in self.kanban_columns.items():
            filter_name = objects.get("filter")
            filter = getattr(self, filter_name)
            objects["items"] = filter(response)
        return response 
    
    def get_list_filter(self, request):
        if self.kanban_layout:
            return ()
        else:
            return self.list_filter
    
    def response_change(self, request, obj: models.Business):
        is_image = bool(request.POST.get("generate_image"))
        print(is_image)
        
        if is_image and obj:
            dimentions = get_dimentions("9:16", 1280, int)
            img_desktop = Image.new("RGBA", (1280, 3961), "#ffffff")
            loss = 1685
            
            old_primary_color = "#FF0000"
            old_secondary_color = "#0059FF"
            
            svg_template = ""
            if obj.custom_color:
                with open(os.path.join(settings.BASE_DIR, "media", "desktop.svg")) as f:
                    svg_template = f.read()
                svg_template = svg_template.replace(old_primary_color.upper(), obj.custom_color)
                svg_template = svg_template.replace(old_primary_color.lower(), obj.custom_color)
            elif (obj.primary_color and obj.secondary_color) and (obj.primary_color != obj.secondary_color):
                with open(os.path.join(settings.BASE_DIR, "media", "desktop-1.svg")) as f:
                    svg_template = f.read()
                svg_template = svg_template.replace(old_primary_color.upper(), obj.primary_color)
                svg_template = svg_template.replace(old_primary_color.lower(), obj.primary_color)
                svg_template = svg_template.replace(old_secondary_color.upper(), obj.secondary_color)
                svg_template = svg_template.replace(old_secondary_color.lower(), obj.secondary_color)
            elif obj.primary_color or obj.secondary_color:
                with open(os.path.join(settings.BASE_DIR, "media", "desktop.svg")) as f:
                    svg_template = f.read()
                color = obj.primary_color or obj.secondary_color
                svg_template = svg_template.replace(old_primary_color.upper(), obj.primary_color)
                svg_template = svg_template.replace(old_primary_color.lower(), obj.primary_color)
                    
            svg_template = svg_template.replace("Logotype", html.escape(obj.name))
            if obj.cellphone:
                svg_template = svg_template.replace("(21) 4002-8922", html.escape(obj.fcellphone()))
            
            filelike_obj = BytesIO(cairosvg.svg2png(svg_template, background_color="#000"))
            background_template = Image.open(filelike_obj)
            img_desktop.paste(background_template, (0, 0))
            
            frame1 = img_desktop.crop((0, 0, dimentions[0], dimentions[1]))
            frame1_name = f'{obj.id}-frame-1.png'
            frame1.save(os.path.join(settings.BASE_DIR, "media", "business_contact", frame1_name))
            obj.image1 = os.path.join("business_contact", frame1_name)

            frame2 = img_desktop.crop((0, 0+loss, dimentions[0], dimentions[1]+loss))
            frame2_name = f'{obj.id}-frame-2.png'
            frame2.save(os.path.join(settings.BASE_DIR, "media", "business_contact", frame2_name))
            obj.image2 = os.path.join("business_contact", frame2_name)
            
            img_cart = Image.new("RGBA", (360, 810), "#ffffff")
            svg_template = ""
                
            if obj.custom_color:
                with open(os.path.join(settings.BASE_DIR, "media", "cart-2.svg")) as f:
                    svg_template = f.read()
                svg_template = svg_template.replace(old_primary_color.upper(), obj.custom_color)
                svg_template = svg_template.replace(old_primary_color.lower(), obj.custom_color)
            elif obj.primary_color and obj.secondary_color and (obj.primary_color != obj.secondary_color):
                with open(os.path.join(settings.BASE_DIR, "media", "cart-1.svg")) as f:
                    svg_template = f.read()
                svg_template = svg_template.replace(old_primary_color.upper(), obj.primary_color)
                svg_template = svg_template.replace(old_primary_color.lower(), obj.primary_color)
                svg_template = svg_template.replace(old_secondary_color.upper(), obj.secondary_color)
                svg_template = svg_template.replace(old_secondary_color.lower(), obj.secondary_color)
            elif obj.primary_color or obj.secondary_color:
                with open(os.path.join(settings.BASE_DIR, "media", "cart-2.svg")) as f:
                    svg_template = f.read()
                color = obj.primary_color or obj.secondary_color
                svg_template = svg_template.replace(old_primary_color.upper(), obj.primary_color)
                svg_template = svg_template.replace(old_primary_color.lower(), obj.primary_color)
            
            filelike_obj = BytesIO(cairosvg.svg2png(svg_template, background_color="#000"))
            cart_template = Image.open(filelike_obj)
            img_cart.paste(cart_template, (0, 0))
            
            frame3_name = f'{obj.id}-frame-3.png'
            img_cart.save(os.path.join(settings.BASE_DIR, "media", "business_contact", frame3_name))
            obj.image3 = os.path.join("business_contact", frame3_name)
            
            img_order = Image.new("RGBA", (1280, 1490), "#ffffff")
            svg_template = ""
                
            if obj.custom_color:
                with open(os.path.join(settings.BASE_DIR, "media", "order.svg")) as f:
                    svg_template = f.read()
                svg_template = svg_template.replace(old_primary_color.upper(), obj.custom_color)
                svg_template = svg_template.replace(old_primary_color.lower(), obj.custom_color)
            elif obj.primary_color or obj.secondary_color:
                with open(os.path.join(settings.BASE_DIR, "media", "order.svg")) as f:
                    svg_template = f.read()
                svg_template = svg_template.replace(old_primary_color.upper(), obj.primary_color)
                svg_template = svg_template.replace(old_primary_color.lower(), obj.primary_color)
            
            svg_template = svg_template.replace("Logotype", html.escape(obj.name))
            filelike_obj = BytesIO(cairosvg.svg2png(svg_template, background_color="#000"))
            order_template = Image.open(filelike_obj)
            img_order.paste(order_template, (0, 0))
            
            frame4_name = f'{obj.id}-frame-4.png'
            img_order.save(os.path.join(settings.BASE_DIR, "media", "business_contact", frame4_name))
            obj.image4 = os.path.join("business_contact", frame4_name)
            
            obj.save()
            return HttpResponseRedirect(request.get_full_path())
        
        return super().response_change(request, obj)
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        
        try:
            business_contact = models.Business.objects.get(id=object_id)
            extra_context["business_contact"] = business_contact
            if business_contact.template:
                template = Template(boldify(business_contact.template.message, True))
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
    
    def get_form(self, request, obj:models.Business = None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            if obj.name:
                href1 = f"https://casadosdados.com.br/solucao/cnpj?q={obj.name}"
                html1 = f'<a href="{href1}" target="_blank" style="font-size: 12px;">casadosdados</a>'
                href2 = f"https://duckduckgo.com/?t=ffab&q={obj.name}"
                html2 = f'<a href="{href2}" target="_blank" style="font-size: 12px;">duckduckgo</a>'
                html3 = "<a href='/' id='id_name_normalize'>Normalize name</a>"
                html = " | ".join([html1, html2, html3])
                help_texts["help_texts"].update({"name": mark_safe(html)})
            
            if obj.cellphone:
                href1 = obj.get_whatsapp_link(add_message=False)
                html1 = f'<a href="{href1}" style="font-size: 14px;" target="_blank">{obj.fcellphone()}</a>'
                html_ddd = f' - <span style="font-size: 14px;">{obj.get_cellphone_ddd()}</span>'
                html = " | ".join([html1]) + html_ddd
                help_texts["help_texts"].update({"cellphone": mark_safe(html)})
                
            if obj.telephone:
                href1 = obj.get_whatsapp_link(add_message=False)
                html1 = f'<a href="{href1}" style="font-size: 14px;" target="_blank">{obj.ftelephone()}</a>'
                html_ddd = f' - <span style="font-size: 14px;">{obj.get_cellphone_ddd()}</span>'
                html = " | ".join([html1]) + html_ddd
                help_texts["help_texts"].update({"telephone": mark_safe(html)})
                
            if obj.instagram_username:
                href1 = obj.get_instagram_link()
                html1 = f'<a href="{href1}" target="_blank">Instagram</a>'
                href2 = f"https://ig.me/m/{obj.instagram_username}"
                html2 = f'<a href="{href2}" target="_blank">Instagram DM</a>'
                href3 = f"https://duckduckgo.com/?t=ffab&q={obj.instagram_username}"
                html3 = f'<a href="{href3}" target="_blank" style="font-size: 12px;">duckduckgo</a>'
                html = " | ".join([html1, html2, html3])
                help_texts["help_texts"].update({"instagram_username": mark_safe(html)}) 
                
            kwargs.update(help_texts)
                
        return super().get_form(request, obj, **kwargs)
    
    @admin.display(description='instagram')
    def instagram(self, obj: models.Business):
        if obj.name:
            inner_text = obj.name[0:19] if len(obj.name) > 20 else obj.name
            html = f'<a href="{obj.get_instagram_link()}" target="_blank">{inner_text}</a>'
            return mark_safe(html)
        elif obj.instagram_username:
            inner_text = obj.instagram_username
            html = f'<a href="{obj.get_instagram_link()}" target="_blank">{inner_text}</a>'
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
            html = f'<a href="{obj.website}" target="_blank">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"
        
    @admin.display(description='website2')
    def website2_(self, obj):
        if obj.website2:
            leng = 30
            inner_text = obj.website2[0:leng - 1] if len(obj.website2) > leng else obj.website2
            if "https://" in inner_text: inner_text = inner_text.replace("https://", "")
            html = f'<a href="{obj.website2}" target="_blank">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"
        
    @admin.display(description='cellphone')
    def cellphone_(self, obj):
        if obj.cellphone:
            if len(obj.cellphone) == 13: 
                link_number = obj.get_whatsapp_link(add_message=False)
                inner_text = f"+{obj.cellphone[0:2]} ({obj.cellphone[2:4]}) {obj.cellphone[4]} {obj.cellphone[5:9]}-{obj.cellphone[9:13]}"
                whatsapp = f'<a href="{link_number}" target="_blank"  style="font-size: 14px;">{inner_text}</a>'
                return mark_safe(whatsapp)
            if len(obj.cellphone) == 11 and int(obj.cellphone[2]) == 9: 
                link_number = obj.get_whatsapp_link(add_message=False)
                inner_text = f"({obj.cellphone[0:2]}) {obj.cellphone[2]} {obj.cellphone[3:7]}-{obj.cellphone[7:11]}"
                whatsapp = f'<a href="{link_number}" target="_blank"  style="font-size: 14px;">{inner_text}</a>'
                return mark_safe(whatsapp)
            elif len(obj.cellphone) == 9 and int(obj.cellphone[0]) == 9: 
                link_number = obj.get_whatsapp_link(add_message=False)
                inner_text = f"{obj.cellphone[0:1]} {obj.cellphone[1:5]}-{obj.cellphone[5:9]}"
                whatsapp = f'<a href="{link_number}" target="_blank"  style="font-size: 14px;">{inner_text}</a>'
                return mark_safe(whatsapp)
            else: 
                return obj.cellphone
        else:
            return None

    
@admin.register(models.BusinessKanban)
class BusinessKanbanAdmin(BusinessAdmin):
    list_filter = []
    kanban_layout = True
    

class BusinessInline(admin.StackedInline):
    model = models.Business
    extra = 0
    
    def get_formset(self, request, obj:models.StaffMember=None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            try:
                business = self.model.objects.get(staff_member=obj)
            except Exception as e:
                business = None
                print(e)
            if business:
                if business.name:
                    help_text1 = f"https://casadosdados.com.br/solucao/cnpj?q={business.name}"
                    html1 = f'<a href="{help_text1}" target="_blank" style="font-size: 12px;">casadosdados</a>'
                    help_text2 = f"https://duckduckgo.com/?t=ffab&q={business.name}"
                    html2 = f'<a href="{help_text2}" target="_blank" style="font-size: 12px;">duckduckgo</a>'
                    html3 = "<a href='/' id='id_name_copy_business'>Copy name</a>"
                    html = f" | ".join([html1, html2, html3])
                    help_texts["help_texts"].update({"name": mark_safe(html)})
                    
                if business.cellphone:
                    href1 = business.get_whatsapp_link(add_message=False)
                    html1 = f'<a href="{href1}" style="font-size: 14px;" target="_blank">{business.fcellphone()}</a>'
                    html_ddd = f'<span style="font-size: 14px;">{business.get_cellphone_ddd()}</span>'
                    html = " | ".join([html1, html_ddd])
                    help_texts["help_texts"].update({"cellphone": mark_safe(html)}) 
                    
                if business.instagram_username:
                    help_text = business.get_instagram_link()
                    html1 = f'<a href="{help_text}" target="_blank" style="font-size: 12px;">Instagram</a>'
                    html = " | ".join([html1])
                    help_texts["help_texts"].update({"instagram_username": mark_safe(html)}) 
                    
                kwargs.update(help_texts)
                
        return super().get_formset(request, obj, **kwargs)
            
class QualifiedListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "qualified"

    # Parameter for the filter that will be used in the URL query.
    # parameter_name = "decade"
    parameter_name = "qualified"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return [
            ("none", "Unknown"),
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes" or self.value() == "no":
            business_contact = models.Business.objects.filter(
                qualified=self.value() == "yes"
            ).values_list("decider__id", flat=True)
            return queryset.filter(id__in=business_contact)
        elif self.value() == "none":
            business_contact = models.Business.objects.filter(
                qualified=None
            ).values_list("decider__id", flat=True)
            return queryset.filter(id__in=business_contact)
        else:
            return queryset.all()
        
@admin.register(models.StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ["id", "name_", "phone_", "email", "instagram_", "contacted"]
    search_fields = ["id", "name", "email"]
    list_filter = ["contacted", QualifiedListFilter]
    actions = [actions.follow, actions.open_link, actions.copy_name, actions.contacted, actions.qualify]
    change_form_template = 'admin/decider.html'
    form = forms.StaffMemberForm
    
    def get_form(self, request, obj:models.StaffMember=None, **kwargs):
        help_texts = { "help_texts": {} }
        if obj:
            if obj.name:
                href1 = f"https://casadosdados.com.br/solucao/cnpj?q={obj.name}"
                html1 = f'<a href="{href1}" target="_blank">casadosdados</a>'
                href2 = f"https://duckduckgo.com/?t=ffab&q={obj.name}"
                html2 = f'<a href="{href2}" target="_blank">duckduckgo</a>'
                html3 = "<a href='/' id='id_name_copy'>Copy name</a>"
                html4 = "<a href='/' id='id_name_greeting'>Get greeting</a>"
                html5 = "<a href='/' id='id_name_normalize'>Normalize name</a>"
                html = " | ".join([html1, html2, html3, html4, html5])
                help_texts["help_texts"].update({"name": mark_safe(html)})
                
            if obj.cnpj:
                href1 = f"https://casadosdados.com.br/solucao/cnpj?q={obj.cnpj}"
                html1 = f'<a href="{href1}" target="_blank">casadosdados</a>'
                href2 = f"https://duckduckgo.com/?t=ffab&q={obj.cnpj}"
                html2 = f'<a href="{href2}" target="_blank">duckduckgo</a>'
                html = " | ".join([html1, html2])
                help_texts["help_texts"].update({"cnpj": mark_safe(html)})
                
            if obj.phone:
                href1 = obj.get_whatsapp_link(add_message=False)
                html1 = obj.fcellphone()
                if len(obj.phone) == 13:
                    html1 = f'<a href="{href1}" style="font-size: 14px;" target="_blank">{obj.fcellphone()}</a>'
                html_ddd = f'<span style="font-size: 14px;">{obj.get_cellphone_ddd()}</span>'
                html = " | ".join([html1, html_ddd])
                help_texts["help_texts"].update({"phone": mark_safe(html)})
                    
            if obj.email:
                html1 = "<a href='/' id='id_email_copy_business'>Copy e-mail</a>"
                html2 = "<a href='/' id='id_email_normalize'>Lower case</a>"
                html = f" | ".join([html1, html2])
                help_texts["help_texts"].update({"email": mark_safe(html)})
            
            if obj.instagram:
                help_text = obj.get_instagram_link()
                html = f'<a href="{help_text}" target="_blank" style="font-size: 12px;">Instagram</a>'
                help_texts["help_texts"].update({"instagram": mark_safe(html)}) 
                
        else:
            html5 = "<a href='/' id='id_name_normalize'>Normalize name</a>"
            html = " | ".join([html5])
            help_texts["help_texts"].update({"name": mark_safe(html)})
        
        kwargs.update(help_texts)
            
        return super().get_form(request, obj, **kwargs)
    
    def response_change(self, request, obj: models.StaffMember):
        is_image = bool(request.POST.get("generate_image"))
        try:
            business_contact = models.Business.objects.filter(decider__id=obj.id)[0]
        except:
            business_contact = None
        
        if is_image and obj:
            dimentions = get_dimentions("9:16", 1280, int)
            img_desktop = Image.new("RGBA", (1280, 3961), "#ffffff")
            loss = 1685
            
            svg_template = ""
            with open(os.path.join(settings.BASE_DIR, "media", "desktop.svg")) as f:
                svg_template = f.read()
                svg_template = svg_template.replace("#00C950", business_contact.color)
                svg_template = svg_template.replace("Logotype", html.escape(business_contact.name))
                
            filelike_obj = BytesIO(cairosvg.svg2png(svg_template, background_color="#000"))
            background_template = Image.open(filelike_obj)
            img_desktop.paste(background_template, (0, 0))
            
            frame1 = img_desktop.crop((0, 0, dimentions[0], dimentions[1]))
            frame1_name = f'{business_contact.id}-frame-1.png'
            frame1.save(os.path.join(settings.BASE_DIR, "media", "business_contact", frame1_name))
            business_contact.image1 = os.path.join("business_contact", frame1_name)

            frame2 = img_desktop.crop((0, 0+loss, dimentions[0], dimentions[1]+loss))
            frame2_name = f'{business_contact.id}-frame-2.png'
            frame2.save(os.path.join(settings.BASE_DIR, "media", "business_contact", frame2_name))
            business_contact.image2 = os.path.join("business_contact", frame2_name)

            img_cart = Image.new("RGBA", (360, 810), "#ffffff")
            svg_template = ""
            with open(os.path.join(settings.BASE_DIR, "media", "mobile.svg")) as f:
                svg_template = f.read()
                svg_template = svg_template.replace("#00C950", business_contact.color)
            
            filelike_obj = BytesIO(cairosvg.svg2png(svg_template, background_color="#000"))
            cart_template = Image.open(filelike_obj)
            img_cart.paste(cart_template, (0, 0))
            
            frame3_name = f'{business_contact.id}-frame-3.png'
            img_cart.save(os.path.join(settings.BASE_DIR, "media", "business_contact", frame3_name))
            business_contact.image3 = os.path.join("business_contact", frame3_name)
            
            business_contact.save()
            return HttpResponseRedirect(".")
        
        return super().response_change(request, obj)
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        
        try:
            business_contact = models.Business.objects.get(staffmember__id=object_id)
            extra_context["business_contact"] = business_contact
            if business_contact.template:
                template = Template(business_contact.template.message)
                context = Context({'business_contact': business_contact})
                rendered_content = template.render(context)
                extra_context["template"] = rendered_content
            else:
                extra_context["template"] = None
        except:
            extra_context["template"] = None
        
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    @admin.display(description='name')
    def name_(self, obj):
        if obj.name:
            link = f"https://casadosdados.com.br/solucao/cnpj?q={obj.name}"
            html = f'<a href="{link}" target="_blank">{obj.name}</a>'
            return mark_safe(html)
        else:
            return None
    
    @admin.display(description='phone')
    def phone_(self, obj):
        if obj.phone:
            href1 = obj.get_whatsapp_link(add_message=False)
            html1 = obj.fcellphone()
            if len(obj.phone) == 13:
                html1 = f'<a href="{href1}" style="font-size: 14px;" target="_blank">{obj.fcellphone()}</a>'
            html = " | ".join([html1])
            return mark_safe(html)
        else:
            return "-"
    
    @admin.display(description='instagram')
    def instagram_(self, obj):
        if obj.instagram:
            link = obj.get_instagram_link()
            html = f'<a href="{link}" target="_blank">{obj.instagram}</a>'
            return mark_safe(html)
        else:
            return "-"
    

@admin.register(models.StaffMemberType)
class StaffMemberTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Interaction)
class InteractionAdmin(admin.ModelAdmin):
    form = forms.InteractionForm
    search_fields = ["name"]
@admin.register(models.InteractionStatus)
class InteractionStatusAdmin(admin.ModelAdmin):
    pass

@admin.register(models.InteractionContactVia)
class InteractionContactViaAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_filter = ["qualified"]
    search_fields = ["website"]
    list_display = ["id", "website", "qualified", "whatsapp", "linktree", "bitly", "social_media", "ignore"]
    actions = [actions.ignore_website]

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
            html = f'<a href="{href}" target="_blank">Open vacancy</a>'
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
                html = f'<a href="{help_text}" target="_blank">{help_text}</a>'
                help_texts["help_texts"].update({"linkedin": mark_safe(html)}) 
            
            if obj.website:
                help_text = obj.website
                html = f'<a href="{help_text}" target="_blank">{help_text}</a>'
                help_texts["help_texts"].update({"website": mark_safe(html)}) 
                
            kwargs.update(help_texts)
                
        return super().get_form(request, obj, **kwargs)
    
    @admin.display(description='name')
    def name_(self, obj):
        if obj.name:
            length = 30
            inner_text = obj.name[0:length - 1] if len(obj.name) > length else obj.name
            html = f'<a href="{obj.website}" target="_blank">{inner_text}</a>'
            return mark_safe(html)
        else:
            return "-"

    @admin.display(description='linkedin')
    def linkedin_(self, obj):
        if obj.linkedin:
            length = 30
            inner_text = obj.linkedin[0:length - 1] if len(obj.linkedin) > length else obj.linkedin
            html = f'<a href="{obj.linkedin}" target="_blank">{inner_text}</a>'
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
    change_form_template = 'admin/template_change_form.html'
    
    class Media:
        js = ('js/admin/template.js',)
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        
        try:
            business_contact = models.Business.objects.get(id=3756)
            template = models.Template.objects.get(id=object_id)
            extra_context["business_contact"] = business_contact
            if template:
                tpt = Template(boldify(template.message, True))
                context = Context({'business_contact': business_contact})
                rendered_content = tpt.render(context)
                extra_context["template"] = rendered_content
            else:
                extra_context["template"] = None
        except Exception as e:
            print(e)
            extra_context["template"] = None
        
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )
    
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
            html = f'<a href="{obj.get_linkedin_link()}" target="_blank">{inner_text}</a>'
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
    actions = [actions.upload_post, actions.not_posted]
    list_display = ["id", "phrase", "posted", "type__name"]
    fieldsets = (
        (None, {
           'fields': ('phrase', 'hashtag', 'posted', 'type')
        }),
        ('Images', {
            'fields': ('variant', 'image1', 'aspect_ratio_image1', 'image1_url', 'image2', 'aspect_ratio_image2', 'svg'),
        }),
        ('Font', {
            'fields': ('font_size', 'text_wrap'),
        }),
        ('Media', {
            'fields': ('image', 'width', 'aspect_ratio_image', 'audio', 'audio_url', 'video', 'video_duration'),
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
        
    def save_model(self, request, obj: models.Post, form, change):
        # if obj.image1 == None and obj.image1_url:
        if obj.image1_url:
            img_res = requests.get(obj.image1_url)
            if img_res.ok:
                image_res_name = re.search(r'([^/?#]+)(?=\?|\#|$)', obj.image1_url).group(0)
                image_res_path = os.path.join(settings.BASE_DIR, "media", image_res_name)
                with open(image_res_path, 'wb') as handler:
                    handler.write(img_res.content)
                    obj.image1 = image_res_name
                image1 = Image.open(image_res_path)
                aspect_ratio_image1 = obj.aspect_ratio_image1.split(":")
                image1 = crop_horizontal_image(
                    image=image1, 
                    aspect_ratio=(int(aspect_ratio_image1[0]), int(aspect_ratio_image1[1])) , 
                    resize_width=obj.width
                )
                image1.save(image_res_path)
           
        
        
        super().save_model(request, obj, form, change)
        
    def response_change(self, request, obj: models.Post):
        is_preview = bool(request.POST.get("preview"))
        is_image = bool(request.POST.get("generate_image_post"))
        is_video = bool(request.POST.get("generate_video"))
        
        if (is_image or is_preview) and bool(obj):
            req = requests.get(obj.variant.font_family)
            height = get_dimentions(obj.aspect_ratio_image, obj.width)[1]
            
            if bool(obj.image1) == False and bool(obj.image1_url):
                image1_filename = re.search(r'([^/?#]+)(?=\?|\#|$)', obj.image1_url).group(0)
                image1_path = os.path.join(settings.BASE_DIR, "media", image1_filename)
                image1_response = requests.get(obj.image1_url, stream=True)
                if image1_response.ok:
                    with open(image1_path, 'wb') as handler:
                        handler.write(image1_response.content)
            
            if bool(obj.image1) and bool(obj.image2) == False:
                img_background = Image.new("RGBA", (obj.width, int(height)), "#fefefe")
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
                    main_text = main_text + text + "\n"
                
                main_font = ImageFont.truetype(BytesIO(req.content), size=obj.font_size)
                img_text = text_to_image(
                    draw=draw_background, 
                    text=main_text,
                    width=obj.width - padding * 4,
                    fill=f"#222", 
                    font=main_font, 
                    align="left",
                    outline=is_preview
                )
                
                print("text max width:", obj.width - padding * 4)
                print("img_text:", img_text.size)
                
                image1 = Image.open(obj.image1)
                aspect_ratio_image1 = obj.aspect_ratio_image1.split(":")
                image1 = crop_horizontal_image(
                    image=image1, 
                    aspect_ratio=(int(aspect_ratio_image1[0]), int(aspect_ratio_image1[1])) , 
                    resize_width=obj.width - padding * 4
                )
                image1 = rounded_corners(image1, 16)
                
                group1 = group_vertically(
                    images=(img_text, image1), 
                    gap=int(gap_y / 2),
                    align="left"
                )
                
                group1_width, group1_height = group1.size
                square_size = (group1_width + padding * 2, group1_height + padding * 2)
                
                img_square = generate_rectangle(
                    size=square_size,
                    border_width=2,
                    border_color="#404040",
                    fill_color="#f5f5f5",
                    border_radius=16,
                )
                
                img_square.paste(group1, (padding, padding), group1)
                
                sc_font = ImageFont.truetype(BytesIO(req.content), size=48)
                top_message = text_to_image(
                    draw=draw_background, 
                    text="NetDelivery | Criação de Sites",
                    width=obj.width - padding * 2,
                    fill=f"#222", 
                    font=sc_font, 
                    align="left",
                    outline=is_preview
                )
                
                tt_font = ImageFont.truetype(BytesIO(req.content), size=40)
                username = text_to_image(
                    draw=draw_background, 
                    text="@web.netdelivery",
                    width=obj.width - padding * 2,
                    fill=f"#222", 
                    font=tt_font, 
                    align="left",
                    outline=is_preview
                )
                
                icon_svg = None
                icon_img = None
                with open(os.path.join(settings.BASE_DIR, "media", "icon.svg")) as f:
                    icon_svg = f.read()
                
                if icon_svg:
                    icon_obj = BytesIO(cairosvg.svg2png(icon_svg))
                    icon_img = Image.open(icon_obj)
                
                group2 = group_vertically(
                    images=(top_message, username), 
                    gap=0,
                    align="left"
                )
                
                group3 = group_horizontally(
                    images=(icon_img, group2), 
                    gap=24,
                    align="center"
                )
                
                group4 = group_vertically(
                    images=(group3, img_square), 
                    gap=gap_y-8,
                    align="left"
                )
                center_paste(img_background, group4, x=True, y=True)
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
            audio_clip = None
            
            if obj.audio:
                audio_clip = AudioFileClip(obj.audio.file.path)
                audio_clip = audio_normalize.audio_normalize(audio_clip)
                audio_clip = volumex.volumex(audio_clip, 0.05)
            elif obj.audio_url:
                audio_res = requests.get(obj.audio_url)
                if audio_res.ok:
                    audio_res_name = re.search(r'([^/?#]+)(?=\?|\#|$)', obj.audio_url).group(0)
                    audio_res_path = os.path.join(settings.BASE_DIR, "media", audio_res_name)
                    with open(audio_res_path, 'wb') as handler:
                        handler.write(audio_res.content)
                audio_clip = AudioFileClip(audio_res_path)
                audio_clip = audio_normalize.audio_normalize(audio_clip)
                audio_clip = volumex.volumex(audio_clip, 0.05)
            
            image_clip = ImageClip(obj.image.path)
            video_clip = image_clip.set_audio(audio_clip) if audio_clip else image_clip
            if obj.video_duration > 0 and audio_clip.duration > obj.video_duration:
                audio_clip.duration = obj.video_duration
                video_clip.duration = obj.video_duration
            else:
                video_clip.duration = audio_clip.duration
                obj.video_duration = audio_clip.duration
            video_clip.fps = 24
            video_path = os.path.join(settings.BASE_DIR, "media", f"post-{obj.id}.mp4")
            video_clip.write_videofile(video_path)
            # video_clip = VideoFileClip(video_clip).with_effects([afx.AudioNormalize()])
            # video_clip = normalize_audio(video_path)
            obj.video = f"post-{obj.id}.mp4"
            obj.save()
            return HttpResponseRedirect(".")
            
        return super().response_change(request, obj)
        
@admin.register(models.PostGenerator)
class PostGeneratorAdmin(admin.ModelAdmin):
    list_display = ["id", "generated"]
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
                phrases = obj.phrases.split("***")
                
                for phrase in phrases:
                    if len(phrase) > 0:
                        post = models.Post()
                        post.phrase = phrase.strip()
                        
                        url_matches = re.findall("(?P<url>https?://[^\s]+)", post.phrase)
                        for url in url_matches:
                            image_extensions = [".jpg", ".jpeg", ".png", ".webp"]
                            is_url_image = has_string_in_list(image_extensions, [url])
                            if is_url_image: post.image1_url = url
                            
                            audio_extensions = [".mp3"]
                            is_url_audio = has_string_in_list(audio_extensions, [url])
                            if is_url_audio: post.audio_url = url
                            
                            post.phrase = post.phrase.replace(url, "").strip()
                        
                        post.variant = models.PostVariant.objects.order_by("?").first()
                        post.svg = models.PostSVG.objects.order_by("?").first()
                        post.type = obj.type
                        post.hashtag = obj.hashtag
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