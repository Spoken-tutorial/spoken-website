from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.http import Http404
from cms.models import *
from cms.forms import *
from PIL import Image
import random, string

def dispatcher(request, permalink=''):
    if permalink == '':
        permalink = 'home'
    page_content = get_object_or_404(Page, permalink=permalink)
    context = {
        'page': page_content,
    }
    return render(request, 'cms/templates/page.html', context)

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
            messages.success(request, """
                Please confirm your registration by clicking on the activation link which has been sent to your registered email id.
            """)
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
    subject = 'Account Active Notification'
    message = """Dear {0},

Thank you for registering at {1}. You may activate your account by clicking on this link or copying and pasting it in your browser
{2}

Regards,
Admin
Spoken Tutorials
IIT Bombay.
    """.format(
        user.username,
        "http://spoken-tutorial.org",
        "http://spoken-tutorial.org/accounts/confirm/" + str(p.confirmation_code) + "/" + user.username
    )

    email = EmailMultiAlternatives(
        subject, message, 'administrator@spoken-tutorial.org',
        to = [user.email], bcc = [], cc = [],
        headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
    )

    #email.attach_alternative(message, "text/html")
    result = email.send(fail_silently=False)

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
                    try:
                        p = Profile.objects.get(user_id = user.id)
                        if not user.first_name or not user.last_name or not p.country or not p.state or not p.district or not p.city  or not p.address or not p.pincode or not p.phone or not p.picture:
                            messages.success(request, "Please update your profile!")
                            return HttpResponseRedirect('/accounts/profile/'+user.username)
                    except: 
                        pass
                    if request.GET and request.GET['next']:
                        return HttpResponseRedirect(request.GET['next'])
                    return HttpResponseRedirect('/')
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
@login_required
def account_logout(request):
    context = RequestContext(request)
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def account_profile(request, username):
    user = request.user
    profile = Profile.objects.get(user_id=user.id)
    old_file_path = settings.MEDIA_ROOT + str(profile.picture)
    new_file_path = None
    if request.method == 'POST':
        form = ProfileForm(user, request.POST, request.FILES, instance = profile)
        if form.is_valid():
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.save()
            form_data = form.save(commit=False)
            form_data.user_id = user.id
            
            # if 'picture-clear' in request.POST and request.POST['picture-clear']:
            #     #if not old_file == new_file:
            #     if os.path.isfile(old_file_path):
            #         os.remove(old_file_path)
            #
            # if 'picture' in request.FILES:
            #     form_data.picture = request.FILES['picture']
            
            form_data.save()
            
            """if 'picture' in request.FILES:
                size = 128, 128
                filename = str(request.FILES['picture'])
                ext = os.path.splitext(filename)[1]
                if ext != '.pdf' and ext != '':
                    im = Image.open(settings.MEDIA_ROOT + str(form_data.picture))
                    im.thumbnail(size, Image.ANTIALIAS)
                    ext = ext[1:]
                    
                    mimeType = ext.upper()
                    if mimeType == 'JPG':
                        mimeType = 'JPEG'
                    im.save(settings.MEDIA_ROOT + "user/" + str(user.id) + "/" + str(user.id) + "-thumb." + ext, mimeType)
                    form_data.thumb = 'user/' + str(user.id)+ '/' + str(user.id) + '-thumb.' + ext
                    form_data.save()"""
            messages.success(request, "Your profile has been updated!")
            return HttpResponseRedirect("/accounts/view-profile/" + user.username)
        
        context = {'form':form}
        return render(request, 'cms/templates/profile.html', context)
    else:
        context = {}
        context.update(csrf(request))
        instance = Profile.objects.get(user_id=user.id)
        context['form'] = ProfileForm(user, instance = instance)
        return render(request, 'cms/templates/profile.html', context)

@login_required
def account_view_profile(request, username):
    user = User.objects.get(username = username)
    profile = Profile.objects.get(user = user)
    context = {
        'profile' : profile,
        'media_url' : settings.MEDIA_URL,
    }
    return render(request, 'cms/templates/view-profile.html', context)

def password_reset(request):
    context = {}
    form = PasswordResetForm()
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            user = User.objects.filter(email=request.POST['email']).first()
            user.set_password(password_string)
            user.save()
            print 'Username => ', user.username
            print 'New password => ', password_string
            #Send email
            subject  = "Spoken Tutorial password reset"
            to = [user.email]
            message = '''Hi {0},

Your account password at 'Spoken Tutorials' has been reset
and you have been issued with a new temporary password.

Your current login information is now:
   username: {1}
   password: {2}

Please go to this page to change your password:
   {3}

In most mail programs, this should appear as a blue link
which you can just click on.  If that doesn't work,
then cut and paste the address into the address
line at the top of your web browser window.

Best Wishes,
Admin
Spoken Tutorials
IIT Bombay.
'''.format(user.username, user.username, password_string, 'http://www.spoken-tutorial.org/accounts/change-password/')

            # send email
            email = EmailMultiAlternatives(
                subject, message, 'administrator@spoken-tutorial.org',
                to = to, bcc = [], cc = [],
                headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
            )

            result = email.send(fail_silently=False)
            messages.success(request, "New password sent to your email "+user.email)
            return HttpResponseRedirect('/accounts/login/')
            

    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'cms/templates/password_reset.html', context)


@login_required
def change_password(request):
    context = {}
    form = ChangePasswordForm()
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user_id = form.cleaned_data['userid'], confirmation_code = form.cleaned_data['code'])
            user = profile.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            messages.success(request, "Your account password has been updated successfully!")
            return HttpResponseRedirect("/accounts/view-profile/" + user.username)
    context['form'] = form
    context.update(csrf(request))
    return render(request, 'cms/templates/change_password.html', context)
