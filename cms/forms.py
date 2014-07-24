from django import forms
from cms.models import *
from events.models import *
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from nicedit.widgets import NicEditWidget
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinLengthValidator, MinValueValidator, RegexValidator, URLValidator

class LoginForm(forms.Form):
    username = forms.CharField(
        required = True
    )
    password = forms.CharField(
        widget = forms.PasswordInput,
        required=True
    )

class RegisterForm(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        max_length=30,
        widget=forms.TextInput(),
        required=True,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9-_+.]*$',
                message='Username required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
                code='invalid_username'
                ),
            ]
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=False),
        min_length=8,
    )
    password_confirm = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput(render_value=False),
        min_length=8,
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.TextInput(), required=True)
    captcha = CaptchaField()
    
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u'%s already exists' % username )
        
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(u'%s already exists' % email )
        
    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    state = forms.ModelChoiceField(label='State', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-state'}), queryset = State.objects.order_by('name'), empty_label = "--- None ---", help_text = "", error_messages = {'required':'State field required.'})
    
    district = forms.ModelChoiceField(label='Dist', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-district'}), queryset = District.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'District Type field required.'})
    
    city = forms.ModelChoiceField(label='City', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-city'}), queryset = City.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'City Type field required.'})
    
    location = forms.ModelChoiceField(label='Location', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-location'}), queryset = Location.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'Location Type field required.'}, required = False)
    
    def __init__(self, user, *args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]
            
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields["state"].queryset = State.objects.filter()
        if args:
            if 'state' in args[0]:
                if args[0]['state'] != '' and args[0]['state'] != 'None':
                    self.fields["district"].queryset = District.objects.filter(state__id=args[0]['state'])
                    self.fields["city"].queryset = City.objects.filter(state__id=args[0]['state'])
        if initial:
            self.fields["district"].queryset = District.objects.filter(state__id=initial.state_id)
            self.fields["city"].queryset = City.objects.filter(state__id=initial.state_id)
            
    class Meta:
        model = Profile
        exclude = ['user', 'confirmation_code']

#Overwrite NewsAdminBodyField
class AdminBodyForm(forms.ModelForm):
    body = forms.CharField(
            widget=NicEditWidget(attrs={'style': 'width: 800px;'}))

