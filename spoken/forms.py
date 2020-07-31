# Third Party Stuff
from builtins import str
from builtins import object
from django import forms
from django.db.models import Count, Q
from django.core.exceptions import ValidationError

# Spoken Tutorial Stuff
from creation.models import TutorialResource, FossCategory
from events.models import Testimonials, InductionInterest, MediaTestimonials


class KeywordSearchForm(forms.Form):
    q = forms.CharField(required=True)


class AllTutorialSearchForm(forms.Form):
    search_foss = forms.ChoiceField(
        choices = [],
        widget=forms.Select(),
        required = False,
        )
    search_language = forms.ChoiceField(
            choices=[],
            widget=forms.Select(),
            required=False,
        ) 

    def __init__(self, *args, **kwargs):
      super(AllTutorialSearchForm, self).__init__(*args, **kwargs)
      foss_list_choices = [('', '-- All Courses --'),]
      lang_list_choices =[('', '-- All Languages --'),]

      foss_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), language__name='English').values('tutorial_detail__foss__foss').annotate(
            Count('id')).order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()
      
      for foss_row in foss_list:
            foss_list_choices.append((str(foss_row[0]), str(foss_row[0]) + ' (' + str(foss_row[1]) + ')'))

      lang_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2)).values('language__name').annotate(
      Count('id')).order_by('language').values_list('language__name', 'id__count').distinct()
      for lang_row in lang_list:
          lang_list_choices.append((str(lang_row[0]), str(lang_row[0]) + ' (' + str(lang_row[1]) + ')'))

      self.fields['search_foss'].choices = foss_list_choices
      self.fields['search_language'].choices = lang_list_choices

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

        foss_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), language__name='English', tutorial_detail__foss__show_on_homepage=1).values('tutorial_detail__foss__foss').annotate(
            Count('id')).order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()

        for foss_row in foss_list:
            foss_list_choices.append((str(foss_row[0]), str(foss_row[0]) + ' (' + str(foss_row[1]) + ')'))

        lang_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage=1).values('language__name').annotate(
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
        type_id = kwargs.pop('type_id', None)
        print(type_id,"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        super(SeriesTutorialSearchForm, self).__init__(*args, **kwargs)
        foss_list_choices = [('', '-- All Courses --'), ]
        lang_list_choices = [('', '-- All Languages --'), ]

        foss_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), language__name='English', tutorial_detail__foss__show_on_homepage=type_id).values('tutorial_detail__foss__foss').annotate(
            Count('id')).order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()

        for foss_row in foss_list:
            foss_list_choices.append((str(foss_row[0]), str(foss_row[0]) + ' (' + str(foss_row[1]) + ')'))

        lang_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage=type_id).values('language__name').annotate(
            Count('id')).order_by('language').values_list('language__name', 'id__count').distinct()
        for lang_row in lang_list:
            lang_list_choices.append((str(lang_row[0]), str(lang_row[0]) + ' (' + str(lang_row[1]) + ')'))

        self.fields['search_otherfoss'].choices = foss_list_choices
        self.fields['search_otherlanguage'].choices = lang_list_choices


class ArchivedTutorialSearchForm(forms.Form):
    search_archivedfoss = forms.ChoiceField(
        choices=[],
        widget=forms.Select(),
        required=False,
    )
    search_archivedlanguage = forms.ChoiceField(
        choices=[],
        widget=forms.Select(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(ArchivedTutorialSearchForm, self).__init__(*args, **kwargs)
        foss_list_choices = [('', '-- All Courses --'), ]
        lang_list_choices = [('', '-- All Languages --'), ]

        foss_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), language__name='English', tutorial_detail__foss__show_on_homepage=2).values('tutorial_detail__foss__foss').annotate(
            Count('id')).order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()

        for foss_row in foss_list:
            foss_list_choices.append((str(foss_row[0]), str(foss_row[0]) + ' (' + str(foss_row[1]) + ')'))

        lang_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage=2).values('language__name').annotate(
            Count('id')).order_by('language').values_list('language__name', 'id__count').distinct()
        for lang_row in lang_list:
            lang_list_choices.append((str(lang_row[0]), str(lang_row[0]) + ' (' + str(lang_row[1]) + ')'))

        self.fields['search_archivedfoss'].choices = foss_list_choices
        self.fields['search_archivedlanguage'].choices = lang_list_choices



