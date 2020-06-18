from config import TARGET, CHANNEL_ID, CHANNEL_KEY
from .helpers import PURPOSE
from django.shortcuts import render
from creation.models import FossCategory, Language
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template.context_processors import csrf
from donate.forms import PayeeForm, TransactionForm
from donate.models import *
from django import forms
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from cdcontent.forms import CDContentForm
from django.contrib import messages
from datetime import datetime
from datetime import timedelta, date
from events import display
import requests

@csrf_exempt
def donatehome(request):
    form = PayeeForm(initial={'country': 'India'})
    if request.method=='POST':
          type = request.POST.get("type", "")
          amount = request.POST.get("amount", "")
          if type == 'initiate':
               form.fields['amount'].widget = forms.NumberInput(attrs={'min': amount,'step': 50.00})
               form.initial = {'amount': amount}
    else:
        form = PayeeForm(initial={'country': 'India','amount':50.00})
        form.fields['amount'].widget = forms.NumberInput(attrs={'min': 50.00,'step': 50.00})

    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'donate/templates/cd_payment_success.html', context)

class PaymentController(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name = 'cdcontent/templates/cdcontent_home.html'
    model = Payee
    form_class = PayeeForm
    success_url = reverse_lazy('cdcontent:cdcontenthome')

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.status = False
        self.object.expiry = calculate_expiry()
        self.object.save()
        payee_obj = self.object;

        foss_ids = form.cleaned_data.get('foss_id')
        languages = form.cleaned_data.get('language_id')
        fosses = foss_ids.split(',')
        foss_languages = languages.split(',|')

        payee_id = payee_obj.pk
        
        for i in range(len(fosses)):
            foss_category = FossCategory.objects.get(pk=int(fosses[i]))  
            languages = foss_languages[i].split(',')
            for language in languages:
                if language!='':
                    foss_language = Language.objects.get(pk=int(language))
                    cd_foss_langs = CdFossLanguages()
                    cd_foss_langs.payment = Payee.objects.get(pk=payee_id)
                    cd_foss_langs.foss = foss_category
                    cd_foss_langs.lang = foss_language
                    cd_foss_langs.save()

        form.save_m2m()
        pass_details(self, form)
        return super(PaymentController, self).form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        messages.warning(self.request, 'Invalid form payment request.')
        return redirect('cdcontent:cdcontenthome')


def calculate_expiry():
    return date.today() + timedelta(days=7)

def encrypted_data(self, form):
    STdata = ''
    user_name = form.cleaned_data.get('name')
    amount = form.cleaned_data.get('amount')
    STdata = str(self.request.user.id)+str(user_name)+str(amount)+PURPOSE+CHANNEL_ID+CHANNEL_KEY
    print(STdata)
    s = display.value(str(STdata))
    return s

def pass_details(self, form):
    
    data = {
    'userId':self.request.user.id,
    'name':form.cleaned_data.get('name'),
#    'amount':form.cleaned_data.get('amount'),
    'amount':1.00,
    'purpose':PURPOSE,
    'channelId':CHANNEL_ID,
    'random':encrypted_data(self, form)
    }
    r = requests.post(TARGET,data = data)
