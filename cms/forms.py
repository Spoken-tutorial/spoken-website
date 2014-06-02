from django import forms
from cms.models import *
from events.models import *
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
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

class ProfileForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    street = forms.CharField()
    #location = forms.CharField()
    #district = forms.CharField()
    #city = forms.CharField()
    #state = forms.CharField()
    country = forms.CharField()
    pincode = forms.CharField()
    phone = forms.CharField(required = False)
    
    state = forms.ModelChoiceField(label='State', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-state'}), queryset = State.objects.order_by('name'), empty_label = "--- None ---", help_text = "", error_messages = {'required':'State field required.'})
    
    district = forms.ModelChoiceField(label='Dist', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-district'}), queryset = District.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'Institute Type field required.'})
    
    city = forms.ModelChoiceField(label='City', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-city'}), queryset = City.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'City Type field required.'})
    
    location = forms.ModelChoiceField(label='Location', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-location'}), queryset = Location.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'City Type field required.'})
    def __init__(self, *args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
            del kwargs["instance"]
        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]
            
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['street'].initial = initial.street
        #self.fields['location'].initial = initial.location
        #self.fields['district'].initial = initial.district
        #self.fields['city'].initial = initial.city
        #self.fields['state'].initial = initial.state
        self.fields['country'].initial = initial.country
        self.fields['pincode'].initial = initial.pincode
        self.fields['phone'].initial = initial.phone
        
        if args:
            if 'district' in args[0]:
                if args[0]['district'] and args[0]['district'] != '' and args[0]['district'] != 'None':
                    self.fields["location"].queryset = Location.objects.filter(district__id=args[0]['district'])
                    
            if 'state' in args[0]:
                if args[0]['state'] != '' and args[0]['state'] != 'None':
                    self.fields["district"].queryset = District.objects.filter(state__id=args[0]['state'])
                    self.fields["city"].queryset = City.objects.filter(state__id=args[0]['state'])
        try:
            if initial:
                if initial.district:
                    self.fields["location"].queryset = Location.objects.filter(district__id=initial.district_id)
                if initial.state:
                    self.fields['state'].initial = initial.state
                    self.fields["district"].queryset = District.objects.filter(state__id=initial.state_id)
                    self.fields["city"].queryset = City.objects.filter(state__id=initial.state_id)
                    if initial.district:
                        self.fields['district'].initial = initial.district
                    if initial.city:
                        self.fields['city'].initial = initial.city
                    if initial.location:
                        self.fields['location'].initial = initial.location
        except Exception, e:
            print e
            pass
