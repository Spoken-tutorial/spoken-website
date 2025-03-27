from config import TARGET, CHANNEL_ID, CHANNEL_KEY, EXPIRY_DAYS
from .helpers import PURPOSE
from django.shortcuts import render
from django.conf import settings
from creation.models import FossCategory, Language
from cms.models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.template.context_processors import csrf
from donate.forms import PayeeForm, TransactionForm
from donate.models import *
from cms.views import create_profile, email_otp,send_registration_confirmation
from django import forms
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView
from certificate.views import _clean_certificate_certificate
from django.urls import reverse_lazy
from cdcontent.forms import CDContentForm
from cdcontent.views import internal_computation,is_organizer_paid
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
from training.views import reg_success
from .models import *
from .forms import *
from .subscription import get_request_headers, get_display_transaction_details, verify_hmac_signature
from donate.payment import save_ilw_hdfc_success_data, save_ilw_hdfc_error_data, get_ilw_session_payload, make_hdfc_session_request
from training.models import TrainingEvents
from decimal import Decimal, InvalidOperation
# @csrf_exempt
# def donatehome(request):
#     form = PayeeForm(initial={'country': 'India'})
#     if request.method == 'POST':
#         type = request.POST.get("type", "")
#         amount = request.POST.get("amount", "")
#         if type == 'initiate':
#             form.fields['amount'].widget = forms.NumberInput(attrs={'min': amount, 'step': 50.00})
#             form.initial = {'amount': amount}
#     else:
#         form = DonateForm(initial={'country': 'India', 'amount': 50.00})
#         form.fields['amount'].widget = forms.NumberInput(attrs={'min': 50.00, 'step': 50.00})

#     context = {
#         'form': form
#     }
#     context.update(csrf(request))
#     # return render(request, 'donate/templates/cd_payment_success.html', context)
#     return render(request, 'donate/donate.html', context)

@csrf_exempt
def donatehome(request):
    form = DonateForm()
    if request.method == 'POST':
        type = request.POST.get("type", "")
        amount = request.POST.get("amount", "")
        if type == 'initiate':
            form.fields['amount'].widget = forms.NumberInput(attrs={'min': amount, 'step': 50.00})

            form.initial = {'amount': amount}        
    else:
        initial = {'amount': 500}
        form = DonateForm(initial = initial)
    context = {
        'form': form
    }
    context.update(csrf(request))
    # return render(request, 'donate/templates/cd_payment_success.html', context)
    return render(request, 'donate/donate.html', context)

@csrf_exempt
def purchase(request):
    form = GoodiesForm()
    if request.method == 'POST':
        type = request.POST.get("type", "")
        amount = request.POST.get("amount", "")
        if type == 'initiate':
            form.fields['amount'].widget = forms.NumberInput(attrs={'min': amount, 'step': 50.00})
            form.initial = {'amount': amount}
    else:
        initial = {'amount': 1000}
        form = GoodiesForm(initial=initial)
    context = {
        'form': form
    }
    context.update(csrf(request))
    # return render(request, 'donate/templates/cd_payment_success.html', context)
    return render(request, 'donate/purchase.html', context)

@csrf_exempt
def pay_now(request, purpose):
    if request.method=='POST':
        if 'Donate' in purpose:
            form = DonateForm(request.POST)
        if 'Goodie' in purpose:
            form = GoodiesForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.reqId = CHANNEL_ID+str(display.value(datetime.now().strftime('%Y%m%d%H%M%S'))[0:20])
            obj = form.save()
            data = get_final_data(request, obj, purpose)
        else:
            messages.errors(request,'Invalid Form')
    return render(request, 'payment_status.html', data)

