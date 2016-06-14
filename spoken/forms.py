# Third Party Stuff
from django import forms
from django.db.models import Q, Count

# Spoken Tutorial Stuff
from creation.models import TutorialResource
from events.models import Testimonials


class KeywordSearchForm(forms.Form):
    q = forms.CharField(required=True)


class TutorialSearchForm(forms.Form):
    try:
        foss_list = TutorialResource.objects.filter(
            Q(status=1) | Q(status=2),
            language__name='English').values('tutorial_detail__foss__foss').annotate(Count('id')).order_by(
            'tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()
        choices = [('', '-- All Courses --'), ]
        for foss_row in foss_list:
            choices.append((str(foss_row[0]), str(foss_row[0]) + ' (' + str(foss_row[1]) + ')'))
        search_foss = forms.ChoiceField(
            choices=choices,
            widget=forms.Select(),
            required=False,
        )
        lang_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2)).values('language__name').annotate(
            Count('id')).order_by('language').values_list('language__name', 'id__count').distinct()
        choices = [('', '-- All Languages --'), ]
        for lang_row in lang_list:
            choices.append((str(lang_row[0]), str(lang_row[0]) + ' (' + str(lang_row[1]) + ')'))
        search_language = forms.ChoiceField(
            choices=choices,
            widget=forms.Select(),
            required=False,
        )
    except:
        pass


class TestimonialsForm(forms.ModelForm):
    source_title = forms.CharField(required=False)
    source_link = forms.CharField(required=False)
    scan_copy = forms.FileField(label='Select a Scaned copy', required=False)
    status = forms.BooleanField(required=False)

    class Meta:
        model = Testimonials
        exclude = ['approved_by', 'user']
