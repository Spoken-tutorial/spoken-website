from config import TARGET, CHANNEL_ID, CHANNEL_KEY, EXPIRY_DAYS
from .helpers import PURPOSE
from django.shortcuts import render
from creation.models import FossCategory, Language
from cms.models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.context_processors import csrf
from donate.forms import PayeeForm, TransactionForm
from donate.models import *
from cms.views import create_profile, send_registration_confirmation
from django import forms
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView
from certificate.views import _clean_certificate_certificate
from django.urls import reverse_lazy
from cdcontent.forms import CDContentForm
from cdcontent.views import internal_computation
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from datetime import datetime
from datetime import timedelta, date
from events import display
import requests
import json
from string import Template
import subprocess
import os
from events.models import AcademicKey
import random
from datetime import date

@csrf_exempt
def donatehome(request):
    form = PayeeForm(initial={'country': 'India'})
    if request.method == 'POST':
        type = request.POST.get("type", "")
        amount = request.POST.get("amount", "")
        if type == 'initiate':
            form.fields['amount'].widget = forms.NumberInput(attrs={'min': amount, 'step': 50.00})
            form.initial = {'amount': amount}
    else:
        form = PayeeForm(initial={'country': 'India', 'amount': 50.00})
        form.fields['amount'].widget = forms.NumberInput(attrs={'min': 50.00, 'step': 50.00})

    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'donate/templates/cd_payment_success.html', context)


@csrf_exempt
def form_valid(request, form):
    """
    If the form is valid, save the associated model.
    """
    form_data = form.save(commit=False)
    form_data.user = request.user
    form_data.status = 0
    form_data.expiry = calculate_expiry()
    form_data.save()
    payee_obj = form_data

    foss_ids = form.cleaned_data.get('foss_id')
    languages = form.cleaned_data.get('language_id')
    level_ids = form.cleaned_data.get('level_id')
    
    fosses = foss_ids.split(',')
    foss_languages = languages.split(',|')
    levels = level_ids.split(',')

    payee_id = payee_obj.pk

    for i in range(len(fosses)):
        foss_category = FossCategory.objects.get(pk=int(fosses[i]))
        foss_level = Level.objects.get(pk=int(levels[i]))
        languages = foss_languages[i].split(',')
        for language in languages:
            if language != '':
                foss_language = Language.objects.get(pk=int(language))
                
                
                cd_foss_langs = CdFossLanguages()
                cd_foss_langs.payment = Payee.objects.get(pk=payee_id)
                cd_foss_langs.foss = foss_category
                cd_foss_langs.lang = foss_language
                if int(foss_level.id):
                    cd_foss_langs.level = foss_level
                cd_foss_langs.save()

    form.save_m2m()

    # return super(PaymentController, self).form_valid(form)


@csrf_exempt
def form_invalid(request, form):
    """
    If the form is invalid, re-render the context data with the
    data-filled form and errors.
    """
    messages.warning(request, 'Invalid form payment request.')
    return redirect('cdcontent:cdcontenthome')


@csrf_exempt
def controller(request):    
    form = PayeeForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            form_valid(request, form)
        else:
            form_invalid(request, form)
    data = get_final_data(request, form)
    return render(request, 'payment_status.html', data)


@csrf_exempt
def calculate_expiry():
    return date.today() + timedelta(days=EXPIRY_DAYS)

@csrf_exempt
def encrypted_data(request, form):
    STdata = ''
    user_name = form.cleaned_data.get('name')
    #amount = form.cleaned_data.get('amount')   
    amount = 1.00
    purpose = PURPOSE + str(form.save(commit=False).pk)
    STdata = str(request.user.id) + str(user_name) + str(amount) + purpose + CHANNEL_ID + CHANNEL_KEY
    
    s = display.value(str(STdata))
    return s


@csrf_exempt
def get_final_data(request, form):

    data = {
        'userId': request.user.id,
        'name': form.cleaned_data.get('name'),
        #    'amount':form.cleaned_data.get('amount'),
        'amount': 1.00,
        'purpose': PURPOSE + str(form.save(commit=False).pk),
        'channelId': CHANNEL_ID,
        'target': TARGET,
        'random': encrypted_data(request, form)
    }
    return data


