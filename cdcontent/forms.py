# Third Party Stuff
from django import forms
from django.db.models import Q

# Spoken Tutorial Stuff
from creation.models import *
import json
def jsonify(data):
    return json.loads(data.replace("u'", "'").replace("'", '"'))

class CDContentForm(forms.Form):
    healthfosslist = list(FossCategory.objects.filter(show_on_homepage = 0, foss__contains='Health').values_list('id','foss'))

    foss_list = list(TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss__show_on_homepage = 1).values_list('tutorial_detail__foss_id', 'tutorial_detail__foss__foss').order_by('tutorial_detail__foss__foss').distinct())+healthfosslist
    foss_list.insert(0, ('', 'Select FOSS Category'))
    
    foss_category = forms.ChoiceField(
        choices = foss_list,
        required = True,
        error_messages = {'required':'FOSS category field is required.'}
    )
    level = forms.ChoiceField(
        choices = [('', 'Select Level'), (0, 'All'), (1, 'Basic'), (2, 'Intermediate'), (3, 'Advanced')],
        required = True,
        error_messages = {'required':'Level field is required.'}
    )
    language = forms.MultipleChoiceField(
        required = True,
        error_messages = {'required':'Languages field is required.'},
        choices = [('', 'Select Languages')]
    )
    selected_foss = forms.CharField(
        required = True,
        error_messages = {'required': 'Add atleast one foss and language, before pressing "Create ZIP file" button'},
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super(CDContentForm, self).__init__(*args, **kwargs)
        #self.fields['language'].choices = ['nothing']
        if args:
            print("args out ",args)
            if ('foss_category' in args[0]) and ('level' in args[0]):
                print("args in ",args[0])
                if args[0]['foss_category'] and args[0]['foss_category'] != '' and args[0]['foss_category'] != 'None':
                    try:
                        tmp_level = int(args[0]['level'])
                    except:
                        tmp_level = ''
                    if tmp_level:
                        lang_recs = list(TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss_id = int(args[0]['foss_category']), tutorial_detail__level_id = int(tmp_level)).values_list('language_id', 'language__name').order_by('language__name').distinct())
                    else:
                        lang_recs = list(TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss_id = int(args[0]['foss_category'])).values_list('language_id', 'language__name').order_by('language__name').distinct())
                    self.fields['language'].choices = lang_recs
