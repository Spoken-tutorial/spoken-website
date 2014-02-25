from django import forms
from cms.models import *
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

class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['first_name', 'last_name', 'street', 'location', 'district', 'city', 'state', 'country', 'pincode', 'phone']
