# Standard Library
from builtins import str
from builtins import range
import random
import string

# Third Party Stuff
from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
 
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from hashids import Hashids
from PIL import Image

# Spoken Tutorial Stuff
from cms.forms import *
from cms.models import *
from cms.services import *
from events.models import Student
from mdldjango.models import MdlUser
from mdldjango.urls import *
from django.template.context_processors import csrf

def dispatcher(request, permalink=''):
    if permalink == '':
        return HttpResponseRedirect('/')
    
    if permalink == 'project_documents':
        impersonating = request.session.pop('_impersonate', None)
        if impersonating is not None:
            from impersonate.signals import session_end
            request.session.modified = True
            session_end.send(
                sender=None,
                impersonator=request.impersonator,
                impersonating=impersonating,
                request=request
            )
            return HttpResponseRedirect('/accounts/login/?next=/project_documents/')
        if not request.user.groups.filter(name ='page_admin').exists():
            messages.error(request, "You are not authorized to access this page. Please login as an authorized user.")
            return HttpResponseRedirect('/accounts/login/?next=/project_documents/')

    page_content = get_object_or_404(Page, permalink=permalink, visible=True)
    col_offset = int((12 - page_content.cols) / 2)
    col_remainder = int((12 - page_content.cols) % 2)
    if col_remainder:
        col_offset = str(col_offset) + 'p5'
    context = {
        'page': page_content,
        'col_offset': col_offset,
    }
    return render(request, 'cms/templates/page.html', context)


def create_profile(user, phone):
    confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
    profile = Profile(user=user, confirmation_code=confirmation_code, phone=phone)
    profile.save()
    return profile


def account_register(request):
    # import recaptcha validate function
    from cms.recaptcha import recaptcha_valdation, get_recaptcha_context

    # reCAPTCHA Site key
    context = get_recaptcha_context()

    if request.method == 'POST':

        # verify recaptcha
        #recaptcha_result = recaptcha_valdation(request)

        form = RegisterFormHome(request.POST)
        #if recaptcha_result and form.is_valid():
        if form.is_valid():
            username = request.POST['username'].strip()
            password = request.POST['password'].strip()
            email = request.POST['email'].strip()
            first_name = str(request.POST['first_name'].strip())
            last_name = str(request.POST['last_name'].strip())
            phone = request.POST['phone']
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = False
            user.save()
            create_profile(user, phone)
            send_registration_confirmation(user)
            messages.success(request,
                "Thank you for registering.\
                Please confirm your registration by clicking on the activation link which has been sent to your registered email %s.<br>\
                In case if you do not receive any activation mail kindly verify and activate your account from below link :<br>\
                <a href='https://spoken-tutorial.org/accounts/verify/'>https://spoken-tutorial.org/accounts/verify/</a>"
                 % (email))
            return HttpResponseRedirect('/')
        context['form'] = form
        return render(request, 'cms/templates/register.html', context)
    else:
        form = RegisterFormHome()
        context['form'] = form
        context.update(csrf(request))
        return render(request, 'cms/templates/register.html', context)


