# Standard Library
import datetime
import os
import time

# Third Party Stuff
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from forms import *
from get_or_create_participant import check_csvfile, encript_password
from models import MdlUser

# Spoken Tutorial Stuff
from events.forms import OrganiserForm
from events.models import *
from events.signals import get_or_create_user
from events.views import *


def authenticate(email=None, password=None):
    try:
        password = encript_password(password)
        user = MdlUser.objects.filter(email=email, password=password).last()
        print user
        if user:
            return user
    except Exception:
        return None


def mdl_logout(request):
    if 'mdluserid' in request.session:
        del request.session['mdluserid']
        request.session.save()
    # print "logout !!"
    return HttpResponseRedirect('/participant/login')


def mdl_login(request):
    messages = {}
    if request.POST:
        email = request.POST["username"]
        password = request.POST["password"]
        if not email or not password:
            messages['error'] = "Please enter valide Username and Password!"
            # return HttpResponseRedirect('/participant/login')
        user = authenticate(email=email, password=password)
        if user:
            request.session['mdluserid'] = user.id
            request.session['mdluseremail'] = user.email
            request.session['mdlusername'] = user.email
            request.session['mdluserinstitution'] = user.institution
            request.session.save()
            request.session.modified = True
        else:
            messages['error'] = "Username or Password Doesn't match!"

    if request.session.get('mdluserid'):
        # print "Current user is ", request.session.get('mdluserid')
        return HttpResponseRedirect('/participant/index')

    context = {'message': messages}
    context.update(csrf(request))
    return render(request, 'mdl/templates/mdluser_login.html', context)


def index(request):
    mdluserid = request.session.get('mdluserid')
    mdlusername = request.session.get('mdlusername')
    if not mdluserid:
        return HttpResponseRedirect('/participant/login')

    try:
        mdluser = MdlUser.objects.get(id=mdluserid)
    except:
        return HttpResponseRedirect('/participant/login')

    if str(mdluser.institution.encode("utf8")).isdigit():
        academic = None
        try:
            academic = AcademicCenter.objects.get(id=mdluser.institution)
        except:
            pass

        if academic:
            category = int(request.GET.get('category', 4))
            if not (category > 0 and category < 6):
                return HttpResponseRedirect('/participant/index/?category=4')

            upcoming_workshop = None
            upcoming_test = None
            past_workshop = None
            past_test = None
            ongoing_test = None
            if category == 3:
                upcoming_workshop = []
                upcoming_workshop = Training.objects.filter((Q(status=10) | Q(status=11) | Q(status=12) | Q(
                    status=3)), academic_id=mdluser.institution, tdate__lte=datetime.date.today()).order_by('-tdate')
                # up = Training.objects.filter(id=23270)[0]
                # upcoming_workshop.append(up)
                # p = up.trainingattendance_set.get(mdluser_id=mdluser.id)
            if category == 5:
                upcoming_test = Test.objects.filter(
                    status=2, academic_id=mdluser.institution, tdate__gt=datetime.date.today()).order_by('-tdate')
            if category == 1:
                past_workshop = TrainingAttend.objects.filter(
                    student__user__email=mdluser.email).order_by('-training__sem_start_date')
            if category == 2:
                past_test = Test.objects.filter(id__in=TestAttendance.objects.filter(
                    mdluser_id=mdluser.id).values_list('test_id'), status=4).order_by('-tdate')
            if category == 4:
                ongoing_test = Test.objects.filter(Q(status=2) | Q(
                    status=3), academic_id=mdluser.institution, tdate__lte=datetime.date.today()).order_by('-tdate')

            context = {
                'mdluserid': mdluserid,
                'mdlusername': mdlusername,
                'upcoming_workshop': upcoming_workshop,
                'upcoming_test': upcoming_test,
                'past_workshop': past_workshop,
                'past_test': past_test,
                'ongoing_test': ongoing_test,
                'category': category,
                'ONLINE_TEST_URL': settings.ONLINE_TEST_URL

            }
            context.update(csrf(request))
            return render(request, 'mdl/templates/mdluser_index.html', context)

    form = OrganiserForm()
    if request.method == 'POST':
        form = OrganiserForm(request.POST)
        if form.is_valid():
            mdluser.institution = form.cleaned_data['college']
            mdluser.save()
            return HttpResponseRedirect('/participant/index')
    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'mdl/templates/academic.html', context)


