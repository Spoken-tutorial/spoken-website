from django import forms
from events.models import Testimonials
from creation.models import FossCategory, Language, TutorialResource

class KeywordSearchForm(forms.Form):
    q = forms.CharField(required=True)

class TutorialSearchForm(forms.Form):
    try:
        foss_category = forms.ChoiceField(
            choices = [('', '-- Select Foss --')] + list(TutorialResource.objects.filter(status = 1, language__name = 'English').values_list('tutorial_detail__foss__foss', 'tutorial_detail__foss__foss').order_by('tutorial_detail__foss__foss').distinct()),
            widget=forms.Select(),
            required = False,
        )
        lang_list = list(Language.objects.all().order_by('name').values_list('name','name'))
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

