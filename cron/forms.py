from django import forms
from .models import AsyncCronMail

class AsyncCronMailForm(forms.ModelForm):
    
    class Meta:
        model = AsyncCronMail
        fields = ['subject', 'csvfile', 'sender', 'message']
        widgets = {
                'message': forms.Textarea(attrs={'rows':4, 'cols':40}),
                }