@login_required
def offline_details(request, wid, category):
    user = request.user
    wid = int(wid)
    category = int(category)
    # print category
    user = request.user
    form = OfflineDataForm()
    try:
        if category == 1:
            Training.objects.get(pk=wid, status__lt=4)
        elif category == 2:
            Training.objects.get(pk=wid, status__lt=4)
        else:
            raise PermissionDenied('You are not allowed to view this page!')
    except Exception:
        raise PermissionDenied('You are not allowed to view this page!')

    if request.method == 'POST':
        form = OfflineDataForm(request.POST, request.FILES)
        try:
            if category == 1:
                w = Training.objects.get(id=wid)
            elif category == 2:
                w = Training.objects.get(id=wid)
            else:
                raise PermissionDenied('You are not allowed to view this page!')
        except:
            raise PermissionDenied('You are not allowed to view this page!')

        if form.is_valid():
            file_path = settings.MEDIA_ROOT + 'training/' + str(wid) + str(time.time())
            f = request.FILES['xml_file']
            fout = open(file_path, 'wb+')
            for chunk in f.chunks():
                fout.write(chunk)
            fout.close()

            error_line_no = ''
            csv_file_error = 0
            csv_file_error, error_line_no = check_csvfile(user, file_path, w, flag=1)
            os.unlink(file_path)
            # update participant count
            update_participants_count(w)

            if error_line_no:
                messages.error(request, error_line_no)
            # update logs
            if category == 1:
                message = w.academic.institution_name + " has submited Offline " + \
                    w.foss.foss + " workshop attendance dated " + w.tdate.strftime("%Y-%m-%d")
                update_events_log(user_id=user.id, role=2, category=0,
                                  category_id=w.id, academic=w.academic_id, status=5)
                update_events_notification(user_id=user.id, role=2, category=0, category_id=w.id,
                                           academic=w.academic_id, status=5, message=message)
                if not error_line_no:
                    messages.success(
                        request, "Thank you for uploading the Attendance. Now make sure that you cross check and verify the details before submiting.")
                return HttpResponseRedirect('/software-training/workshop/' + str(wid) + '/attendance/')
            else:
                message = w.academic.institution_name + " has submited Offline training attendance."
                update_events_log(user_id=user.id, role=2, category=2,
                                  category_id=w.id, academic=w.academic_id, status=5)
                update_events_notification(user_id=user.id, role=2, category=2, category_id=w.id,
                                           academic=w.academic_id, status=5, message=message)
                if not error_line_no:
                    messages.success(
                        request, "Thank you for uploading the Attendance. Now make sure that you cross check and verify the details before submiting.")
                return HttpResponseRedirect('/software-training/training/' + str(wid) + '/attendance/')
        messages.error(request, "Please Upload CSV file !")
    context = {
        'form': form,
    }
    messages.info(request, """
        Please upload the CSV file which you have generated.
        To know more <a href="http://process.spoken-tutorial.org/images/9/96/Upload_Attendance.pdf" target="_blank">
        Click here</a>.
    """)
    context.update(csrf(request))
    return render(request, 'mdl/templates/offline_details.html', context)


