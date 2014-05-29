from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.utils import timezone
from django.http import Http404
from cms.models import *
from cms.forms import *
import random, string

def dispatcher(request, permalink=''):
    if permalink == '':
        permalink = 'home'
    page_content = get_object_or_404(Page, permalink=permalink)
    context = {
        'page': page_content,
    }
    return render_to_response('cms/templates/page.html', context)

def account_register(request):
    context = {}
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
            user = User.objects.create_user(username, email, password)
            user.is_active = False
            user.save()
            confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
            p = Profile(user=user, confirmation_code=confirmation_code)
            p.save()
            send_registration_confirmation(user)
            return HttpResponseRedirect('/')
        context = {'form':form}
        return render_to_response('cms/templates/register.html', context, context_instance = RequestContext(request))
    else:
        form = RegisterForm()
        context = {
            'form': form
        }
        context.update(csrf(request))
        return render_to_response('cms/templates/register.html', context)

def send_registration_confirmation(user):
    p = Profile.objects.get(user=user)
    #user.email = "k.sanmugam2@gmail.com"
    # Sending email when an answer is posted
    subject = 'Account Notification'
    message = """
        Dear {0}\n
        Click this link to activate your account <b>"{1}"</b>\n\n
        Regards,<br>\n
        Spoken Tutorial
    """.format(
        "sanmugam",
        "http://beta.spoken-tutorial.org/accounts/confirm/" + str(p.confirmation_code) + "/" + user.username
    )

    email = EmailMultiAlternatives(
        subject,'', '',
        [user.email],
        headers={"Content-type":"text/html;charset=iso-8859-1"}
    )

    email.attach_alternative(message, "text/html")
    result = email.send(fail_silently=True)

def confirm(request, confirmation_code, username):
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        #if profile.confirmation_code == confirmation_code and user.date_joined > (timezone.now()-timezone.timedelta(days=1)):
        if profile.confirmation_code == confirmation_code:
            user.is_active = True
            user.save()
            user.backend='django.contrib.auth.backends.ModelBackend' 
            login(request,user)
            messages.success(request, "Your account has been activated!. Please update your profile to complete your registration")
            return HttpResponseRedirect('/accounts/profile/'+user.username)
        else:
            messages.success(request, "Something went wrong!. Please try again!")
            return HttpResponseRedirect('/')
    except Exception, e:
        messages.success(request, "Your account not activated!. Please try again!")
        return HttpResponseRedirect('/')

def account_login(request):
    user = request.user
    error_msg = ''
    if request.user.is_anonymous():
        form = LoginForm()
        context = {
            'form' : form
        }
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if user_has_profile(user):
                        if request.GET and request.GET['next']:
                            return HttpResponseRedirect(request.GET['next'])
                        return HttpResponseRedirect('/')
                    messages.success(request, "Please update your profile!")
                    return HttpResponseRedirect('/accounts/profile/'+user.username)
                else:
                    error_msg = 'Your account is disabled.'
            else:
                error_msg = 'Invalid username / password'
                messages.error(request, error_msg)
                return render(request, 'cms/templates/login.html', context)
        context.update(csrf(request))
        if error_msg:
            messages.error(request, error_msg)
        return render_to_response('cms/templates/login.html', context)
    return HttpResponseRedirect('/')

def account_logout(request):
    context = RequestContext(request)
    logout(request)
    return HttpResponseRedirect('/')

def account_profile(request, username):
    #todo: validation
    #todo: store location, state and etc.. ids
    if request.method == 'POST':
        user = User.objects.get(username=username)
        form = ProfileForm(request.POST, user = request.user, instance = Profile.objects.get(user = user))
        if form.is_valid():
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.save()
            
            profile = Profile.objects.get(user=user)
            profile.street = request.POST['street']
            profile.location_id = request.POST['location']
            profile.district_id = request.POST['district']
            profile.city_id = request.POST['city']
            profile.state_id = request.POST['state']
            profile.country = request.POST['country']
            profile.pincode = request.POST['pincode']
            profile.phone = request.POST['phone']
            profile.save()
            if user_has_profile(user):
                messages.success(request, "Your profile has been updated!")
                return HttpResponseRedirect("/")
            return HttpResponseRedirect("/accounts/profile/"+username+"/")
        
        context = {'form':form}
        return render_to_response('cms/templates/profile.html', context, context_instance = RequestContext(request))
    #if username:
    #    try:
    user = User.objects.get(username=username)
    context = {}
    context['form'] = ProfileForm(user = request.user, instance = Profile.objects.get(user = user))
    context.update(csrf(request))
    return render(request, 'cms/templates/profile.html', context)
    #    except:
    #        raise Http404('Page not found')
    #else:
    #    raise Http404('Page not found')

def user_has_profile(user):
    try:
        p = Profile.objects.get(user_id = user.id)
        if not p.street or not p.state or not p.district or not p.location or not p.country:
            return False
        return True
    except Exception, e:
        print "************"
        print e
