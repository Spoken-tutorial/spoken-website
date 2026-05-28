# Third Party Stuff
from django import forms
from django.db.models import Q
from django.core.validators import FileExtensionValidator

# Spoken Tutorial Stuff
from creation.models import *


class YoutubeVideoSelectForm(forms.Form):
    foss_category = forms.ChoiceField(
        widget=forms.Select(),
        required=True,
        error_messages={'required': 'FOSS category field is required.'}
    )
    language = forms.ChoiceField(
        choices=[('', 'Select Language'), ],
        widget=forms.Select(attrs={'disabled': 'disabled'}),
        required=True,
        error_messages={'required': 'Language field is required.'}
    )
    tutorial_name = forms.ChoiceField(
        choices=[('', 'Select Tutorial'), ],
        widget=forms.Select(attrs={'disabled': 'disabled'}),
        required=True,
        error_messages={'required': 'Tutorial Name field is required.'}
    )

    def __init__(self, *args, **kwargs):
        super(YoutubeVideoSelectForm, self).__init__(*args, **kwargs)
        foss_list = list(
            FossCategory.objects.filter(
                id__in=TutorialResource.objects.filter(
                    Q(status=1) | Q(status=2),
                    language__name='English',
                    video_id__isnull=False,
                ).values_list('tutorial_detail__foss_id').distinct()
            ).order_by('foss').values_list('id', 'foss')
        )
        foss_list.insert(0, ('', 'Select FOSS category'))
        self.fields['foss_category'] = forms.ChoiceField(
            choices=foss_list,
            error_messages={'required': 'FOSS category field is required.'}
        )

        if args:
            if 'foss_category' in args[0]:
                if args[0]['foss_category'] and args[0]['foss_category'] != '' and args[0]['foss_category'] != 'None':
                    initial_data = ''
                    if 'language' in args[0]:
                        if args[0]['language'] and args[0]['language'] != '' and args[0]['language'] != 'None':
                            initial_data = args[0]['language']
                    choices = list(
                        Language.objects.filter(
                            id__in=TutorialResource.objects.filter(
                                Q(status=1) | Q(status=2),
                                tutorial_detail__foss_id=args[0]['foss_category'],
                                video_id__isnull=False,
                            ).values_list('language_id').distinct()
                        ).order_by('name').values_list('id', 'name')
                    )
                    if len(choices):
                        self.fields['language'].widget.attrs = {}
                    choices.insert(0, ('', 'Select Language'))
                    self.fields['language'].choices = choices
                    if initial_data:
                        self.fields['language'].initial = initial_data
                        lang_rec = Language.objects.get(pk=int(initial_data))
                        tut_init_data = ''
                        if 'tutorial_name' in args[0]:
                            if args[0]['tutorial_name'] and args[0]['tutorial_name'] != '' and args[0]['tutorial_name'] != 'None':
                                tut_init_data = args[0]['tutorial_name']
                        td_list = TutorialDetail.objects.filter(foss_id=args[0]['foss_category']).values_list('id')
                        choices = list(TutorialDetail.objects.filter(
                            id__in=TutorialResource.objects.filter(
                                tutorial_detail_id__in=td_list,
                                language_id=lang_rec.id,
                                status__gte=1,
                                video_id__isnull=False,
                            ).values_list('tutorial_detail_id')
                        ).order_by('level', 'order').values_list('id', 'tutorial'))
                        if len(choices):
                            self.fields['tutorial_name'].widget.attrs = {}
                        choices.insert(0, ('', 'Select Tutorial'))
                        self.fields['tutorial_name'].choices = choices
                        self.fields['tutorial_name'].initial = tut_init_data
                    else:
                        self.fields['tutorial_name'].choices = [('', 'Select Tutorial'), ]
                        self.fields['tutorial_name'].widget.attrs = {'disabled': 'disabled'}


class YouTubeUploadForm(forms.Form):
    """Form for uploading YouTube videos with cascading dropdowns"""
    
    foss_category = forms.ModelChoiceField(
        queryset=FossCategory.objects.all().order_by('foss'),
        empty_label='-- Select FOSS Category --',
        required=True,
        error_messages={'required': 'FOSS category field is required.'},
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    language = forms.ModelChoiceField(
        queryset=Language.objects.all().order_by('name'),
        empty_label='-- Select Language --',
        required=True,
        error_messages={'required': 'Language field is required.'},
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    tutorial = forms.ModelChoiceField(
        queryset=TutorialResource.objects.none(),
        empty_label='-- Select Tutorial --',
        required=True,
        error_messages={'required': 'Tutorial field is required.'},
        widget=forms.Select(attrs={
            'class': 'form-control',
            'disabled': 'disabled'
        })
    )
    
    title = forms.CharField(
        max_length=200,
        required=True,
        error_messages={'required': 'Title field is required.'},
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Auto-generated title'
        })
    )
    
    description = forms.CharField(
        required=True,
        error_messages={'required': 'Description field is required.'},
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Auto-filled from outline',
            'rows': 5
        })
    )
    
    privacy_status = forms.ChoiceField(
        choices=[
            ('public', 'Public'),
            ('unlisted', 'Unlisted'),
            ('private', 'Private'),
        ],
        required=True,
        error_messages={'required': 'Privacy status field is required.'},
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    thumbnail = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/png'
        })
    )
    
    playlist = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.HiddenInput(attrs={
            'id': 'id_playlist_hidden'
        })
    )
    
    playlist_position = forms.IntegerField(
        required=False,
        min_value=0,
        help_text="0 = top. Leave empty to append.",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0'
        })
    )

    def __init__(self, *args, **kwargs):
        super(YouTubeUploadForm, self).__init__(*args, **kwargs)
        if self.data.get('tutorial'):
            self.fields['tutorial'].queryset = TutorialResource.objects.all()
            self.fields['tutorial'].widget.attrs.pop('disabled', None)