def mdl_register(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                MdlUser.objects.get(email=request.POST['email'])
                messages.success(request, ("Email : " + request.POST['email'] + " already registered on this website. "
                                           "Please click <a href='http://www.spoken-tutorial.org/participant/login/'>"
                                           "here </a>to login"))
            except Exception:
                mdluser = MdlUser()
                mdluser.auth = 'manual'
                mdluser.institution = form.cleaned_data['college']
                mdluser.gender = form.cleaned_data['gender']
                mdluser.firstname = form.cleaned_data['firstname'].upper()
                mdluser.lastname = form.cleaned_data['lastname'].upper()
                mdluser.email = form.cleaned_data['email'].lower()
                mdluser.username = mdluser.email
                mdluser.password = encript_password(form.cleaned_data['password'])
                mdluser.confirmed = 1
                mdluser.mnethostid = 1
                mdluser.save()
                mdluser = MdlUser.objects.get(email=mdluser.email)
                get_or_create_user(mdluser, form.cleaned_data['password'])
                messages.success(request, "User " + form.cleaned_data['firstname'] + " " + form.cleaned_data[
                                 'lastname'] + " Created!. Please click <a href='http://www.spoken-tutorial.org/participant/login/'>here </a>to login")
                return HttpResponseRedirect('/participant/register/')

    context = {}
    context['form'] = form
    context.update(csrf(request))
    return render(request, 'mdl/templates/register.html', context)


def feedback(request, wid):
    mdluserid = request.session.get('mdluserid')
    mdlusername = request.session.get('mdlusername')
    if not mdluserid:
        return HttpResponseRedirect('/participant/login')

    form = FeedbackForm()
    mdluserid = request.session.get('mdluserid')
    if not mdluserid:
        return HttpResponseRedirect('/participant/login')
    w = None
    try:
        w = TrainingRequest.objects.select_related().get(pk=wid)
    except Exception, e:
        # print e
        messages.error(request, 'Invalid Training-Request ID passed')
        return HttpResponseRedirect('/participant/index/?category=1')
        # return PermissionDenied('Invalid Training-Request ID passed')
    try:
        # check if feedback already exits
        TrainingFeedback.objects.get(training_id=wid, mdluser_id=mdluserid)
        messages.success(request, "We have already received your feedback. ")
        return HttpResponseRedirect('/participant/index/?category=1')
    except Exception, e:
        # print e
        pass

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            try:
                form_data = form.save(commit=False)
                form_data.training_id = wid
                form_data.mdluser_id = mdluserid
                form_data.save()
                messages.success(request, "Thank you for your valuable feedback.")
                return HttpResponseRedirect('/participant/index/?category=1')
            except Exception, e:
                print e
                pass
                # return HttpResponseRedirect('/participant/index/')
    context = {
        'form': form,
        'w': w,
        'mdluserid': mdluserid,
        'mdlusername': mdlusername,
    }
    context.update(csrf(request))
    return render(request, 'mdl/templates/feedback.html', context)


def forget_password(request):
    context = {}
    form = PasswordResetForm()
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            user = MdlUser.objects.filter(email=request.POST['email']).first()
            password_encript = encript_password(password_string)
            user.password = password_encript
            user.save()
            # reset auth user password
            mdluser, flag, authuser = get_or_create_user(user)
            authuser.set_password(password_string)
            authuser.save()

            subject = "Spoken Tutorial Online Test password reset"
            to = [user.email]
            message = '''Hi {0},

Your account password at 'Spoken Tutorials Online Test Center' has been reset
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

Cheers from the 'Spoken Tutorials Online Test Center' administrator,

Admin Spoken Tutorials
'''.format(user.firstname, user.username, password_string, 'http://onlinetest.spoken-tutorial.org/login/change_password.php')

            # send email
            email = EmailMultiAlternatives(
                subject, message, 'administrator@spoken-tutorial.org',
                to=to, bcc=[], cc=[],
                headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type": "text/html;charset=iso-8859-1"}
            )

            email.send(fail_silently=False)
            messages.success(request, "New password sent to your email " + user.email)
            return HttpResponseRedirect('/participant/login/')

    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'mdl/templates/password_reset.html', context)


def changeMdlUserPass(email, password_string):
    """updated mdl pass when auth user pass change
    """
    try:
        user = MdlUser.objects.filter(email=email).first()
        password_encript = encript_password(password_string)
        user.password = password_encript
        user.save()
        return True
    except:
        return False
