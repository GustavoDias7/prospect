from django import forms
from . import models

class BusinessForm(forms.ModelForm):
    class Meta:
        model = models.Business
        fields = "__all__"
        
    class Media:
        js = ('js/admin/instagram_contacts.js',)
        css = {
            'all': ('css/admin/instagram_contacts.css',)
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