@csrf_exempt
def form_valid(request, form, purpose):
    """
    This method saves the Payee & CdFossLanguages records.
    Payee record is used to store payment information.
    CdFossLanguages record stores mapping of user and foss which the user is eligible to download.
    """
    # Save Payee record
    form_data = form.save(commit=False)
    # form_data.reqId = CHANNEL_ID+str(display.value(datetime.now().strftime('%Y%m%d%H%M%S'))[0:20])
    form_data.reqId = ''
    form_data.user = request.user
    form_data.status = 0
    form_data.expiry = calculate_expiry()
    form_data.purpose = purpose
    source = request.POST.get('source')
    if source == 'deet':
        form_data.source = 'deet'
    form_data.save()
    payee_obj = form_data
    # Save CdFossLanguages record
    if purpose == "cdcontent":
        fosses = form.cleaned_data.get('foss_id').split(',')
        foss_languages = form.cleaned_data.get('language_id').split(',|')
        levels = form.cleaned_data.get('level_id').split(',')

        foss_level = 0
        
        for i in range(len(fosses)):
            foss_category = FossCategory.objects.get(pk=int(fosses[i]))
            if int(levels[i]):
                foss_level = Level.objects.get(pk=int(levels[i]))
            
            languages = foss_languages[i].split(',')
            try:
                custom_lang = request.POST.get('foss_language')
                languages = languages + [str(custom_lang)]
            except:
                # this is coming from Events' page
                pass
            for language in languages:
                if language not in ('','None'):
                    foss_language = Language.objects.get(pk=int(language))
                    cd_foss_langs = CdFossLanguages()
                    cd_foss_langs.payment = Payee.objects.get(pk=payee_obj.pk)
                    cd_foss_langs.foss = foss_category
                    cd_foss_langs.lang = foss_language
                    if foss_level:
                        cd_foss_langs.level = foss_level
                    cd_foss_langs.save()
    else: #for ilw
        event_id = request.POST.get('event')
        event = TrainingEvents.objects.get(id=event_id)
        fosses = event.course.foss.all()
        foss_language = request.POST.get('foss_language',None)

        entries = [ CdFossLanguages(payment=payee_obj, foss=foss, lang=event.Language_of_workshop) for foss in fosses ]
        if foss_language:
            entries += [ CdFossLanguages(payment=payee_obj, foss=foss, lang=event.Language_of_workshop) for foss in fosses ]
        CdFossLanguages.objects.bulk_create(entries)

    form.save_m2m()
    return payee_obj

@csrf_exempt
def form_invalid(request, form):
    """
    If the form is invalid, re-render the context data with the
    data-filled form and errors.
    """
    
    messages.warning(request, 'Invalid form payment request.')
    return redirect('cdcontent:cdcontenthome')


@csrf_exempt
def controller(request, purpose):
    form = PayeeForm(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():
            # form_valid function creates Payee & CdFossLanguages records.
            # & returns Payee record
            payee_obj_new = form_valid(request, form, purpose)
        else:
            form_invalid(request, form)
    
    if purpose != 'cdcontent': # purpose = event_id in case of ILW
        participant_form = reg_success(request, 'general') 
        participant_form.payment_status = payee_obj_new
        try :
            participant_form.save()
        except :
            return redirect('training:list_events', status='myevents')
    data = get_final_data(request, payee_obj_new, purpose)
    if payee_obj_new.source == 'deet':
        callbackurl = request.POST.get('callbackurl')
        json = {'id': f'p{payee_obj_new.id}', 'name': payee_obj_new.name,
                 'email':payee_obj_new.email, 'paid college': False,
                 'amount': payee_obj_new.amount, 'status': 0}
        requests.post(callbackurl, json)

    if purpose == 'cdcontent':
        return render(request, 'payment_status.html', data)
    else:
    #instead of redirecting to payment_status and starting the payment process, start hdfc transaction steps
    #hdfc session request
        payee_email = payee_obj_new.email
        headers = get_request_headers(payee_email)
        payload = get_ilw_session_payload(request,payee_obj_new, participant_form)
        payment_link = make_hdfc_session_request(payee_obj_new, headers, payload)
        if payment_link is not None:
            return redirect(payment_link)
        else:
            return redirect('training:list_events', status='myevents')
    # return render(request, 'payment_status.html', data)


@csrf_exempt
def calculate_expiry():
    return datetime.now() + timedelta(days = EXPIRY_DAYS)


@csrf_exempt
def encrypted_data(request, obj, purpose):
    userId = "0" if purpose == "school_donation" else str(request.user.id)
    STdata = ''
    user_name = obj.name
    amount = obj.amount
    purpose = purpose+"NEW"+str(obj.pk)
    request_id = obj.reqId
    STdata =  request_id + userId + str(user_name) + str(amount) + purpose + CHANNEL_ID + CHANNEL_KEY
    s = display.value(str(STdata))
    return s


@csrf_exempt
def get_final_data(request, obj, purpose):
    userId = "0" if purpose == "school_donation" else str(request.user.id)
    data = {
        'reqId' :  obj.reqId,
        'userId': userId,
        'name': obj.name,
        'amount': obj.amount,
        'purpose': purpose+"NEW"+str(obj.pk) ,
        'channelId': CHANNEL_ID,
        'target': TARGET,
        'random': encrypted_data(request, obj, purpose)
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
    
    try:
        fname, lname = temp[0], temp[1]
    except:
        fname, lname = user_name, ""
    password = fname+'@ST'+str(random.random()).split('.')[1][:5]
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
        user.save()
        create_profile(user, '')
        email_otp(user)
        context['message'] = "new"

    return HttpResponse(json.dumps(context), content_type='application/json')



@csrf_exempt
def validate_user(request):
    context = {}
    user_name = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    if email and password:
        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                msg = ''
                context['organizer_paid'] = is_organizer_paid(request)
            else:
                msg = "Your account is disabled.<br>\
                            Kindly activate your account by clicking on the activation link which has been sent to your registered email %s.<br>\
                            In case if you do not receive any activation mail kindly verify and activate your account from below link :<br>\
                            <a href='https://spoken-tutorial.org/accounts/verify/'>https://spoken-tutorial.org/accounts/verify/</a>"% (user.email)                
        else:
            msg = 'Invalid username / password'
    else:
        msg = 'Please enter username and Password'
    
    context['msg']=msg
    return HttpResponse(json.dumps(context), content_type='application/json')


@csrf_exempt
def validate(request):
    context = {}
    user_pass = request.POST.get("otp")
    email = request.POST.get("email")
    user = User.objects.get(email=email)
    profile = Profile.objects.get(user=user)
    if profile.confirmation_code == user_pass:
        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        context['validate'] = "success"
    else:
        context["validate"] = "fail"
    return HttpResponse(json.dumps(context), content_type='application/json')

def receipt(request):
    response = HttpResponse(content_type='application/pdf')
    file_name = request.POST.get("name").split(" ")[0]
    
    try:
        download_file_name = None
        template = 'receipt_template'
        download_file_name = "ST_" + file_name + '.pdf'
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
            expiry = request.POST.get("expiry"),
            email = request.POST.get("email"))
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        out = certificate_path
        command = 'user_receipt'
        process = subprocess.Popen('make -C {0} {1} file_name={2}'.format(certificate_path, command, file_name),
            stderr=subprocess.PIPE, shell=True)
        
        err = process.communicate()[1]
        if process.returncode == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'rb')
            response['Content-Disposition'] = 'attachment; \
                        filename=%s' % (download_file_name)
            response.write(pdf.read())
            clean_process = subprocess.Popen('make -C {0} clean file_name={1}'.format(
                certificate_path, file_name), shell=True)
            return response
    except Exception as e:
        print("error is ",e)

    return response

