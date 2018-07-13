# Third Party Stuff
from django import forms
from django.db.models import Count, Q

# Spoken Tutorial Stuff
from creation.models import TutorialResource
from events.models import Testimonials, InductionInterest


class KeywordSearchForm(forms.Form):
    q = forms.CharField(required=True)


class TutorialSearchForm(forms.Form):
    search_foss = forms.ChoiceField(
        choices=[],
        widget=forms.Select(),
        required=False,
    )
    search_language = forms.ChoiceField(
        choices=[],
        widget=forms.Select(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(TutorialSearchForm, self).__init__(*args, **kwargs)
        foss_list_choices = [('', '-- All Courses --'), ]
        lang_list_choices = [('', '-- All Languages --'), ]

        foss_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), language__name='English', tutorial_detail__foss__show_on_homepage=True).values('tutorial_detail__foss__foss').annotate(
            Count('id')).order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()

        for foss_row in foss_list:
            foss_list_choices.append((str(foss_row[0]), str(foss_row[0]) + ' (' + str(foss_row[1]) + ')'))

        lang_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage=True).values('language__name').annotate(
            Count('id')).order_by('language').values_list('language__name', 'id__count').distinct()
        for lang_row in lang_list:
            lang_list_choices.append((str(lang_row[0]), str(lang_row[0]) + ' (' + str(lang_row[1]) + ')'))

        self.fields['search_foss'].choices = foss_list_choices
        self.fields['search_language'].choices = lang_list_choices


class SeriesTutorialSearchForm(forms.Form):
    search_otherfoss = forms.ChoiceField(
        choices=[],
        widget=forms.Select(),
        required=False,
    )
    search_otherlanguage = forms.ChoiceField(
        choices=[],
        widget=forms.Select(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(SeriesTutorialSearchForm, self).__init__(*args, **kwargs)
        foss_list_choices = [('', '-- All Courses --'), ]
        lang_list_choices = [('', '-- All Languages --'), ]

        foss_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), language__name='English', tutorial_detail__foss__show_on_homepage=False).values('tutorial_detail__foss__foss').annotate(
            Count('id')).order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()

        for foss_row in foss_list:
            foss_list_choices.append((str(foss_row[0]), str(foss_row[0]) + ' (' + str(foss_row[1]) + ')'))

        lang_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage=False).values('language__name').annotate(
            Count('id')).order_by('language').values_list('language__name', 'id__count').distinct()
        for lang_row in lang_list:
            lang_list_choices.append((str(lang_row[0]), str(lang_row[0]) + ' (' + str(lang_row[1]) + ')'))

        self.fields['search_otherfoss'].choices = foss_list_choices
        self.fields['search_otherlanguage'].choices = lang_list_choices


class TestimonialsForm(forms.ModelForm):
    source_title = forms.CharField(required=False)
    source_link = forms.CharField(required=False)
    scan_copy = forms.FileField(label='Select a Scaned copy', required=False)
    status = forms.BooleanField(required=False)

    class Meta:
        model = Testimonials
        exclude = ['approved_by', 'user']


class ExpressionForm(forms.ModelForm):
    class Meta:
        model = InductionInterest
        fields = '__all__'
        widgets = {
            'other_comments': forms.Textarea,
            'other_medium': forms.Textarea,
            'other_education': forms.Textarea,
            'other_specialisation': forms.Textarea,
            'other_designation': forms.Textarea,
            'other_language': forms.Textarea,
            'college_address': forms.Textarea,
        }

    def __init__(self, *args, **kwargs):
        super(ExpressionForm, self).__init__(*args, **kwargs)
        self.fields['other_comments'].required = False
        self.fields['other_language'].required = False
        self.fields['other_medium'].required = False
        self.fields['other_education'].required = False
        self.fields['other_specialisation'].required = False
        self.fields['other_designation'].required = False
        self.fields['borrow_laptop'].required = False

    def clean(self):
        cleaned_data = super(ExpressionForm, self).clean()
        try:
            mother_tongue = cleaned_data['mother_tongue']
        except KeyError:
            mother_tongue = ''
        try:
            medium = cleaned_data['medium_of_studies']
        except KeyError:
            medium = ''

        try:
            education = cleaned_data['education']
        except KeyError:
            education = ''

        try:
            specialisation = cleaned_data['specialisation']
        except KeyError:
            specialisation = ''

        try:
            designation = cleaned_data['designation']
        except KeyError:
            designation = ''

        try:
            bring_laptop = cleaned_data['bring_laptop']
        except KeyError:
            bring_laptop = ''

        other_language = cleaned_data['other_language']
        if mother_tongue.lower() == 'other' and not other_language:
            self.add_error('other_language', 'Other mother tongue is required.')

        other_education = cleaned_data['other_education']
        if education.lower() == 'other' and not other_education:
            self.add_error('other_education', 'Other education is required.')

        other_medium = cleaned_data['other_medium']
        if medium.lower() == 'other' and not other_medium:
            self.add_error('other_medium', 'Other medium is required.')

        other_specialisation = cleaned_data['other_specialisation']
        if specialisation.lower() == 'other' and not other_specialisation:
            self.add_error('other_specialisation', 'Other specialisation is required.')

        other_designation = cleaned_data['other_designation']
        if designation.lower() == 'other' and not other_designation:
            self.add_error('other_designation', 'Other designation is required.')

        borrow_laptop = cleaned_data['borrow_laptop']
        if bring_laptop.lower() == 'no' and not borrow_laptop:
            self.add_error('borrow_laptop', 'field is required.')
