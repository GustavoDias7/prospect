from django import forms
from .models import InstagramContact

class InstagramContactForm(forms.ModelForm):
    class Meta:
        model = InstagramContact
        fields = "__all__"
        
    class Media:
        js = ('js/admin/instagram_contacts.js',)