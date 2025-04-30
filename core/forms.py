from django import forms
from . import models

class BusinessContactForm(forms.ModelForm):
    class Meta:
        model = models.BusinessContact
        fields = "__all__"
        
    class Media:
        js = ('js/admin/instagram_contacts.js',)
        
class BusinessContactProxyForm(forms.ModelForm):
    class Meta:
        model = models.BusinessContactProxy
        fields = "__all__"
        
    # class Media:
    #     js = ('js/admin/instagram_contacts_proxy.js',)
    
class BusinessContactKabanForm(forms.ModelForm):
    class Meta:
        model = models.BusinessContactKaban
        fields = "__all__"
        
    # class Media:
    #     js = ('js/admin/instagram_contacts_proxy.js',)
        
class TemplateForm(forms.ModelForm):
    class Meta:
        model = models.Template
        fields = "__all__"
        
    class Media:
        js = ('js/admin/template.js',)
        
class DeciderForm(forms.ModelForm):
    class Meta:
        model = models.Decider
        fields = "__all__"
        
    class Media:
        js = ('js/admin/decider.js',)