from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from models import MdlUser
from events.models import TrainingAttendance
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from forms import *
from django.contrib import messages
import xml.etree.cElementTree as etree
from xml.etree.ElementTree import ElementTree
# Create your views here.
import hashlib
import csv, os, time
from django.core.exceptions import PermissionDenied
from events.views import *
from events.models import *
from django.conf import settings
from events.forms import OrganiserForm
from django.core.mail import EmailMultiAlternatives
from validate_email import validate_email
from get_or_create_participant import get_or_create_participant, encript_password, check_csvfile
    
def authenticate(username = None, password = None):
    try:
        #print " i am in moodle auth"
        user = MdlUser.objects.get(username=username)
        #print user
        pwd = user.password
        p = encript_password(password)
        pwd_valid =  (pwd == p)
        #print pwd
        #print "------------"
        if user and pwd_valid:
            return user
    except Exception, e:
        #print e
        #print "except ---"
        return None

def mdl_logout(request):
    if 'mdluserid' in request.session:
        del request.session['mdluserid']
        request.session.save()
    #print "logout !!"
    return HttpResponseRedirect('/participant/login')
    
def mdl_login(request):
    messages = {}
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]
        if not username or not password:
            messages['error'] = "Please enter valide Username and Password!"
            #return HttpResponseRedirect('/participant/login')
        user = authenticate(username = username, password = password)
        if user:
            request.session['mdluserid'] = user.id
            request.session['mdluseremail'] = user.email
            request.session['mdlusername'] = user.username
            request.session['mdluserinstitution'] = user.institution
            request.session.save()
            request.session.modified = True
        else:
            messages['error'] = "Username or Password Doesn't match!"

    if request.session.get('mdluserid'):
        #print "Current user is ", request.session.get('mdluserid')
        return HttpResponseRedirect('/participant/index')
        
    context = {'message':messages}
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
    
    if str(mdluser.institution).isdigit():
        academic = None
        try:
            academic = AcademicCenter.objects.get(id = mdluser.institution)
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
                upcoming_workshop = Training.objects.filter((Q(status = 0) | Q(status = 1) | Q(status = 2) | Q(status = 3)), academic_id=mdluser.institution, trdate__gte=datetime.date.today()).order_by('-trdate')
            if category == 5:
                upcoming_test = Test.objects.filter(status=2, academic_id=mdluser.institution, tdate__gt=datetime.date.today()).order_by('-tdate')
            if category == 1:
                past_workshop = Training.objects.filter(id__in = TrainingAttendance.objects.filter(mdluser_id = mdluser.id).values_list('training_id'), status = 4).order_by('-trdate')
            if category == 2:
                past_test = Test.objects.filter(id__in = TestAttendance.objects.filter(mdluser_id = mdluser.id).values_list('test_id'), status = 4).order_by('-tdate')
            if category == 4:
                ongoing_test = Test.objects.filter(status=3, academic_id=mdluser.institution, tdate = datetime.date.today()).order_by('-tdate')
            
            context = {
                'mdluserid' : mdluserid,
                'mdlusername' : mdlusername,
                'upcoming_workshop' : upcoming_workshop,
                'upcoming_test' : upcoming_test,
                'past_workshop' : past_workshop,
                'past_test' : past_test,
                'ongoing_test' : ongoing_test,
                'category' : category,
                'ONLINE_TEST_URL' : settings.ONLINE_TEST_URL

            }
            context.update(csrf(request))
            return render(request, 'mdl/templates/mdluser_index.html', context)
    
    form  = OrganiserForm()
    if request.method == 'POST':
        form = OrganiserForm(request.POST)
        if form.is_valid():
            mdluser.institution = form.cleaned_data['college']
            mdluser.save()
            return HttpResponseRedirect('/participant/index')
    context = {
        'form' : form
    }
    context.update(csrf(request))
    return render(request, 'mdl/templates/academic.html', context)

