
# Third Party Stuff
from builtins import str
from builtins import range
from builtins import object
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

# Spoken Tutorial Stuff
from creation.models import *


class FossAvailableForTestForm(forms.ModelForm):
    foss = forms.ModelChoiceField(queryset=FossCategory.objects.filter(status=True).order_by('foss'))

    class Meta(object):
        model = FossAvailableForTest
        exclude = ['created']


class UploadPrerequisiteForm(forms.Form):
    foss_category = forms.ChoiceField(
        choices = [('', 'Select FOSS Category'),],
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    tutorial_name = forms.ChoiceField(
        choices = [('', 'Select Tutorial'),],
        widget=forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Tutorial Name field is required.'}
    )

    def __init__(self, user, *args, **kwargs):
        super(UploadPrerequisiteForm, self).__init__(*args, **kwargs)
        foss_list = list(
            FossCategory.objects.filter(
                id__in = TutorialResource.objects.filter(
                    language__name = 'English'
                ).values_list('tutorial_detail__foss_id').distinct()
            ).order_by('foss').values_list('id', 'foss')
        )
        foss_list.insert(0, ('', 'Select FOSS Category'))
        self.fields['foss_category'].choices = foss_list

        if args:
            if 'foss_category' in args[0]:
                if args[0]['foss_category'] and args[0]['foss_category'] != '' and args[0]['foss_category'] != 'None':
                    initial_data = ''
                    if 'tutorial_name' in args[0]:
                        if args[0]['tutorial_name'] and args[0]['tutorial_name'] != '' and args[0]['tutorial_name'] != 'None':
                            initial_data = args[0]['tutorial_name']
                    td_list = TutorialDetail.objects.filter(foss_id = args[0]['foss_category']).values_list('id')
                    lang_rec = Language.objects.get(name = 'English')
                    choices = list(
                        TutorialDetail.objects.filter(
                            id__in = TutorialResource.objects.filter(
                                tutorial_detail_id__in = td_list,
                                language_id = lang_rec.id,
                            ).values_list(
                                'tutorial_detail_id'
                            )
                        ).values_list(
                            'id',
                            'tutorial'
                        )
                    )
                    choices.insert(0, ('', 'Select Tutorial'))
                    self.fields['tutorial_name'].choices = choices
                    self.fields['tutorial_name'].widget.attrs = {}
                    self.fields['tutorial_name'].initial = initial_data

class UploadTimedScriptForm(forms.Form):
    foss_category = forms.ChoiceField(
        choices = [('', 'Select FOSS Category'),],
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    tutorial_name = forms.ChoiceField(
        choices = [('', 'Select Tutorial Name'),],
        widget=forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Tutorial Name field is required.'}
    )

    def __init__(self, user, *args, **kwargs):
        super(UploadTimedScriptForm, self).__init__(*args, **kwargs)
        lang_rec = Language.objects.get(name = 'English')
        foss_list = list(
            FossCategory.objects.filter(
                id__in = ContributorRole.objects.filter(
                    user = user,
                    language = lang_rec,
                    status = 1
                ).values_list(
                    'tutorial_detail__foss_id'
                )
            ).values_list('id', 'foss')
        )
        foss_list.insert(0, ('', 'Select FOSS Category'))
        self.fields['foss_category'].choices = foss_list
        if args:
            if 'foss_category' in args[0]:
                if args[0]['foss_category'] and args[0]['foss_category'] != '' and args[0]['foss_category'] != 'None':
                    initial_data = ''
                    if 'tutorial_name' in args[0]:
                        initial_data = args[0]['tutorial_name']
                    choices = list(TutorialDetail.objects.filter(id__in = TutorialResource.objects.filter(tutorial_detail__foss_id = args[0]['foss_category'], language = lang_rec, script_status = 4).values_list('tutorial_detail_id')).order_by('order').values_list('id', 'tutorial'))
                    choices.insert(0, ('', 'Select Tutorial Name'))
                    self.fields['tutorial_name'].choices = choices
                    self.fields['tutorial_name'].widget.attrs = {}
                    self.fields['tutorial_name'].initial = initial_data


class ChangeComponentStatusForm(forms.Form):
    foss_category = forms.ChoiceField(
        choices = [('', ''),],
        widget=forms.Select(),
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    tutorial_name = forms.ChoiceField(
        choices = [('', 'Select Tutorial'),],
        widget=forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Tutorial Name field is required.'}
    )
    language = forms.ChoiceField(
        choices = [('', 'Select Language'),],
        widget = forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Language field is required.'}
    )
    component = forms.ChoiceField(
        choices = [('', 'Select Component'),],
        widget = forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Component field is required.'}
    )
    status = forms.ChoiceField(
        choices = [('', 'Select Status'),],
        widget = forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Status field is required.'}
    )
    def __init__(self, *args, **kwargs):
        super(ChangeComponentStatusForm, self).__init__(*args, **kwargs)
        foss_list = list(FossCategory.objects.filter(status = 1).values_list('id', 'foss').order_by('foss'))
        foss_list.insert(0, ('', 'Select Foss'))
        self.fields['foss_category'].choices = foss_list
        if args:
             if 'foss_category' in args[0]:
                if args[0]['foss_category']:
                    initial_data = ''
                    if 'language' in args[0]:
                        if args[0]['language']:
                            initial_data = args[0]['language']
                    choices = list(Language.objects.filter(id__in = TutorialResource.objects.filter(tutorial_detail__in = TutorialDetail.objects.filter(foss_id = int(args[0]['foss_category'])).values_list('id'), status = 0).values_list('language_id').distinct()).values_list('id', 'name').order_by('name'))
                    if len(choices):
                        self.fields['language'].widget.attrs = {}
                    choices.insert(0, ('', 'Select Language'))
                    self.fields['language'].choices = choices
                    if initial_data:
                        self.fields['language'].initial = initial_data
                        lang = Language.objects.get(pk = initial_data)
                        tut_init_data = ''
                        if 'tutorial_name' in args[0]:
                            if args[0]['tutorial_name']:
                                tut_init_data = args[0]['tutorial_name']
                        td_list = TutorialDetail.objects.filter(foss_id = args[0]['foss_category']).values_list('id')
                        choices = list(TutorialResource.objects.filter(tutorial_detail_id__in = td_list, language_id = initial_data, status = 0).distinct().values_list('tutorial_detail_id', 'tutorial_detail__tutorial'))
                        if len(choices):
                            self.fields['tutorial_name'].widget.attrs = {}
                        choices.insert(0, ('', 'Select Tutorial'))
                        self.fields['tutorial_name'].choices = choices
                        self.fields['tutorial_name'].initial = tut_init_data
                        comp_init_data = ''
                        if 'component' in args[0]:
                            if args[0]['component']:
                                comp_init_data = args[0]['component']
                        if lang.name == 'English':
                            choices = [('outline', 'Outline'), ('script', 'Script'), ('slide', 'Slides'), ('video', 'Video'), ('code', 'Codefiles'), ('assignment', 'Assignment'), ('prerequisite', 'Prerequisite'), ('keyword', 'Keywords'), ('additional_material', 'Additional Material')]
                        else:
                            choices = [('outline', 'Outline'), ('script', 'Script'), ('video', 'Video')]
                        if len(choices):
                            self.fields['component'].widget.attrs = {}
                        choices.insert(0, ('', 'Select Component'))
                        self.fields['component'].choices = choices
                        self.fields['component'].initial = comp_init_data
                        if tut_init_data and comp_init_data:
                            status_init_data = ''
                            if 'status' in args[0]:
                                if args[0]['status']:
                                    status_init_data = args[0]['status']
                            tr_rec = TutorialResource.objects.select_related().get(tutorial_detail_id = tut_init_data, language = lang)
                            choices = [("0", 'Pending')]
                            compValue = None
                            if comp_init_data in ['outline', 'script', 'video']:
                                compValue = getattr(tr_rec, comp_init_data + '_status')
                            else:
                                compValue = getattr(tr_rec.common_content, comp_init_data + '_status')
                            if compValue:
                                choices.append(("5", 'Need Improvement'))
                            if comp_init_data in ['code', 'assignment','additional_material']:
                                    choices.append(("6", 'Not Required'))
                            if len(choices):
                                self.fields['status'].widget.attrs = {}
                            choices.insert(0, ('', 'Select Status'))
                            self.fields['status'].choices =choices
                            self.fields['status'].initial = status_init_data


class PublishToPending(forms.Form):
    foss_category = forms.ChoiceField(
        widget=forms.Select(),
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    tutorial_name = forms.ChoiceField(
        choices = [('', 'Select Tutorial'),],
        widget=forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Tutorial Name field is required.'}
    )
    language = forms.ChoiceField(
        choices = [('', 'Select Language'),],
        widget = forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Language field is required.'}
    )
    def __init__(self, *args, **kwargs):
        super(PublishToPending, self).__init__(*args, **kwargs)
        foss_list = list(FossCategory.objects.filter(status = 1).values_list('id', 'foss').order_by('foss'))
        foss_list.insert(0, ('', 'Select Foss Category'))
        self.fields['foss_category'].choices = foss_list

        if args:
            if 'foss_category' in args[0]:
                if args[0]['foss_category'] and args[0]['foss_category'] != '' and args[0]['foss_category'] != 'None':
                    initial_data = ''
                    if 'language' in args[0]:
                        if args[0]['language'] and args[0]['language'] != '' and args[0]['language'] != 'None':
                            initial_data = args[0]['language']
                    choices = list(Language.objects.filter(id__in = TutorialResource.objects.filter(tutorial_detail__in = TutorialDetail.objects.filter(foss_id = int(args[0]['foss_category'])).values_list('id'), status = 1).values_list('language_id').distinct()).values_list('id', 'name'))
                    if len(choices):
                        self.fields['language'].widget.attrs = {}
                    choices.insert(0, ('', 'Select Language'))
                    self.fields['language'].choices = choices
                    if initial_data:
                        self.fields['language'].initial = initial_data
                        tut_init_data = ''
                        if 'tutorial_name' in args[0]:
                            if args[0]['tutorial_name'] and args[0]['tutorial_name'] != '' and args[0]['tutorial_name'] != 'None':
                                tut_init_data = args[0]['tutorial_name']
                        td_list = TutorialDetail.objects.filter(foss_id = args[0]['foss_category']).values_list('id')
                        choices = list(TutorialResource.objects.filter(tutorial_detail_id__in = td_list, language_id = initial_data, status = 1).distinct().values_list('tutorial_detail_id', 'tutorial_detail__tutorial'))
                        if len(choices):
                            self.fields['tutorial_name'].widget.attrs = {}
                        choices.insert(0, ('', 'Select Tutorial'))
                        self.fields['tutorial_name'].choices = choices
                        self.fields['tutorial_name'].initial = tut_init_data


class UploadPublishTutorialForm(forms.Form):
    tutorial_name = forms.ChoiceField(
        choices = [('', 'Select Tutorial'),],
        widget=forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Tutorial Name field is required.'}
    )
    language = forms.ChoiceField(
        choices = [('', 'Select Language'),],
        widget = forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Language field is required.'}
    )
    def __init__(self, user, *args, **kwargs):
        super(UploadPublishTutorialForm, self).__init__(*args, **kwargs)
        foss_list = list(
            FossCategory.objects.filter(
                id__in = ContributorRole.objects.filter(
                    user_id = user.id,
                    status = 1
                ).values_list(
                    'tutorial_detail__foss_id'
                )
            ).values_list('id', 'foss')
        )
        foss_list.insert(0, ('', 'Select FOSS category'))
        self.fields['foss_category'] = forms.ChoiceField(
            choices = foss_list,
            error_messages = {'required':'FOSS category field is required.'}
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
                            id__in = ContributorRole.objects.filter(
                                user_id = user.id,
                                foss_category_id = args[0]['foss_category']
                            ).values_list(
                                'language_id'
                            )
                        ).values_list(
                            'id',
                            'name'
                        )
                    )
                    if len(choices):
                        self.fields['language'].widget.attrs = {}
                    choices.insert(0, ('', 'Select Language'))
                    self.fields['language'].choices = choices
                    if initial_data:
                        self.fields['language'].initial = initial_data
                        lang_rec = Language.objects.get(pk = int(initial_data))
                        tut_init_data = ''
                        if 'tutorial_name' in args[0]:
                            if args[0]['tutorial_name'] and args[0]['tutorial_name'] != '' and args[0]['tutorial_name'] != 'None':
                                tut_init_data = args[0]['tutorial_name']
                        if lang_rec.name == 'English':
                            td_list = TutorialDetail.objects.filter(foss_id = args[0]['foss_category']).values_list('id')
                            choices = list(TutorialDetail.objects.filter(
                                id__in = td_list
                            ).values_list('id', 'tutorial'))
                        else:
                            eng_rec = Language.objects.get(name = 'English')
                            td_list = TutorialDetail.objects.filter(foss_id = args[0]['foss_category']).values_list('id')
                            choices = list(TutorialDetail.objects.filter(
                                id__in = TutorialResource.objects.filter(
                                    tutorial_detail_id__in = td_list,
                                    language_id = eng_rec.id,
                                    status = 1
                                ).values_list(
                                    'tutorial_detail_id'
                                )
                            ).values_list('id', 'tutorial'))
                        if len(choices):
                            self.fields['tutorial_name'].widget.attrs = {}
                        choices.insert(0, ('', 'Select Tutorial'))
                        self.fields['tutorial_name'].choices = choices
                        self.fields['tutorial_name'].initial = tut_init_data
                    else:
                        self.fields['tutorial_name'].choices = [('', 'Select Tutorial'),]
                        self.fields['tutorial_name'].widget.attrs = {'disabled': 'disabled'}

class UploadTutorialForm(forms.Form):
    tutorial_name = forms.ChoiceField(
        choices = [('', 'Select Tutorial'),],
        widget=forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Tutorial Name field is required.'}
    )
    language = forms.ChoiceField(
        choices = [('', 'Select Language'),],
        widget = forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Language field is required.'}
    )
    def __init__(self, user, *args, **kwargs):
        super(UploadTutorialForm, self).__init__(*args, **kwargs)
        foss_list = list(
            FossCategory.objects.filter(
                id__in = ContributorRole.objects.filter(
                    user_id = user.id,
                    status = 1
                ).values_list(
                    'tutorial_detail__foss_id'
                )
            ).values_list('id', 'foss')
        )
        foss_list.insert(0, ('', 'Select FOSS category'))
        self.fields['foss_category'] = forms.ChoiceField(
            choices = foss_list,
            error_messages = {'required':'FOSS category field is required.'}
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
                            id__in = ContributorRole.objects.filter(
                                user_id = user.id,
                                tutorial_detail__foss_id = args[0]['foss_category']
                            ).values_list(
                                'language_id'
                            )
                        ).values_list(
                            'id',
                            'name'
                        )
                    )
                    if len(choices):
                        self.fields['language'].widget.attrs = {}
                    choices.insert(0, ('', 'Select Language'))
                    self.fields['language'].choices = choices
                    if initial_data:
                        self.fields['language'].initial = initial_data
                        lang_rec = Language.objects.get(pk = int(initial_data))
                        tut_init_data = ''
                        if 'tutorial_name' in args[0]:
                            if args[0]['tutorial_name'] and args[0]['tutorial_name'] != '' and args[0]['tutorial_name'] != 'None':
                                tut_init_data = args[0]['tutorial_name']
                        if lang_rec.name == 'English':
                            td_list = TutorialDetail.objects.filter(foss_id = args[0]['foss_category']).values_list('id')
                            choices = list(TutorialDetail.objects.filter(
                                id__in = td_list
                            ).exclude(
                                id__in = TutorialResource.objects.filter(
                                    tutorial_detail_id__in = td_list,
                                    language_id = lang_rec.id,
                                    status = 1
                                    ).values_list(
                                        'tutorial_detail_id'
                                    )
                            ).values_list('id', 'tutorial'))
                        else:
                            eng_rec = Language.objects.get(name = 'English')
                            td_list = TutorialDetail.objects.filter(foss_id = args[0]['foss_category']).values_list('id')
                            choices = list(TutorialDetail.objects.filter(
                                id__in = TutorialResource.objects.filter(
                                    tutorial_detail_id__in = td_list,
                                    language_id = eng_rec.id,
                                    status = 1
                                ).values_list(
                                    'tutorial_detail_id'
                                )
                            ).exclude(
                                id__in = TutorialResource.objects.filter(
                                    tutorial_detail_id__in = td_list,
                                    language_id = lang_rec.id,
                                    status__gte = 1
                                ).values_list(
                                    'tutorial_detail_id'
                                )
                            ).values_list('id', 'tutorial'))
                        if len(choices):
                            self.fields['tutorial_name'].widget.attrs = {}
                        choices.insert(0, ('', 'Select Tutorial'))
                        self.fields['tutorial_name'].choices = choices
                        self.fields['tutorial_name'].initial = tut_init_data
                    else:
                        self.fields['tutorial_name'].choices = [('', 'Select Tutorial'),]
                        self.fields['tutorial_name'].widget.attrs = {'disabled': 'disabled'}

class ComponentForm(forms.Form):
    comp = forms.FileField(label = 'Select a file', required = True)
    comptype = forms.CharField(
        required = True,
        error_messages = {'required': 'component type is required.'},
        widget=forms.HiddenInput()
    )

    def clean(self):
        super(ComponentForm, self).clean()
        file_types = {
            'video': 'video/ogg',
            'slide': ['application/zip', 'application/x-zip-compressed'],
            'code': ['application/zip', 'application/x-zip-compressed'],
            'assignment': ['text/plain', 'application/pdf'],
            'additional_material': ['text/plain', 'application/pdf',
                                            'application/zip', 'application/x-zip-compressed',
                                            'application/vnd.oasis.opendocument.text',
                                            'application/vnd.oasis.opendocument.spreadsheet',
                                            'application/vnd.oasis.opendocument.presentation']
        }
        component = ''
        if 'comp' in self.cleaned_data:
            component = self.cleaned_data['comp']
        component_type = self.cleaned_data['comptype']
        if component and component_type:
            if not component.content_type in file_types[component_type]:
                self._errors["comp"] = self.error_class(["Not a valid file format."])
        else:
            raise forms.ValidationError("Access Denied!")
        return component

    def __init__(self, comptype, *args, **kwargs):
        super(ComponentForm, self).__init__(*args, **kwargs)
        if comptype == 'video':
            tmp_choices1 = []
            tmp_choices2 = []
            for i in range(60):
                i_str = str(i)
                if i < 10:
                    i_str = '0' + i_str
                tmp_choices1.append((i_str, i_str))
                tmp_choices2.append((i_str, i_str))
            tmp_choices1.insert(0, ('', 'Select Minutes'))
            self.fields['thumb_mins'] = forms.ChoiceField(
                choices = tmp_choices1,
                widget=forms.Select(),
                required = True,
            )
            tmp_choices2.insert(0, ('', 'Select Seconds'))
            self.fields['thumb_secs'] = forms.ChoiceField(
                choices = tmp_choices2,
                widget=forms.Select(),
                required = True,
            )
            self.fields['isarchive'] = forms.ChoiceField(
                choices = [(0, 'Replace old video'), (1, 'Archive old video as Correction'), (2, 'Archive old video as Version')],
                widget=forms.Select(),
                required = False,
            )
        self.fields['comptype'].initial = comptype

class UploadOutlineForm(forms.Form):
    outline = forms.CharField(
        widget = forms.Textarea,
        required = True,
        error_messages = {'required':'Outline field required'}
    )
    def __init__(self, trid, *args, **kwargs):
        super(UploadOutlineForm, self).__init__(*args, **kwargs)
        outline_rec = TutorialResource.objects.get(pk = trid)
        if outline_rec.outline:
            self.fields['outline'].initial = outline_rec.outline


class UploadScriptForm(forms.Form):
    scriptpath = forms.CharField(
        required = True,
        error_messages = {'required': 'script path is required'},
        widget=forms.HiddenInput()
    )
    def __init__(self, path, *args, **kwargs):
        super(UploadScriptForm, self).__init__(*args, **kwargs)
        self.fields['scriptpath'].initial = path


class UploadKeywordsForm(forms.Form):
    keywords = forms.CharField(
        widget = forms.Textarea,
        required = True,
        error_messages = {'required':'Keywords field required'}
    )
    def __init__(self, trid, *args, **kwargs):
        super(UploadKeywordsForm, self).__init__(*args, **kwargs)
        keywords_rec = TutorialResource.objects.select_related().get(pk = trid)
        if keywords_rec.common_content.keyword:
            self.fields['keywords'].initial = keywords_rec.common_content.keyword

class ContributorRoleForm(forms.ModelForm):
    user = forms.ModelChoiceField(

        queryset = User.objects.filter(Q(groups__name = 'Contributor')|Q(groups__name = 'External-Contributor')).order_by('username'),
        help_text = "",
        error_messages = {'required': 'User field required.'}
    )
    foss_category = forms.ModelChoiceField(
        queryset = FossCategory.objects.filter(status = 1).order_by('foss'),
        empty_label = "----------",
        help_text = "",
        error_messages = {'required': 'FOSS category field required.'}
    )
    language = forms.ModelChoiceField(

        queryset = Language.objects.order_by('name'),
        empty_label = "----------",
        help_text = "",
        error_messages = {'required': 'Language field required.'}
    )
    status = forms.BooleanField(required = False)
    grant_to_all = forms.BooleanField(required = False,help_text = "Grants Contributor Role for all the tutorials for the selected FOSS" )

    class Meta(object):
        model = ContributorRole
        exclude = ['created', 'updated']


class DomainReviewerRoleForm(forms.ModelForm):
    user = forms.ModelChoiceField(

        queryset = User.objects.filter(Q(groups__name = 'Domain-Reviewer')).order_by('username'),
        help_text = "",
        error_messages = {'required': 'User field required.'}
    )
    foss_category = forms.ModelChoiceField(

        queryset = FossCategory.objects.filter(status = 1).order_by('foss'),
        empty_label = "----------",
        help_text = "",
        error_messages = {'required': 'FOSS category field required.'}
    )
    language = forms.ModelChoiceField(

        queryset = Language.objects.order_by('name'),
        empty_label = "----------",
        help_text = "", error_messages = {'required': 'Language field required.'}
    )
    status = forms.BooleanField(required = False)

    class Meta(object):
        model = DomainReviewerRole
        exclude = ['created', 'updated']

class QualityReviewerRoleForm(forms.ModelForm):
    user = forms.ModelChoiceField(

        queryset = User.objects.filter(Q(groups__name = 'Quality-Reviewer')).order_by('username'),
        help_text = "", error_messages = {'required': 'User field required.'}
    )
    foss_category = forms.ModelChoiceField(

        queryset = FossCategory.objects.filter(status = 1).order_by('foss'),
        empty_label = "----------",
        help_text = "",
        error_messages = {'required': 'FOSS category field required.'}
    )
    language = forms.ModelChoiceField(

        queryset = Language.objects.order_by('name'),
        empty_label = "----------",
        help_text = "",
        error_messages = {'required': 'Language field required.'}
    )
    status = forms.BooleanField(required = False)

    class Meta(object):
        model = QualityReviewerRole
        exclude = ['created', 'updated']

class ReviewVideoForm(forms.Form):
    video_status = forms.ChoiceField(
        choices = [('', '------'), (2, 'Accept'), (5, 'Need improvement')],
        required = True,
        error_messages = {'required': 'Please select the status'}
    )
    feedback = forms.CharField(
        widget = forms.Textarea,
        required = False
    )


class DomainReviewComponentForm(forms.Form):
    component_status = forms.ChoiceField(
        choices = [('', '------'), (3, 'Accept'), (5, 'Need improvement')],
        required = True,
        error_messages = {'required': 'Please select the status'}
    )
    feedback = forms.CharField(
        widget = forms.Textarea,
        required = False
    )


class QualityReviewComponentForm(forms.Form):
    component_status = forms.ChoiceField(
        choices = [('', '------'), (4, 'Accept'), (5, 'Need improvement')],
        required = True,
        error_messages = {'required': 'Please select the status'}
    )
    feedback = forms.CharField(
        widget = forms.Textarea,
        required = False
    )


class TutorialMissingComponentForm(forms.Form):
    component = forms.ChoiceField(
        choices = [('', 'Select Component'), (1, 'Outline'), (2, 'Script'), (3, 'Video'), (4, 'Slides'), (5, 'Codefiles'), (6, 'Assignment')],
        required = True,
        error_messages = {'required': 'Please select component'}
    )
    report_type = forms.ChoiceField(
        choices = [(0, 'Component itself is missing'), (1, 'Some content is missing')],
        widget = forms.RadioSelect(),
        required = True,
        error_messages = {'required': 'Please select one from the above options'}
    )
    remarks = forms.CharField(
        widget = forms.Textarea,
        required = False,
        error_messages = {'required': 'Please fill the Remarks field'}
    )
    inform_me = forms.ChoiceField(
        choices = [(0, 'No'), (1, 'Yes')],
        widget = forms.RadioSelect(),
        required = True,
        error_messages = {'required': 'Please select one from the above options'}
    )
    email = forms.EmailField(required = False, error_messages = {'required': 'Please fill the Email field'})

    def __init__(self, user, *args, **kwargs):
        super(TutorialMissingComponentForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        super(TutorialMissingComponentForm, self).clean()
        print((self.user))
        if 'report_type' in self.cleaned_data:
            if self.cleaned_data['report_type'] == '1':
                if 'remarks' in self.cleaned_data:
                    if not self.cleaned_data['remarks']:
                        self._errors['remarks'] = '<ul class="errorlist"><li>Please fill Remarks field</li></ul>'
                else:
                    self._errors['remarks'] = '<ul class="errorlist"><li>Please fill Remarks field</li></ul>'
        if 'inform_me' in self.cleaned_data:
            print((self.cleaned_data))
            if self.cleaned_data['inform_me'] == '1':
                print((self.cleaned_data['inform_me']))
                if not self.user.is_authenticated():
                    if 'email' in self.cleaned_data:
                        if not self.cleaned_data['email']:
                            self._errors['email'] = '<ul class="errorlist"><li>Please fill Email field</li></ul>'
                    else:
                        self._errors['email'] = '<ul class="errorlist"><li>Please fill Email field</li></ul>'

class TutorialMissingComponentReplyForm(forms.Form):
    reply_message = forms.CharField(
        widget = forms.Textarea,
        required = True,
        error_messages = {'required': 'Please fill the "Reply Message" field'}
    )

class SuggestTopicForm(forms.ModelForm):
    difficulty_level = forms.ModelChoiceField(

        widget = forms.Select(
            attrs = {'class' : 'ac-state'}),
            queryset = Level.objects.all().order_by('id'),
            empty_label = "Select Difficulty Level",
            help_text = "",
            error_messages = {'required':'Please select Difficulty Level'}
    )
    example_suggestion = forms.ChoiceField(
        choices = [(True, 'Yes'), (False, 'No')],
        required = True,
        error_messages = {'required': 'Please select Yes or No for this option'}
    )

    class Meta(object):
        model = SuggestTopic
        exclude = ['user', 'created']

class SuggestExampleForm(forms.ModelForm):
    script_writer = forms.ChoiceField(
        choices = [(True, 'Yes'), (False, 'No')],
        required = True,
        error_messages = {'required': 'Please select Yes or No for this option'}
    )
    is_reviewer = forms.ChoiceField(
        choices = [(True, 'Yes'), (False, 'No')],
        required = True,
        error_messages = {'required': 'Please select Yes or No for this option'}
    )
    class Meta(object):
        model = SuggestExample
        exclude = ['user', 'created']

class CollaborateForm(forms.ModelForm):
    are_you_one = forms.ChoiceField(
        choices=[('Novice', 'Novice'), ('Junior Expert', 'Junior Expert'), ('Mature Expert', 'Mature Expert')],
        widget=forms.RadioSelect()
    )
    howmuch_time = forms.ChoiceField(
        choices=[(1, '1 Hour per day'), (2, '2 Hours per week'), (3, '6 Hours per month')],
        widget=forms.RadioSelect()
    )
    is_reviewer = forms.ChoiceField(
        choices = [(True, 'Yes'), (False, 'No')],
        required = True,
        error_messages = {'required': 'Please select Yes or No for this option'}
    )
    lang_contributor = forms.ChoiceField(
        choices = [(True, 'Yes'), (False, 'No')],
        required = True,
        error_messages = {'required': 'Please select Yes or No for this option'}
    )
    lead_st = forms.ChoiceField(
        choices = [(True, 'Yes'), (False, 'No')],
        required = True,
        error_messages = {'required': 'Please select Yes or No for this option'}
    )
    class Meta(object):
        model = Collaborate
        exclude = ['user', 'created']

class AvailableFossForm(forms.ModelForm):
    foss = forms.ModelChoiceField(

        queryset = FossCategory.objects.filter(status = 1).order_by('foss'),
        empty_label = "----------",
        help_text = "",
        error_messages = {'required': 'FOSS category field required.'}
    )

class UpdatePrerequisiteForm(forms.Form):
    source_foss = forms.ChoiceField(
        choices = [('', '-- Select Foss --'),] + list(FossCategory.objects.filter(status=1).values_list('id', 'foss').order_by('foss')),
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    source_tutorial = forms.ChoiceField(
        choices = [('', '-- Select Tutorial --'),],
        widget=forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Tutorial Name field is required.'}
    )
    destination_foss = forms.ChoiceField(
        choices = [('', '-- Select Foss --'), ('0', '-- Not Required --'),] + list(FossCategory.objects.filter(status=1).values_list('id', 'foss').order_by('foss')),
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    destination_tutorial = forms.ChoiceField(
        choices = [('', '-- Select Tutorial --'), ('0', '-- Not Required --'),],
        widget=forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Tutorial Name field is required.'}
    )

    def __init__(self, *args, **kwargs):
        super(UpdatePrerequisiteForm, self).__init__(*args, **kwargs)
        if args:
            if 'source_foss' in args[0]:
                if args[0]['source_foss'] and args[0]['source_foss'] != '' and args[0]['source_foss'] != 'None':
                    initial_data = ''
                    td_list = TutorialDetail.objects.filter(foss_id = args[0]['source_foss']).values_list('id')
                    lang_rec = Language.objects.get(name = 'English')
                    choices = list(
                        TutorialDetail.objects.filter(
                            id__in = TutorialResource.objects.filter(
                                tutorial_detail_id__in = td_list,
                                language_id = lang_rec.id,
                            ).values_list(
                                'tutorial_detail_id'
                            )
                        ).values_list(
                            'id',
                            'tutorial'
                        )
                    )
                    choices.insert(0, ('', 'Select Tutorial'))
                    self.fields['source_tutorial'].choices = choices
                    self.fields['source_tutorial'].widget.attrs = {}
                    self.fields['source_tutorial'].initial = initial_data
            if 'destination_foss' in args[0]:
                if args[0]['destination_foss'] and args[0]['destination_foss'] != '' and args[0]['destination_foss'] != 'None':
                    initial_data = ''
                    td_list = TutorialDetail.objects.filter(foss_id = args[0]['destination_foss']).values_list('id')
                    lang_rec = Language.objects.get(name = 'English')
                    choices = list(
                        TutorialDetail.objects.filter(
                            id__in = TutorialResource.objects.filter(
                                tutorial_detail_id__in = td_list,
                                language_id = lang_rec.id,
                            ).values_list(
                                'tutorial_detail_id'
                            )
                        ).values_list(
                            'id',
                            'tutorial'
                        )
                    )
                    choices.insert(0, ('', '-- Select Tutorial --'))
                    choices.insert(1, ('0', '-- Not Required --'))
                    self.fields['destination_tutorial'].choices = choices
                    self.fields['destination_tutorial'].widget.attrs = {}
                    self.fields['destination_tutorial'].initial = initial_data

class UpdateKeywordsForm(forms.Form):
    foss = forms.ChoiceField(
        choices = [('', '-- Select Foss --'),] + list(FossCategory.objects.filter(status=1).values_list('id', 'foss').order_by('foss')),
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    tutorial = forms.ChoiceField(
        choices = [('', '-- Select Tutorial --'),],
        widget=forms.Select(attrs = {'disabled': 'disabled'}),
        required = True,
        error_messages = {'required': 'Tutorial Name field is required.'}
    )
    keywords = forms.CharField(
        widget = forms.Textarea,
        required = True,
        error_messages = {'required':'Keywords field required'}
    )

    def __init__(self, *args, **kwargs):
        super(UpdateKeywordsForm, self).__init__(*args, **kwargs)
        if args:
            if 'foss' in args[0] and args[0]['foss']:
                initial_data = ''
                if 'tutorial' in args[0] and args[0]['tutorial']:
                    initial_data = args[0]['tutorial']
                choices = TutorialResource.objects.filter(
                    tutorial_detail__foss_id = args[0]['foss'],
                    language__name = 'English'
                ).values_list('tutorial_detail_id', 'tutorial_detail__tutorial').order_by('tutorial_detail__tutorial')
                self.fields['tutorial'].choices = choices
                self.fields['tutorial'].widget.attrs = {}
                self.fields['tutorial'].initial = initial_data


class UpdateSheetsForm(forms.Form):
    foss = forms.ChoiceField(
        choices = [('', '-- Select Foss --'),] + list(TutorialResource.objects.filter(Q(status = 1) | Q(status = 2), language__name='English').values_list('tutorial_detail__foss_id', 'tutorial_detail__foss__foss').order_by('tutorial_detail__foss__foss').distinct()),
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    language = forms.ChoiceField(
        choices=[('', '-- Select Language --'), ],
        widget=forms.Select(attrs={'disabled': 'disabled'}),
        required=True,
        error_messages={'required': 'Language field is required.'}
    )
    comp = forms.FileField(required=False)

    def clean(self):
        super(UpdateSheetsForm, self).clean()
        file_types = ['application/pdf']
        component = ''
        if 'comp' in self.cleaned_data:
            component = self.cleaned_data['comp']
        if component:
            if not component.content_type in file_types:
                self._errors["comp"] = self.error_class(["Not a valid file format."])
        else:
            self._errors["comp"] = self.error_class(["This field is required."])
        return component

    def __init__(self, *args, **kwargs):
        super(UpdateSheetsForm, self).__init__(*args, **kwargs)

        if args:
            if 'foss' in args[0] and args[0]['foss']:
                initial_lang = ''
                if 'language' in args[0] and args[0]['language']:
                    initial_lang = args[0]['language']
                choices = TutorialResource.objects.filter(Q(status = 1) | Q(status = 2), tutorial_detail__foss_id = args[0]['foss']).values_list('language_id', 'language__name').order_by('language__name').distinct()
                self.fields['language'].choices =  [('', '-- Select Language --'),] + list(choices)
                self.fields['language'].widget.attrs = {}
                self.fields['language'].initial = initial_lang

class UpdateAssignmentForm(forms.Form):
    foss = forms.ChoiceField(
        choices = [('', '-- Select Foss --'),] + list(TutorialResource.objects.filter(Q(status = 1) |
            Q(status = 2), language__name='English').values_list(
            'tutorial_detail__foss_id', 'tutorial_detail__foss__foss').order_by(
            'tutorial_detail__foss__foss').distinct()),
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    tutorial = forms.ChoiceField(
        choices=[('', '-- Select Tutorial --'), ],
        widget=forms.Select(attrs={'disabled': 'disabled'}),
        required=True,
        error_messages={'required': 'Tutorial field is required.'}
    )
    comp = forms.FileField(required=False)

    def clean(self):
        super(UpdateAssignmentForm, self).clean()
        component = ''
        if 'comp' in self.cleaned_data:
            component = self.cleaned_data['comp']
        if not component:
            self._errors["comp"] = self.error_class(["This field is required."])
        return component

    def __init__(self, *args, **kwargs):
        super(UpdateAssignmentForm, self).__init__(*args, **kwargs)

        if args:
            if 'foss' in args[0] and args[0]['foss']:
                initial_tut = ''
                if 'tutorial' in args[0] and args[0]['tutorial']:
                    initial_tut = args[0]['tutorial']
                choices = TutorialResource.objects.filter(Q(status = 1) | Q(status = 2), tutorial_detail__foss_id = args[0]['foss']).values_list('tutorial_detail_id', 'tutorial_detail__tutorial').order_by('tutorial_detail__tutorial').distinct()
                self.fields['tutorial'].choices =  [('', '-- Select tutorial --'),] + list(choices)
                self.fields['tutorial'].widget.attrs = {}
                self.fields['tutorial'].initial = initial_tut

class UpdateCodefilesForm(forms.Form):
    foss = forms.ChoiceField(
        choices = [('', '-- Select Foss --'),] + list(TutorialResource.objects.filter(Q(status = 1) |
            Q(status = 2), language__name='English').values_list(
            'tutorial_detail__foss_id', 'tutorial_detail__foss__foss').order_by(
            'tutorial_detail__foss__foss').distinct()),
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    tutorial = forms.ChoiceField(
        choices=[('', '-- Select Tutorial --'), ],
        widget=forms.Select(attrs={'disabled': 'disabled'}),
        required=True,
        error_messages={'required': 'Tutorial field is required.'}
    )
    comp = forms.FileField(required=False)

    def clean(self):
        super(UpdateCodefilesForm, self).clean()
        component = ''
        if 'comp' in self.cleaned_data:
            component = self.cleaned_data['comp']
        if not component:
            self._errors["comp"] = self.error_class(["This field is required."])
        return component

    def __init__(self, *args, **kwargs):
        super(UpdateCodefilesForm, self).__init__(*args, **kwargs)

        if args:
            if 'foss' in args[0] and args[0]['foss']:
                initial_tut = ''
                if 'tutorial' in args[0] and args[0]['tutorial']:
                    initial_tut = args[0]['tutorial']
                choices = TutorialResource.objects.filter(Q(status = 1) | Q(status = 2), tutorial_detail__foss_id = args[0]['foss']).values_list('tutorial_detail_id', 'tutorial_detail__tutorial').order_by('tutorial_detail__tutorial').distinct()
                self.fields['tutorial'].choices =  [('', '-- Select tutorial --'),] + list(choices)
                self.fields['tutorial'].widget.attrs = {}
                self.fields['tutorial'].initial = initial_tut

class UpdateCommonCompForm(forms.Form):
    foss = forms.ChoiceField(
        choices = [('', '-- Select Foss --'),] + list(TutorialResource.objects.filter(Q(status = 1) |
            Q(status = 2), language__name='English').values_list(
            'tutorial_detail__foss_id', 'tutorial_detail__foss__foss').order_by(
            'tutorial_detail__foss__foss').distinct()),
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    tutorial = forms.ChoiceField(
        choices=[('', '-- Select Tutorial --'), ],
        widget=forms.Select(attrs={'disabled': 'disabled'}),
        required=True,
        error_messages={'required': 'Tutorial field is required.'}
    )
    comp = forms.FileField(required=False)
    component_type = forms.ChoiceField(
        choices = [('', '-- Select Type --'), ('Codefiles', 'Codefiles'), ('Slides', 'Slides'), ('Additionalmaterial', 'Additional Material')],
        required = True,
        error_messages = {'required': 'Please select component type'}
    )

    def clean(self):
        super(UpdateCommonCompForm, self).clean()
        component = ''
        if 'comp' in self.cleaned_data:
            component = self.cleaned_data['comp']
        if not component:
            self._errors["comp"] = self.error_class(["This field is required."])
        return component

    def __init__(self, *args, **kwargs):
        super(UpdateCommonCompForm, self).__init__(*args, **kwargs)

        if args:
            if 'foss' in args[0] and args[0]['foss']:
                initial_tut = ''
                if 'tutorial' in args[0] and args[0]['tutorial']:
                    initial_tut = args[0]['tutorial']
                choices = TutorialResource.objects.filter(Q(status = 1) | Q(status = 2), tutorial_detail__foss_id = args[0]['foss']).values_list('tutorial_detail_id', 'tutorial_detail__tutorial').order_by('tutorial_detail__tutorial').distinct()
                self.fields['tutorial'].choices =  [('', '-- Select tutorial --'),] + list(choices)
                self.fields['tutorial'].widget.attrs = {}
                self.fields['tutorial'].initial = initial_tut

class LanguageManagerForm(forms.ModelForm):

    user = forms.ModelChoiceField(
                                  queryset=User.objects.filter(Q(groups__name='Contributor'
                                  )
                                  | Q(groups__name='External-Contributor'
                                  )).distinct().order_by('username'), help_text=''
                                  ,
                                  error_messages={'required': 'User field required.'
                                  })
    language = forms.ModelChoiceField(
            queryset=Language.objects.order_by('name'),
            empty_label='----------', help_text='',
            error_messages={'required': 'Language field required.'})
    status = forms.BooleanField(required=False)

    class Meta:

        model = LanguageManager
        exclude = ['created', 'updated']