@csrf_protect
def send_onetime(request):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    from django.core.validators import EmailValidator
    
    context = {}
    user_name = request.POST.get('username')
    email = request.POST.get('email')
    temp = user_name.split(" ")
    password = ''

    try:
        fname, lname = temp[0], temp[1]
    except:
        fname, lname = user_name, ""
    # validate email
    try:
        validate_email( email )
        context['email_validation']=""
        context['valid_email']='1'
    except ValidationError as e:
        context['valid_email']='0'
        try:
            context['email_validation']=e.messages[0]
        except:
            context['email_validation']="Please Enter Valid Email"
    try:
        user = User.objects.get(email=email)
        if user.is_active:
            context['message'] = "active_user"
        else:
            send_registration_confirmation(user)
            context['message'] = "inactive_user"
    except MultipleObjectsReturned as e:
        pass
    except ObjectDoesNotExist:
        user = User.objects.create_user(email, email, password)
        user.first_name = fname
        user.last_name = lname
        user.is_active = False
        user.password = fname+'@ST'+str(random.random()).split('.')[1][:5]
        user.save()
        create_profile(user, '')
        send_registration_confirmation(user)
        print("sent 1st mail")
        context['message'] = "new"

    return HttpResponse(json.dumps(context), content_type='application/json')



@csrf_protect
def validate_user(request):
    print(request.POST)
    context = {}
    user_name = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    if email and password:
        user = authenticate(username=email, password=password)
        print(user)
        if user is not None:
            error_msg = ''
            if user.is_active:
                login(request, user)
                print("user logged in------")

                try:
                    idcase = AcademicKey.objects.get(academic_id=request.user.organiser.academic_id)
                    today = date.today()
                    expiry_date = idcase.expiry_date
                    if expiry_date >= today  :
                        context['organizer_paid'] = '1'
                    else:
                        context['organizer_paid'] = '0'
                except :
                    context['organizer_paid'] = '0'

            else:
                error_msg = "Your account is disabled.<br>\
                            Kindly activate your account by clicking on the activation link which has been sent to your registered email %s.<br>\
                            In case if you do not receive any activation mail kindly verify and activate your account from below link :<br>\
                            <a href='https://spoken-tutorial.org/accounts/verify/'>https://spoken-tutorial.org/accounts/verify/</a>"% (user.email)
                print(error_msg)                
        else:
            error_msg = 'Invalid username / password'
            print(error_msg)
    else:
        error_msg = 'Please enter username and Password'
        print(error_msg)
    
    context['error_msg']=error_msg
    return HttpResponse(json.dumps(context), content_type='application/json')


@csrf_exempt
def validate(request):
    print("Trying to validate user")
    context = {}
    user_pass = request.POST.get("otp")
    email = request.POST.get("email")
    user = User.objects.get(email=email)
    profile = Profile.objects.get(user=user)
    print(profile.confirmation_code, " - ", user_pass)
    if profile.confirmation_code == user_pass:
        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        context['validate'] = "success"
        print("user is :",request.user)
    else:
        context["validate"] = "fail"
    return HttpResponse(json.dumps(context), content_type='application/json')


def receipt(request):
    print("Yes :",request.POST)
    response = HttpResponse(content_type='application/pdf')
    file_name = request.POST.get("name")
    
    try:
        download_file_name = None
        template = 'receipt_template'
        download_file_name = "ST_"+request.POST.get("name")+'.pdf'
        certificate_path = os.path.dirname(os.path.realpath(__file__))+"/receipt/"
        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(
            image_dir = certificate_path+"images/",
            name = request.POST.get("name"),
            amount = request.POST.get("amount"),
            reqId = request.POST.get("reqId"),
            transId = request.POST.get("transId"),
            refNo = request.POST.get("refNo"),
            provId = request.POST.get("provId"),
            status = request.POST.get("status"),
            msg = request.POST.get("msg"),
            key = request.POST.get("key"),
            expiry = request.POST.get("expiry"),
            email = request.POST.get("email"))
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        out = certificate_path
        
        subprocess.run(['pdflatex','--output-directory',certificate_path,certificate_path+file_name+'.tex'])
        pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'rb')
        response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
        response.write(pdf.read())
        _clean_certificate_certificate(certificate_path, file_name)
        return response
    except Exception as e:
        print("error is ",e)

    return response
