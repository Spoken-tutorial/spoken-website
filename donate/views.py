from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template.context_processors import csrf
from donate.forms import PayeeForm
from donate.models import *
from django import forms
from django.views.decorators.csrf import csrf_protect,csrf_exempt

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
    return render(request, 'donate/templates/donate_home.html', context)

@csrf_protect
def initiate_payment(request):
    print(request.POST)
    payee = request.POST.get("Payee")
    country = request.POST.get("Country")
    state = request.POST.get("State")
    email = request.POST.get("Email")
    amount = request.POST.get("Amount")
    gender = request.POST.get("Gender")
    fosses = request.POST.get("FOSS")
    languages = request.POST.get("Language")
    
    # newpayee = Payee()
    # newpayee.name  =  payee
    # newpayee.country  =  country
    # newpayee.state  =  state
    # newpayee.amount  =  amount
    # newpayee.email  = email
    # newpayee.gender  = gender
    # newpayee.foss  =  foss
    # newpayee.language  =  languages
    # newpayee.status  =  1
    # newpayee.key  =  uuid or hash 
    # newpayee.save()

    form = PayeeForm(initial={'country': 'India'})
    context = {
        'form': form
    }

    return render(request, 'donate/templates/donate_home.html', context)
