from django import forms
from . import models
from django.utils.safestring import mark_safe
    
class BusinessForm(forms.ModelForm):
    class Meta:
        model = models.Business
        fields = "__all__"
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
            "address2": forms.Textarea(attrs={"rows": 2}),
        }
        exclude = ["following",  "cellphone", "telephone", "cep2", "instagram_username", "facebook_username", "website", "email"]
        
    class Media:
        js = ('js/admin/instagram_contacts.js',)
        css = {
            'all': ('css/admin/business.css',)
        }
        
class BusinessContactProxyForm(forms.ModelForm):
    class Meta:
        # model = models.BusinessContactProxy
        fields = "__all__"
        
    # class Media:
    #     js = ('js/admin/instagram_contacts_proxy.js',)
    
class BusinessKanbanForm(forms.ModelForm):
    class Meta:
        model = models.BusinessKanban
        fields = "__all__"
        
    class Media:
        js = ('js/admin/instagram_contacts_kanban.js',)
        
class InteractionForm(forms.ModelForm):
    class Meta:
        model = models.Interaction
        fields = "__all__"
        
    class Media:
        js = ('js/admin/interaction.js',)

class PhoneNumberForm(forms.ModelForm):
    full_number = forms.CharField(max_length=20, required=False, help_text=mark_safe('<a id="full_number_convert" href="/" target="_blank">Convert</a>'))

    class Meta:
        model = models.PhoneNumber
        fields = "__all__"
        
    class Media:
        js = ('js/admin/phone_number.js',)

class DomainForm(forms.ModelForm):
    name = forms.CharField(required=False, help_text=mark_safe('<a id="convert_url_to_domain" href="/" target="_blank">URL to domain</a>'))

    class Meta:
        model = models.Domain
        fields = "__all__"
        
    class Media:
        js = ('js/admin/domain.js',)

class TemplateForm(forms.ModelForm):
    class Meta:
        model = models.Template
        fields = "__all__"
        
    class Media:
        js = ('js/admin/template.js',)
        
class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = models.StaffMember
        fields = "__all__"
        
    class Media:
        js = ('js/admin/decider.js',)