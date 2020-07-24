from django.contrib.auth.models import User
from donate.models import *
from django import forms
from events.models import State	

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

        