class TestimonialsForm(forms.ModelForm):
    source_title = forms.CharField(required=False)
    source_link = forms.CharField(required=False)
    scan_copy = forms.FileField(label='Select a Scaned copy', required=False)
    status = forms.BooleanField(required=False)

    class Meta(object):
        model = Testimonials
        exclude = ['approved_by', 'user']


def file_size(value):
    '''
    Checks if the size is greater than the fixed 
    limit & raises an error if the size is greater. 
    100 MB = 104857600 B
    500 MB = 524288000 B
    50 MB = 52428800 B
    '''
    if value.size > 52428800:
        raise ValidationError('File too large. Size should not exceed 50 MiB.')


class MediaTestimonialForm(forms.Form):
    '''
    Form to take in the values for the media testimonials 
    and save in the MediaTestimonials table.
    '''

    def __init__(self, *args, **kwargs):
        on_home_page = kwargs.pop('on_home_page')
        super(MediaTestimonialForm, self).__init__(*args, **kwargs)
        foss_list_choices = [('', '-- All Courses --'), ]
       
        foss_list = FossCategory.objects.filter(status=1, show_on_homepage=on_home_page).values('foss').annotate(
            Count('id')).order_by('foss').values_list('foss').distinct()

        for foss_row in foss_list:
            foss_list_choices.append((str(foss_row[0]), str(foss_row[0]) ))

        self.fields['foss'].choices = foss_list_choices

        self.fields['foss'].widget.attrs['class'] = 'form-control'
        self.fields['media'].widget.attrs['class'] = 'form-control'
        self.fields['media'].widget.attrs['id'] = 'media_element'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['workshop_details'].widget.attrs['class'] = 'form-control'
        self.fields['content'].widget.attrs['class'] = 'form-control'

    foss = forms.ChoiceField(
        choices=[],
        widget=forms.Select()
    )

    name = forms.CharField(label='Name', required=True)

    workshop_details = forms.CharField(label='Workshop Details (Workshop name, venue, Date | e.g. Spoken Workshop, IIT Bombay, 26 January 2018)', required=True)

    media = forms.FileField(label='File(Select an mp4/mov/mp3 file less than 50MB)', required=True)
    content = forms.CharField(label='Short Description', widget=forms.Textarea, required=True,
                              max_length=500)

    def clean(self):
        if 'media' not in self.cleaned_data:
            raise ValidationError({'media': ['No file or empty file given', ]})
        super(MediaTestimonialForm, self).clean()
        formats = ['mp4', 'mp3', 'mov']
        if self.cleaned_data['media'].name[-3:] not in formats:
            self._errors["media"] = self.error_class(["Not a valid file format."])
        return self.cleaned_data['media']


class MediaTestimonialEditForm(forms.ModelForm):
    class Meta:
        model = MediaTestimonials
        exclude = ['path', 'created']
        widgets = {
            'foss' : forms.Select(attrs={'class': "form-control"}),
            'workshop_details': forms.TextInput(attrs={'class': "form-control"}),
            'content' : forms.Textarea(attrs={'class': "form-control"}),
            'user' : forms.TextInput(attrs={'class': "form-control"}) 
        }
        labels = {
            'user': "Name",
            'workshop_details': "Workshop Details (Workshop name, venue, Date | e.g. Spoken Workshop, IIT Bombay, 26 January 2018)",
            'content': "Short Description"    
        }

class ExpressionForm(forms.ModelForm):
    class Meta(object):
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
