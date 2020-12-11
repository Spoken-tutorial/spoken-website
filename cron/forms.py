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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].widget.attrs.update({'class': 'form-control'})
        self.fields['csvfile'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['sender'].widget.attrs.update({'class': 'form-control', 'value':'no-reply@spoken-tutorial.org'})
        self.fields['message'].widget.attrs.update({'class': 'form-control'})
