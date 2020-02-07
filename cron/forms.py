from django import forms
from .models import AsyncCronMail
from ckeditor.widgets import CKEditorWidget

class AsyncCronMailForm(forms.ModelForm):
    
    class Meta:
        model = AsyncCronMail
        fields = ['subject', 'csvfile', 'sender', 'message']
        widgets = {
                'message': CKEditorWidget(),
                }
