from django.contrib.auth.models import User
from donate.models import *
from django import forms
from events.models import State
import phonenumbers
from django.core.validators import EmailValidator

class PayeeForm(forms.ModelForm):
    state = forms.ModelChoiceField(
            widget = forms.Select(attrs = {'class' : 'ac-state'}),
            queryset = State.objects.order_by('name'),
            empty_label = "--- Select State ---", 
            help_text = "",
            required=False,
            )

    foss_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    language_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    level_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    class Meta:
        model = Payee
        fields = ['name', 'email', 'state', 'gender', 'amount']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Please enter your name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Your email id'})
        #self.fields['country'].widget.attrs.update({'class': 'form-control'})
        #self.fields['country'].initial = 'India'
        self.fields['state'].widget.attrs.update({'class': 'form-control'})
        self.fields['gender'].widget.attrs.update({'class': 'form-control'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control'})
        
        if user:
            if user.is_authenticated:
                self.fields['email'].initial = user.email
                self.fields['email'].widget.attrs['readonly'] = True
                self.fields['name'].initial = user.get_full_name()



class TransactionForm(forms.ModelForm):

    name = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )    
    email = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    country = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    key = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    expiry = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    user = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required = False,
    )
    amount = forms.CharField(
                    widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                        )
    reqId = forms.CharField(
                        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                            )
    transId = forms.CharField(
                            widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                                )
    refNo = forms.CharField(
                                widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                                    )
    provId = forms.CharField(
                                    widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                                        )
    msg = forms.CharField(
                                        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                                            )
    selected_foss = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)
    status = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)
   
    class Meta(object):
        model = PaymentTransaction
        exclude = ['created','updated']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        pass

class DonateForm(forms.ModelForm):
    class Meta:
        model = DonationPayee
        fields = ['name','email','gender','contact','country','address','amount']
        widgets = {
          'address': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
        labels = {
        "amount": "Amount (INR - Indian Rupees)",
        "contact": "Mobile Number"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].required = False


class GoodiesForm(forms.ModelForm):



    amount = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    class Meta:
        model = Goodies
        fields = ['name','email','gender','contact','address','item','country','size','amount']
        widgets = {
          'address': forms.Textarea(attrs={'rows':4, 'cols':15}),
        }
        labels = {
        "contact": "Mobile Number"
        }

class DonationTransactionForm(forms.ModelForm):

    name = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    email = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    country = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    key = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    expiry = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    user = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required = False,
    )
    amount = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}),)
    reqId = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    transId = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    refNo = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    provId = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    msg = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    status = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)

    class Meta(object):
        model = DonationTransaction
        exclude = ['created','updated']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        pass


class GoodieTransactionForm(forms.ModelForm):

    name = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    email = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    country = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    key = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    expiry = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    user = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required = False,
    )
    amount = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}),)
    reqId = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    transId = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    refNo = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    provId = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    msg = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    status = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)
    status = forms.CharField(
        widget=forms.HiddenInput(),
        required=False)

    class Meta(object):
        model = GoodiesTransaction
        exclude = ['created','updated']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()

        
class SchoolDonationForm(forms.ModelForm):
    class Meta:
        model = SchoolDonation
        fields = ['name', 'email', 'contact', 'state', 'city', 'address', 'amount', 'note']

class AcademicSubscriptionForm(forms.Form):
    institute = forms.ModelMultipleChoiceField(queryset=AcademicCenter.objects.all().order_by('institution_name'))
    state = forms.ModelChoiceField(queryset=State.objects.all().order_by('name'),
                                   empty_label='----Select State----')
    email = forms.EmailField(validators=[EmailValidator(message="Enter a valid email address.")], required=False)
    name = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=20)
    
    class Meta:
        model = AcademicSubscription
        fields = ['name','email', 'state',  'phone', 'institute']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['name'].initial = f"{user.first_name} {user.last_name}"
            self.fields['email'].initial = f"{user.email}"
    
    def clean_phone(self):
        value = self.cleaned_data.get('phone')
        try:
            phone = phonenumbers.parse(value, "IN") #default to +91 if no country code is provided
            if not phonenumbers.is_valid_number(phone):
                raise forms.ValidationError("Enter a valid phone number.")
        except phonenumbers.NumberParseException:
            raise forms.ValidationError("Enter a valid phone number")
        return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
