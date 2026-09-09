# Third Party Stuff
import datetime
from django import forms
from django.conf import settings
from django.db.models import Q

# Spoken Tutorial Stuff
from creation.models import *
from spoken import config as spoken_config
from donate.subscription import has_active_subscription, is_student_insti_subscribed, is_organiser_insti_subscribed
from events.models import Invigilator, Organiser, StudentMaster, Student
import json

def is_cdcontent_role_allowed(user):
    if not user or not user.is_authenticated() or not user.pk:
        return False
    if user.is_superuser:
        return True
    allowed_roles = getattr(spoken_config, 'CD_CONTENT_ALLOWED_ROLES', [])
    return user.groups.filter(name__in=allowed_roles).exists()

def is_invigilator_insti_subscribed(user):
    try:
        academic = Invigilator.objects.get(user=user).academic
        return has_active_subscription(academic.id)
    except Exception:
        return False

def is_user_insti_subscribed(user):
    if not user or not user.is_authenticated() or not user.pk:
        return False
    if hasattr(user, 'organiser') and is_organiser_insti_subscribed(user):
        return True
    if hasattr(user, 'student') and is_student_insti_subscribed(user):
        return True
    if hasattr(user, 'invigilator') and is_invigilator_insti_subscribed(user):
        return True
    return False

def jsonify(data):
    return json.loads(data.replace("u'", "'").replace("'", '"'))

class CDContentForm(forms.Form):
    foss_category = forms.ChoiceField(
        choices = [('', 'Select FOSS Category')],
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
        user = kwargs.pop('user', None)
        super(CDContentForm, self).__init__(*args, **kwargs)
        #self.fields['language'].choices = ['nothing']
        bypass_download = is_cdcontent_role_allowed(user)
        is_subscribed = is_user_insti_subscribed(user) if not bypass_download else False

        if bypass_download:
            healthfosslist = list(FossCategory.objects.filter(show_on_homepage=0, foss__contains='Health').values_list('id', 'foss'))
            foss_list = list(TutorialResource.objects.filter(
                Q(status=1) | Q(status=2),
                tutorial_detail__foss__show_on_homepage=1
            ).values_list('tutorial_detail__foss_id', 'tutorial_detail__foss__foss').order_by('tutorial_detail__foss__foss').distinct()) + healthfosslist
        elif is_subscribed:
            restriction_date = getattr(spoken_config, 'TUTORIAL_RESTRICTION_DATE', None)
            if restriction_date:
                if isinstance(restriction_date, datetime.date) and not isinstance(restriction_date, datetime.datetime):
                    if settings.USE_TZ:
                        from django.utils import timezone
                        restr_datetime = timezone.make_aware(datetime.datetime.combine(restriction_date, datetime.time.min))
                    else:
                        restr_datetime = datetime.datetime.combine(restriction_date, datetime.time.min)
                else:
                    restr_datetime = restriction_date

                disqualified_foss_ids = set(TutorialResource.objects.filter(
                    Q(status=1) | Q(status=2),
                    is_unrestricted=False,
                    publish_at__gte=restr_datetime
                ).values_list('tutorial_detail__foss_id', flat=True).distinct())

                foss_filter = Q(tutorial_detail__foss__download=True) | ~Q(tutorial_detail__foss_id__in=disqualified_foss_ids)
                health_foss_filter = Q(download=True) | ~Q(id__in=disqualified_foss_ids)
            else:
                foss_filter = Q()
                health_foss_filter = Q()

            healthfosslist = list(FossCategory.objects.filter(
                Q(show_on_homepage=0) & Q(foss__contains='Health') & health_foss_filter
            ).values_list('id', 'foss'))
            foss_list = list(TutorialResource.objects.filter(
                Q(status=1) | Q(status=2),
                tutorial_detail__foss__show_on_homepage=1
            ).filter(foss_filter).values_list('tutorial_detail__foss_id', 'tutorial_detail__foss__foss').order_by('tutorial_detail__foss__foss').distinct()) + healthfosslist
        else:
            healthfosslist = list(FossCategory.objects.filter(show_on_homepage=0, foss__contains='Health', download=True).values_list('id', 'foss'))
            foss_list = list(TutorialResource.objects.filter(
                Q(status=1) | Q(status=2),
                tutorial_detail__foss__show_on_homepage=1,
                tutorial_detail__foss__download=True
            ).values_list('tutorial_detail__foss_id', 'tutorial_detail__foss__foss').order_by('tutorial_detail__foss__foss').distinct()) + healthfosslist

        foss_choices = [('', 'Select FOSS Category')] + foss_list
        self.fields['foss_category'].choices = foss_choices
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
