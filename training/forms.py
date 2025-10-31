from builtins import str
from builtins import object
from django import forms
from django.contrib.auth.models import User
from .helpers import is_user_paid
from events.models import *
from training.models import *
from .validators import validate_csv_file
import phonenumbers
from spoken.config import DEFAULT_ILW_HOST_COLLEGE
from health_app.models import *

CITY_DEPENDENT_EVENTS=['HN', 'PDP', 'CDP']
class CreateTrainingEventForm(forms.ModelForm):
    ilw_course = forms.CharField(required=False)
    event_coordinator_email = forms.CharField(required = False)
    event_coordinator_contact_no = forms.CharField(required = False)
    foss_data = forms.ModelMultipleChoiceField(queryset=FossCategory.objects.filter(id__in=CourseMap.objects.filter(category=0, test=1).values('foss_id')))
    city = forms.ModelChoiceField(queryset=City.objects.none(), required=False)
    host_college = forms.ModelChoiceField(queryset=AcademicCenter.objects.none(), required=False)
    
    class Meta(object):
        model = TrainingEvents
        exclude = ['entry_user', 'training_status', 'Language_of_workshop', 'foss']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        selected_state = self.data.get('state')
        event_type = self.data.get('event_type')
        if event_type in CITY_DEPENDENT_EVENTS:
            self.fields['host_college'].queryset = AcademicCenter.objects.filter(id=DEFAULT_ILW_HOST_COLLEGE)
        else:
            self.fields['host_college'].queryset = AcademicCenter.objects.filter(state=selected_state)
        if selected_state:
            self.fields['city'].queryset = City.objects.filter(state=selected_state)
        else:            
            self.fields['city'].queryset = City.objects.none()


    def clean(self):
        cleaned_data = super().clean()
        event_type = cleaned_data.get('event_type')
        if event_type in CITY_DEPENDENT_EVENTS:
            cleaned_data['host_college'] = AcademicCenter.objects.get(id=DEFAULT_ILW_HOST_COLLEGE)
        if event_type != 'INTERN':
            cleaned_data['payment_required'] = False
        return cleaned_data


class EditTrainingEventForm(CreateTrainingEventForm):
    def __init__(self, *args, **kwargs):
        super(EditTrainingEventForm, self).__init__(*args, **kwargs)
        if self.instance:
            if self.instance.course:
                self.fields['ilw_course'].initial = self.instance.course.name
                self.fields['foss_data'].initial = self.instance.course.foss.all()
            event_type = self.instance.event_type
            selected_state = self.instance.state
            if event_type in CITY_DEPENDENT_EVENTS:
                self.fields['city'].queryset = City.objects.filter(state=selected_state)
            else:
                self.fields['host_college'].queryset = AcademicCenter.objects.filter(state=selected_state)
            

    def save(self, commit=False):
        event = super().save(commit=False)
        if self.instance.pk:
            self.update_event(event)
        if commit:
            event.save()
        return event
    
    def update_event(self, event):
        ilw_course = self.cleaned_data['ilw_course']
        foss_data = self.cleaned_data['foss_data']
        course = event.course
        if course is not None:
            course.name = ilw_course
            course.save()
        else:
            course = ILWCourse.objects.create(name=ilw_course)
        course.foss.clear()
        course.foss.set(foss_data)
        event.course = course
        event.save()


