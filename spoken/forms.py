from django import forms
from events.models import Testimonials
class KeywordSearchForm(forms.Form):
    q = forms.CharField(required=True)

class TutorialSearchForm(forms.Form):
    try:
        foss_category = forms.ChoiceField(
            choices = [('', '-- Select Foss --')] + list(FossCategory.objects.all().values_list('id', 'foss')),
            widget=forms.Select(),
            required = False,
        )
        lang_list = list(Language.objects.all().values_list('id', 'name'))
        lang_list.insert(0, ('', '-- Select Language --'))
        language = forms.ChoiceField(
            choices = lang_list,
            widget = forms.Select(),
            required = False,
        )
    except:
        pass

class TestimonialsForm(forms.ModelForm):
    source_title = forms.CharField(required =  False)
    source_link = forms.CharField(required =  False)
    scan_copy = forms.FileField(label = 'Select a Scaned copy', required = False)
    status = forms.BooleanField(required = False)
    class Meta:
        model = Testimonials
        exclude = ['approved_by', 'user']

