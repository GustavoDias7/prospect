from django import forms
from . import models

class BusinessContactForm(forms.ModelForm):
    class Meta:
        model = models.Business
        fields = "__all__"
        
    class Media:
        js = ('js/admin/instagram_contacts.js',)
        
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