class RegisterUser(forms.ModelForm):
    
    state = forms.ModelChoiceField(
            widget = forms.Select(attrs = {'class' : 'ac-state'}),
            queryset = State.objects.order_by('name'),
            empty_label = "--- Select State ---", 
            help_text = "",
            required=True,
            )
    college = forms.CharField(
        required = False,
        error_messages = {'required': 'component type is required.'},
    )
    foss_language = forms.ModelChoiceField(
        queryset = Language.objects.order_by('name'),
        required = False,
        help_text = "You can listen to the FOSS in the above Indian languages"
    )
    phone = forms.CharField(required = True,
        error_messages = {'required': 'Enter valid phone number.'},)
    city = forms.ModelChoiceField(queryset=City.objects.none(), required=False)
    language_hn = forms.ModelChoiceField(queryset=HNLanguage.objects.all(), required=False)
    class Meta(object):
        model = Participant
        fields = ['name', 'email', 'state', 'gender', 'amount', 'foss_language', 'company', 'city', 'language_hn']

    def __init__(self, *args, **kwargs):
        super(RegisterUser, self).__init__(*args, **kwargs)
        self.fields['amount'].required = False
        self.fields['state'].initial = State.objects.get(id=21)
        selected_state = self.data.get('state')
        if selected_state: 
            self.fields['city'].queryset = City.objects.filter(state=selected_state)
        # Fetch languages if event_type is HN
        event_id = self.data.get('event')
        event_type = self.data.get('event_type')
        if event_id and event_type == 'HN':
            event = TrainingEvents.objects.get(id=event_id)
            hn_categories = [x.external_course for x in ExternalCourseMap.objects.filter(foss__in=event.course.foss.all())]
            topic_categories = TopicCategory.objects.filter(category_id__in=hn_categories).values_list('topic_category_id', flat=True)
            languages = HNContributorRole.objects.filter(topic_cat_id__in=topic_categories).values_list('language_id', flat=True)
            langs = HNLanguage.objects.filter(lan_id__in=languages).distinct()
            # self.fields['foss_language'].queryset = langs
            self.fields['language_hn'].queryset = langs
     

    def clean(self):
        cleaned_data = super().clean()
        hn_lang = cleaned_data.get('language_hn')
        if cleaned_data.get('language_hn'):
            cleaned_data['language_hn'] = hn_lang.lan_id
        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise ValidationError("Enter a valid phone number")
        phone = phone.strip()  # Remove any extra spaces
        try:
            # Attempt parsing with a default region (IN for India)
            parsed_number = phonenumbers.parse(phone, "IN")
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise ValidationError("Invalid phone number format. Include country/area code if required.")
            
        if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError("Invalid phone number. Please check the number and try again.")
        formatted_number =  phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        return formatted_number

class UploadParticipantsForm(forms.ModelForm):
    csv_file = forms.FileField(required=True)

    class Meta(object):
        model = Participant
        fields = ['registartion_type']
    
    def clean_csv_file(self):
        data = self.cleaned_data["csv_file"]
        file_data = validate_csv_file(data)
        return file_data

class UploadCollegeForm(forms.ModelForm):
    csv_file = forms.FileField(required=True)

    class Meta(object):
        model = AcademicPaymentStatus
        exclude = ['entry_user']
    
    def clean_csv_file(self):
        data = self.cleaned_data["csv_file"]
        file_data = validate_csv_file(data)
        return file_data

class TrainingManagerPaymentForm(forms.Form):
    state = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs = {}), required = False)
    college = forms.ChoiceField(choices=[('0', '-- None --'), ], widget=forms.Select(attrs = {}), required = False)
    status = forms.ChoiceField(choices=[('', '-- None --'), ('S', 'Successfull'), ('F', 'Failed'),('X','Undefined')], required = False)
    request_type = forms.ChoiceField(choices=[('', '-- None --'), ('I', 'Initiated at Bank'), ('R', 'Reconciled')], required = False)
    fdate = forms.DateTimeField(required = False)
    tdate = forms.DateTimeField(required = False)
    events = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs = {}), required = False)
    user_email = forms.EmailField(max_length = 200, required = False)
    userid = forms.IntegerField(required = False)
    def __init__(self, user,*args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
            del kwargs["instance"]

        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]

        super(TrainingManagerPaymentForm, self).__init__(*args, **kwargs)
        

        rp_states = ResourcePerson.objects.filter(status=1,user=user)
        # load the choices
        state_list = list(State.objects.filter(id__in=rp_states.values('state')).order_by('name').values_list('id', 'name'))
        state_list.insert(0, ('', '-- None --'))
        self.fields['state'].choices = state_list

        centre_choices =[]
        centre_choices.insert(0,(0,'All Colleges'))

        event_choices = []
        event_choices.insert(0,(0,'All Events'))
        
        if args:
            if 'state' in args[0]:
                if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
                    centre_qs = AcademicCenter.objects.filter(state_id=args[0]['state']).order_by('institution_name')
                    centre_choices = [(x.id, '%s, %s' % (x.institution_name, x.academic_code)) for x in centre_qs]
                    centre_choices.insert(0,(0,'All Colleges'))
                    self.fields['college'].choices = centre_choices
                    self.fields['college'].widget.attrs = {}

            if 'college' in args[0]:
                if args[0]['college'] and args[0]['college'] != '' and args[0]['college'] != 'None':
                    event_qs = TrainingEvents.objects.filter(host_college_id=args[0]['college']).order_by('event_name')
                    event_choices = [(x.id, '%s, %s' % (x.event_name, x.event_type)) for x in event_qs]
                    event_choices.insert(0,(0,'All Events'))
                    self.fields['events'].choices = event_choices
                    self.fields['events'].widget.attrs = {}


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        exclude = ['added_by', 'created', 'updated']