@login_required
def offline_details(request, wid, category):
    wid = int(wid)
    category = int(category)
    #print category
    user = request.user
    form = OfflineDataForm()
    try:
        if category == 1:
            Training.objects.get(pk=wid, status__lt=4)
        elif category == 2:
            Training.objects.get(pk=wid, status__lt=4)
        else:
            #print 'yes'
            raise PermissionDenied('You are not allowed to view this page!')
    except Exception, e:
        #print e
        raise PermissionDenied('You are not allowed to view this page!')
        
    if request.method == 'POST':
        form = OfflineDataForm(request.POST, request.FILES)
        try:
            if category == 1:
                w = Training.objects.get(id = wid)
            elif category == 2:
                w = Training.objects.get(id = wid)
            else:
                raise PermissionDenied('You are not allowed to view this page!')
        except:
            raise PermissionDenied('You are not allowed to view this page!')
                    
        if form.is_valid():
            if request.FILES['xml_file'].content_type == 'text/xml':
                tree = ElementTree()
                try:
                    data = tree.parse(request.FILES['xml_file'])
                except:
                    messages.error(request, "Mismatched tags in Xml file. Please check weather all tags placed properly.")
                    return HttpResponseRedirect('/participant/offline-data/'+ str(wid) + '/' + str(category))
                details = data.getiterator("detail")
                count = 0
                for studentDetails in details:
                    count = count + 1
                    #print studentDetails
                    try:
                        firstname = studentDetails[0].text.strip().title()
                        lastname = studentDetails[1].text.strip().title()
                        gender =  studentDetails[2].text.strip().title()
                        email = None
                        try:
                            email = studentDetails[3].text.lower().strip()
                        except:
                            messages.error(request, "Participant/Student's Email ID is Required. Please open with browser and check all required details are exits!")
                            return HttpResponseRedirect('/participant/offline-data/'+ str(wid) + '/' + str(category))
                        get_or_create_participant(w, firstname, lastname, gender, email, category)
                    except Exception, e:
                        #print e, "sssssssssss"
                        messages.error(request, "Record number "+ str(count) + " required data is missing. Please open with browser and check all required details are exits!.")
                        continue
            else:
                file_path = settings.MEDIA_ROOT + 'training/' + str(wid) + str(time.time())
                f = request.FILES['xml_file']
                fout = open(file_path, 'wb+')
                for chunk in f.chunks():
                    fout.write(chunk)
                fout.close()
                
                error_line_no = ''
                csv_file_error = 0
                csv_file_error, error_line_no = check_csvfile(file_path, w, flag=1)
                os.unlink(file_path)
                #save participant_count
                w.participant_counts = TrainingAttendance.objects.filter(training = w, status__gte = 1).count()
                w.save()
                
                if error_line_no:
                    messages.error(request, "<b>Error: Line number "+ error_line_no + " in CSV file data is not in a proper format in the Participant list. The format should be First name, Last name, Email, Gender. For more details <a href='http://process.spoken-tutorial.org/images/c/c2/Participant_data.pdf' target='_blank'>Click here</a></b>")
            #update logs
            if category == 1:
                message = w.academic.institution_name+" has submited Offline "+w.foss.foss+" workshop attendance dated "+w.trdate.strftime("%Y-%m-%d")
                update_events_log(user_id = user.id, role = 2, category = 0, category_id = w.id, academic = w.academic_id, status = 5)
                update_events_notification(user_id = user.id, role = 2, category = 0, category_id = w.id, academic = w.academic_id, status = 5, message = message)
                if not error_line_no:
                    messages.success(request, "Thank you for uploading the Attendance. Now make sure that you cross check and verify the details before submiting.")
                return HttpResponseRedirect('/software-training/workshop/'+str(wid)+'/attendance/')
            else:
                message = w.academic.institution_name+" has submited Offline training attendance."
                update_events_log(user_id = user.id, role = 2, category = 2, category_id = w.id, academic = w.academic_id, status = 5)
                update_events_notification(user_id = user.id, role = 2, category = 2, category_id = w.id, academic = w.academic_id, status = 5, message = message)
                if not error_line_no:
                    messages.success(request, "Thank you for uploading the Attendance. Now make sure that you cross check and verify the details before submiting.")
                return HttpResponseRedirect('/software-training/training/'+str(wid)+'/attendance/')
        messages.error(request, "Please Upload xml file !") 
    context = {
        'form': form,
    }
    messages.info(request, """
        Please upload the CSV file which you have generated. 
        To know more <a href="http://process.spoken-tutorial.org/images/9/96/Upload_Attendance.pdf" target="_blank">Click here</a>.
    """) 
    context.update(csrf(request))
    return render(request, 'mdl/templates/offline_details.html', context)

def mdl_register(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        
        #Email exits
        try:
            user = MdlUser.objects.filter(email=request.POST['email']).first()
            if user:
                messages.success(request, "Email : "+request.POST['email']+" already registered on this website. Please click <a href='http://www.spoken-tutorial.org/participant/login/'>here </a>to login")
        except Exception, e:
            #print e
            pass
            
        if form.is_valid():
            mdluser = MdlUser()
            mdluser.auth = 'manual'
            mdluser.institution = form.cleaned_data['college']
            mdluser.gender = form.cleaned_data['gender']
            mdluser.firstname = form.cleaned_data['firstname']
            mdluser.lastname = form.cleaned_data['lastname']
            mdluser.email = form.cleaned_data['email']
            mdluser.username = form.cleaned_data['username']
            mdluser.password = encript_password(form.cleaned_data['password'])
            mdluser.confirmed = 1
            mdluser.mnethostid = 1
            mdluser.save()
            messages.success(request, "User " + form.cleaned_data['firstname'] +" "+form.cleaned_data['lastname']+" Created!")
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
        w = Training.objects.select_related().get(pk=wid)
        #check if feedback already exits
        TrainingFeedback.objects.get(training_id = wid, mdluser_id = mdluserid)
        messages.success(request, "We have already received your feedback. ")
        return HttpResponseRedirect('/participant/index/?category=1')
    except Exception, e:
        #print e
        pass
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            try:
                form_data = form.save(commit=False)
                form_data.training_id = wid
                form_data.mdluser_id = mdluserid
                form_data.save()
                try:
                    wa = TrainingAttendance.objects.get(mdluser_id=mdluserid, training_id = wid)
                    wa.status = 2
                    wa.save()
                except:
                    wa = TrainingAttendance()
                    wa.training_id = wid
                    wa.mdluser_id = mdluserid
                    wa.status = 1
                    wa.save()
                messages.success(request, "Thank you for your valuable feedback.")
                return HttpResponseRedirect('/participant/index/?category=1')
            except Exception, e:
                print e
                pass
                #return HttpResponseRedirect('/participant/index/')
    context = {
        'form' : form,
        'w' : w,
        'mdluserid' : mdluserid,
        'mdlusername' : mdlusername,
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
            subject  = "Spoken Tutorial Online Test password reset"
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
                to = to, bcc = [], cc = [],
                headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
            )

            result = email.send(fail_silently=False)
            messages.success(request, "New password sent to your email "+user.email)
            return HttpResponseRedirect('/participant/login/')
            

    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'mdl/templates/password_reset.html', context)
