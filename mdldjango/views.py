from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from models import MdlUser
from events.models import WorkshopAttendance
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from forms import *
from django.contrib import messages
import xml.etree.cElementTree as etree
# Create your views here.
import hashlib

def encript_password(password):
    password = hashlib.md5(password+'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').hexdigest()
    print password
    return password
    
def authenticate(username = None, password = None):
    try:
        print " i am in moodle auth"
        user = MdlUser.objects.get(username=username)
        print user
        pwd = user.password
        p = encript_password(password)
        pwd_valid =  (pwd == p)
        print pwd
        #print "------------"
        if user and pwd_valid:
            return user
    except Exception, e:
        print e
        print "except ---"
        return None

def mdl_logout(request):
    del request.session['mdluserid']
    request.session.save()
    print "logout !!"
    return HttpResponseRedirect("/moodle/login")
    
def mdl_login(request):
    messages = {}
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]
        if not username or not password:
            messages['error'] = "Please enter valide Username and Password!"
            #return HttpResponseRedirect("/moodle/login")
        user = authenticate(username = username, password = password)
        if user:
            request.session['mdluserid'] = user.id
            request.session['mdluseremail'] = user.email
            request.session['mdluserinstitution'] = user.institution
            request.session.save()
            request.session.modified = True
        else:
            messages['error'] = "Username or Password Doesn't match!"

    if request.session.get('mdluserid'):
        print "Current user is ", request.session.get('mdluserid')
        return HttpResponseRedirect("/moodle/index")
        
    context = {'message':messages}
    context.update(csrf(request))
    return render(request, 'mdl/templates/mdluser_login.html', context)

def index(request):
    mdluserid = request.session.get('mdluserid')
    if not mdluserid:
        return HttpResponseRedirect("/moodle/login")
    
    try:
        mdluser = MdlUser.objects.get(id=mdluserid)
    except:
        return HttpResponseRedirect("/moodle/login")
    
    upcoming_workshop = Workshop.objects.filter(status=1, academic_id=mdluser.institution)
    upcoming_test = Test.objects.filter(status=2, academic_id=mdluser.institution)
    past_workshop = Workshop.objects.filter(id__in = WorkshopAttendance.objects.filter(mdluser_id = mdluser.id).values_list('workshop_id'), status = 2)
    past_test = Test.objects.filter(id__in = TestAttendance.objects.filter(mdluser_id = mdluser.id).values_list('test_id'), status = 4)
    
    context = {
        'mdluserid' : mdluserid,
        'upcoming_workshop' : upcoming_workshop,
        'upcoming_test' : upcoming_test,
        'past_workshop' : past_workshop,
        'past_test' : past_test

    }
    context.update(csrf(request))
    return render(request, 'mdl/templates/mdluser_index.html', context)
    
@login_required
def offline_details(request):
    user = request.user
    form = OfflineDataForm(user = request.user)
    wid = 0
    if request.method == 'POST':
        form = OfflineDataForm(user, request.POST, request.FILES)
        if form.is_valid():
            xmlDocData = form.cleaned_data['xml_file'].read()
            xmlDocTree = etree.XML(xmlDocData)
            wid = form.cleaned_data['workshop_code']
            try:
                w = Workshop.objects.get(id = wid)
            except:
                print "Error"
                
            for studentDetails in xmlDocTree.iter('detail'):
                firstname = studentDetails[0].text
                lastname = studentDetails[1].text
                gender =  studentDetails[2].text
                age = studentDetails[3].text
                email = studentDetails[4].text
                permanent_address = studentDetails[5].text
                city = studentDetails[6].text
                country = studentDetails[7].text
                department = studentDetails[8].text
                password = hashlib.md5(studentDetails[0].text)
                password = password.hexdigest()
                try:
                    mdluser = MdlUser.objects.get(email = email)
                    
                except Exception, e:
                    mdluser = MdlUser()
                    mdluser.firstname = firstname
                    mdluser.username = firstname
                    mdluser.lastname = lastname
                    mdluser.password = password
                    mdluser.institution = w.academic_id
                    mdluser.email = email
                    mdluser.save()
                    mdluser = MdlUser.objects.filter(email = email, firstname= firstname, username=firstname, password=password).first()
                
                try:
                    wa = WorkshopAttendance.objects.get(workshop_id = form.cleaned_data['workshop_code'], mdluser_id = mdluser.id)
                except Exception, e:
                    wa = WorkshopAttendance()
                    wa.workshop_id = wid
                    wa.status = 1
                    wa.mdluser_id = mdluser.id
                    wa.save()
            return HttpResponseRedirect('/events/workshop/'+str(wid)+'/approvel/?status=completed')
    messages = {}
    context = {
        'form': form,
        'message':messages,
    }
    context.update(csrf(request))
    return render(request, 'mdl/templates/offline_details.html', context)

def mdl_register(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            mdluser = MdlUser()
            mdluser.auth = 'manual'
            mdluser.institution = form.cleaned_data['college']
            mdluser.firstname = form.cleaned_data['firstname']
            mdluser.lastname = form.cleaned_data['lastname']
            mdluser.email = form.cleaned_data['email']
            mdluser.username = form.cleaned_data['username']
            mdluser.password = encript_password(form.cleaned_data['password'])
            mdluser.confirmed = 1
            mdluser.mnethostid = 1
            mdluser.save()
            messages.success(request, "User " + form.cleaned_data['firstname'] +" "+form.cleaned_data['firstname']+" Created!")
            return HttpResponseRedirect('/moodle/register/')
            
    context = {}
    context['form'] = form
    context.update(csrf(request))
    return render(request, 'mdl/templates/register.html', context)
