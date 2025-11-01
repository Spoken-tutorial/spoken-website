
# Third Party Stuff
from builtins import str
from builtins import object
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from nicedit.widgets import NicEditWidget
from ckeditor.widgets import CKEditorWidget
from validate_email import validate_email
from django.contrib.auth.validators import ASCIIUsernameValidator
# Spoken Tutorial Stuff
from cms.models import *
from events.models import *
from cms.validators import ASCIIValidator



class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        validators = [
            ASCIIUsernameValidator(
                message = 'Enter a valid username. 30 characters or fewer. \
                    Letters, digits and ./-/_ only. Please do not copy paste here.',
                code = 'invalid_username'
            ),
        ]
        )
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class RegisterFormHome(forms.Form):
    username = forms.CharField(
        label = _("Username"),
        max_length = 30,
        widget = forms.TextInput(),
        required = True,
        validators = [
            ASCIIUsernameValidator(
                message = 'Enter a valid username. 30 characters or fewer. \
                    Letters, digits and ./-/_ only. Please do not copy paste here.',
                code = 'invalid_username'
            ),
        ]
    )
    first_name = forms.CharField(
        validators = [
            ASCIIValidator(
                message = _(
                        'Please enter a valid first name.'
                        'This field may contain only English letters.'
                        ' Please do not copy paste here.'
                    ),
                code = 'invalid_first_name',
            ), 
        ]
    )
    last_name = forms.CharField(
        validators = [
            ASCIIValidator(
                message = _(
                        'Please enter a valid last name.'
                        'This field may contain only English letters.'
                        ' Please do not copy paste here.'
                    ),
                code = 'invalid_last_name',
            ), 
        ]
    )
    phone = forms.CharField(max_length=20)
    password = forms.CharField(
        label = _("Password"),
        widget = forms.PasswordInput(render_value = False),
        min_length = 8,
    )
    password_confirm = forms.CharField(
        label = _("Password (again)"),
        widget = forms.PasswordInput(render_value = False),
        min_length = 8,
    )
    email = forms.EmailField(
        label = _("Email"),
        widget = forms.TextInput(),
        required=True
    )


    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('%s already exists' % username )


    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            if not validate_email(email):
                raise forms.ValidationError('%s is not valid email.' % email )
        except:
            raise forms.ValidationError('%s is not valid email.' % email )
        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('%s already exists' % email )

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta(object):
        model = Profile
        exclude = ['user', 'confirmation_code', 'street', 'location']

    def clean_picture(self):
       if 'picture' in self.cleaned_data and \
           self.cleaned_data['picture']:
            content_types = ['jpg', 'jpeg', 'png']
            filename = str(self.cleaned_data['picture'])
            ext = os.path.splitext(filename)[1].lower()
            if ext[1:] not in content_types:
                raise forms.ValidationError("Wrong format:Profile picture should be in \"png/jpg\" format only!")

    first_name = forms.CharField()
    last_name = forms.CharField()
    state = forms.ModelChoiceField(label = 'State',   \
        widget = forms.Select(attrs = {'class' : 'ac-state'}), queryset = \
        State.objects.order_by('name'), empty_label = "--- None ---", \
        help_text = "", error_messages = {'required':'State field required.'})

    district = forms.ModelChoiceField(label='Dist',   \
        widget = forms.Select(attrs = {'class' : 'ac-district'}), \
        queryset = District.objects.none(), empty_label = "--- None ---", \
        help_text = "", error_messages = \
        {'required':'District Type field required.'})

    city = forms.ModelChoiceField(label = 'City',   \
    widget = forms.Select(attrs = {'class' : 'ac-city'}), \
    queryset = City.objects.none(), empty_label = "--- None ---", \
    help_text = "", error_messages = {'required':'City Type field required.'})


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
        if initial:
            self.fields["district"].queryset = \
                District.objects.filter(state__id = initial.state_id)
            self.fields["city"].queryset = \
                City.objects.filter(state__id = initial.state_id)

        if args:
            if 'state' in args[0]:
                if args[0]['state'] != '' and args[0]['state'] != 'None':
                    self.fields["district"].queryset = \
                        District.objects.filter(state__id = args[0]['state'])
                    self.fields["city"].queryset = \
                        City.objects.filter(state__id = args[0]['state'])


#Overwrite NewsAdminBodyField
class AdminBodyForm(forms.ModelForm):
    body = forms.CharField(
            widget = CKEditorWidget(attrs = {'style': 'width: 800px;'}))


class CmsPageForm(forms.ModelForm):
    body = forms.CharField(widget = CKEditorWidget(attrs = \
        {'style': 'width: 800px;'}))
    cols = forms.ChoiceField(choices = ((6, '6'), (7, '7'), (8, '8'), \
        (9, '9'), (10, '10'), (11, '11'), (12, '12')))


    class Meta(object):
        model = Page
        exclude = ['created']


class PasswordResetForm(forms.Form):
    email = forms.EmailField()


    def clean_email(self):
        email = self.cleaned_data['email']
        error = 1
        er_msg = None
        try:
            user = User.objects.filter(email=email).first()
            if user:
              if user.is_active:
                print((user.is_active))
                error = 0
              else:
                error = 1
                er_msg = "Your account is not activated. Kindly activate the account by clicking on the activation link which has been sent to your registered email id."
            else:
              error = 1
              er_msg= 'Email: %s not exists' % email
        except Exception as e:
            print(e)
        if error:
            raise forms.ValidationError( er_msg )


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        #min_length=8,
    )
    code = forms.CharField()
    userid = forms.CharField()
    new_password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        min_length=8,
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        min_length=8,
    )


    def clean(self):
        profile = Profile.objects.get(user_id = self.cleaned_data['userid'], \
            confirmation_code = self.cleaned_data['code'])
        user = profile.user
        if 'old_password' in self.cleaned_data:
            if not user.check_password(self.cleaned_data['old_password']):
                raise forms.ValidationError("Old password did not match")

        new_password = self.cleaned_data.get('new_password')
        confirm_new_password = self.cleaned_data.get('confirm_new_password')
        if confirm_new_password and new_password != new_password:
            raise forms.ValidationError("Passwords did not match")
        return self.cleaned_data


class NewsAdditionaFieldAdmin(forms.ModelForm):
    weight = forms.ChoiceField(choices = ((1, 'A'), (2, 'Z'), (3, 'B')))
'''def clean_picture(self):
        CONTENT_TYPES = ['jpg', 'jpeg', 'png', 'pdf']
        MAX_UPLOAD_SIZE = 1024 * 1024 * 2
        content = self.cleaned_data['picture']
        if content:
            content_type = content.content_type.split('/')[1]
            if content_type in CONTENT_TYPES:
                if content._size > MAX_UPLOAD_SIZE:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(content._size)))
            else:
                raise forms.ValidationError(_('Please choose image file format.'))
            return content
'''


class VerifyForm(forms.Form):
    email = forms.EmailField(required=True)