@csrf_exempt
def school_donation(request):
    if request.method == 'POST':
        form = SchoolDonationForm(request.POST)
        if form.is_valid():
            #prepare data for donation gateway
            donation = form.save(commit=False)
            reqId = CHANNEL_ID + str(display.value(datetime.now().strftime('%Y%m%d%H%M%S'))[0:20])
            donation.reqId = reqId
            donation.save()
            purpose = "school_donation"
            data = get_final_data(request, donation, purpose)
            try:
                return render(request, 'payment_status.html', data)
            except Exception as e:
                form.add_error(None, 'An error occurred. Please try again later.')
                return render(request, 'donate/school_donation.html', {'form': form})
    else:
        form = SchoolDonationForm()
    return render(request, 'donate/school_donation.html', {'form': form})


@csrf_exempt
def ilw_payment_callback(request):
    context = {}
    status_template = 'spoken/templates/ilw_payment_status.html'
    order_id = request.POST.get('order_id')
    if not order_id:
        raise Http404
    
    payee = Payee.objects.get(transaction__order_id=order_id)
    context['order_id'] = order_id
    try:
        order_status_url = f"{settings.ORDER_STATUS_URL}{order_id}"
        # order status api
        headers = get_request_headers(payee.email)
        try:
            response = requests.get(order_status_url, headers=headers)
            response_data = response.json()
        except requests.exceptions.RequestException as e:
            context['status'] = 'FAILED'
            return render(request, status_template, context=context)
        if response.status_code == 200:
            verified = verify_hmac_signature(request.POST)
            if not verified:
                context['status'] = 'FAILED'
                return render(request, status_template, context=context)
            save_ilw_hdfc_success_data(order_id, response_data)
            data = get_display_transaction_details(response_data)
            data['udf5'] = response_data.get('udf5', '')
            context['data'] = data
            order_status = response_data.get('status', '')
            amount = response_data.get('amount', '')
            if order_status == 'CHARGED':
                try:
                    amount_decimal = Decimal(str(amount))
                except InvalidOperation:
                    context['status'] = 'FAILED'
                    return render(request, status_template, context=context)
                if amount_decimal == payee.amount:
                    context['status'] = 'CHARGED'
                else:
                    context['status'] = 'FAILED'
                    save_ilw_hdfc_error_data(order_id, response_data, msg="Amount mismatch")
            elif order_status == 'PENDING_VBV' or order_status == 'AUTHORIZING': #This is a non-terminal transaction status. Show pending screen/polling
                context['status'] = 'PENDING'
            else:
                context['status'] = 'FAILED'
            return render(request, status_template, context=context)
        else:
            save_ilw_hdfc_error_data(order_id, response_data)  
            context['status'] = 'FAILED'
    except Exception as e:
        context['status'] = 'FAILED'
    return render(request, status_template, context=context) # return to payment page site