def send_registration_confirmation(user):
    p = Profile.objects.get(user=user)
    # user.email = "k.sanmugam2@gmail.com"
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
        "https://spoken-tutorial.org",
        "https://spoken-tutorial.org/accounts/confirm/" + str(p.confirmation_code) + "/" + user.username
    )

    email = EmailMultiAlternatives(
        subject, message, 'no-reply@spoken-tutorial.org',
        to = [user.email], bcc = [], cc = [],
        headers={'Reply-To': 'no-reply@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
    )

    #email.attach_alternative(message, "text/html")
    try:
        result = email.send(fail_silently=False)
    except:
        pass

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
            messages.success(request, "Your account has been activated!. Please update your profile.")
            return HttpResponseRedirect('/')
        else:
            messages.success(request, "Something went wrong!. Please try again!")
            return HttpResponseRedirect('/')
    except Exception as e:
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
            form = LoginForm(request.POST)
            if form.is_valid():
                username = request.POST.get('username', None)
                password = request.POST.get('password', None)
                remember = request.POST.get('remember', None)
                if username and password:
                    user = auth.authenticate(username=username, password=password)
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            if remember:
                                request.session.set_expiry(settings.KEEP_LOGGED_DURATION)
                            else:
                                request.session.set_expiry(0)
                            try:
                                p = Profile.objects.get(user_id = user.id)
                                if not user.first_name or not user.last_name or not p.state or not p.district or not p.city or not p.address or not p.phone:# or not p.pincode or not p.picture:
                                    messages.success(request, "<ul><li>Please update your profile.</li><li>Please make sure you enter your First name, Last name both and with correct spelling.</li><li>It is recommended that you do upload the photo.</li></ul>")
                                    return HttpResponseRedirect('/accounts/profile/'+user.username)
                            except:
                                pass
                            if request.GET and request.GET['next']:
                                return HttpResponseRedirect(request.GET['next'])
                            return HttpResponseRedirect('/')
                        else:
                            error_msg = "Your account is disabled.<br>\
                            Kindly activate your account by clicking on the activation link which has been sent to your registered email %s.<br>\
                            In case if you do not receive any activation mail kindly verify and activate your account from below link :<br>\
                            <a href='https://spoken-tutorial.org/accounts/verify/'>https://spoken-tutorial.org/accounts/verify/</a>"% (user.email)
                    else:
                        error_msg = 'Invalid username / password'
                else:
                    error_msg = 'Please enter username and Password'
                context['form'] = form
                messages.error(request, error_msg)
                return render(request, 'cms/templates/login.html', context)
            else:
                context['form'] = form
        context.update(csrf(request))
        if error_msg:
            messages.error(request, error_msg)
        return render(request, 'cms/templates/login.html', context)
    return HttpResponseRedirect('/')


@login_required
def account_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def account_profile(request, username):
    user = request.user
    try:
      profile = Profile.objects.get(user_id=user.id)
    except:
      profile = create_profile(user)
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

            if 'picture-clear' in request.POST and request.POST['picture-clear']:
               #if not old_file == new_file:
               if os.path.isfile(old_file_path):
                   os.remove(old_file_path)

            if 'picture' in request.FILES:
               form_data.picture = request.FILES['picture']

            form_data.save()

            if 'picture' in request.FILES:
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
                    thumbName = 'user/' + str(user.id)+ '/' + str(user.id) + '-thumb.' + ext
                    im.save(settings.MEDIA_ROOT + thumbName, mimeType)
                    form_data.thumb = thumbName
                    form_data.save()
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
    if username != request.user.username:
        raise PermissionDenied('You are not allowed to view this page!')

    user = User.objects.get(username = username)
    profile = None
    try:
      profile = Profile.objects.get(user = user)
    except:
      profile = create_profile(user)
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

            # change if any mdl user pass too
            from mdldjango.views import changeMdlUserPass
            changeMdlUserPass(request.POST['email'], password_string)

            print(('Username => ', user.username))
            print(('New password => ', password_string))

            if not user.profile_set.first():
                profile = create_profile(user,None)

            changePassUrl = "http://www.spoken-tutorial.org/accounts/change-password"
            if request.GET and request.GET['next']:
                changePassUrl = changePassUrl + "?auto=%s&username=%s&next=%s" % (user.profile_set.first().confirmation_code, user.username, request.GET['next'])

            #Send email
            subject  = "Spoken Tutorial password reset"
            to = [user.email]
            message = '''Hi {0},

Your account password at 'Spoken Tutorials' has been reset
and you have been issued with a new temporary password.

Your current login information is now:
   username: {1}
   password: {2}

With respect to change your password kindly follow the steps written below :

Step 1. Visit below link to change the password. Provide temporary password given above in the place of Old Password field.
	{3}

Step 2.Use this changed password for spoken forum login and in moodle login also.

In most mail programs, this should appear as a blue link
which you can just click on.  If that doesn't work,
then cut and paste the address into the address
line at the top of your web browser window.

Best Wishes,
Admin
Spoken Tutorials
IIT Bombay.
'''.format(user.username, user.username, password_string,changePassUrl)

            # send email
            email = EmailMultiAlternatives(
                subject, message, 'no-reply@spoken-tutorial.org',
                to = to, bcc = [], cc = [],
                headers={'Reply-To': 'no-reply@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
            )

            result = email.send(fail_silently=False)
            # redirect to next url if there or redirect to login page
            # use for forum password rest form
            redirectNext = request.GET.get('next', False)
            if redirectNext:
                return HttpResponseRedirect(redirectNext)
            messages.success(request, "New password sent to your email "+user.email)
            return HttpResponseRedirect('/accounts/change-password/')


    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'cms/templates/password_reset.html', context)


#@login_required
def change_password(request):
    # chacking uselogin
    pcode = request.GET.get('auto', False)
    username = request.GET.get('username', False)
    nextUrl = request.GET.get('next', False)

    # check pcode in profile page
    if pcode and username and nextUrl:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        if profile.confirmation_code == pcode:
            user.backend='django.contrib.auth.backends.ModelBackend'
            login(request,user)

    if request.user.is_anonymous():
        return HttpResponseRedirect('/accounts/login/?next=/accounts/change-password')

    context = {}
    form = ChangePasswordForm()
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user_id = form.cleaned_data['userid'], confirmation_code = form.cleaned_data['code'])
            user = profile.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            # change if any mdl user pass too
            from mdldjango.views import changeMdlUserPass
            changeMdlUserPass(user.email, form.cleaned_data['new_password'])

            if nextUrl:
                return HttpResponseRedirect(nextUrl.split("?", 1)[0])

            messages.success(request, "Your account password has been updated successfully!")
            return HttpResponseRedirect("/accounts/view-profile/" + user.username)
    context['form'] = form
    context.update(csrf(request))
    return render(request, 'cms/templates/change_password.html', context)


def confirm_student(request, token):
    mdluserid = Hashids(salt=settings.SPOKEN_HASH_SALT).decode(token)[0]
    try:
        mdluser = MdlUser.objects.filter(pk=mdluserid).first()
        user = User.objects.get(email=mdluser.email)
        student = Student.objects.get(user_id = user.id)
        if mdluser:
            user.is_active = True
            user.save()

            student.verified = True
            student.error = False
            student.save()

            messages.success(request, "Your account has been activated!. Please login to continue.")
            return HttpResponseRedirect('https://spoken-tutorial.org/participant/login/')
        else:
            print('can not match record')
            messages.error(request, "Your account not activated!. Please try again!")
            return HttpResponseRedirect('/')
    except ObjectDoesNotExist:
        messages.error(request, "Your account not activated!. Please try again!")
        return HttpResponseRedirect('/')


def verify_email(request):
  context = {}
  if request.method == 'POST':
    form = VerifyForm(request.POST)
    if form.is_valid():
      email = form.cleaned_data['email']
      #send verification mail as per the criteria check
      status, msg = send_verify_email(request,email)
      if status:
        messages.success(request, msg, extra_tags='success')
      else:
        messages.error(request, msg, extra_tags='error')
    else:
      messages.error(request, 'Invalid Email ID', extra_tags='error')
  return render(request, "cms/templates/verify_email.html", context)
