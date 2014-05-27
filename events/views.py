from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt

from django.http import Http404
from django.db.models import Q

from urlparse import urlparse

from BeautifulSoup import BeautifulSoup

import xml.etree.cElementTree as etree

import json
import urllib,urllib2

from events.models import *
from cms.models import Profile

from forms import *
import datetime
from django.utils import formats
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#pdf generate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from PyPDF2 import PdfFileWriter, PdfFileReader
from StringIO import StringIO

#randon string
import string
import random

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def is_event_manager(user):
    """Check if the user is having event manger  rights"""
    if user.groups.filter(name='Event Manager').count() == 1:
        return True
        
def is_resource_person(user):
    """Check if the user is having resource person  rights"""
    if user.groups.filter(name='Resource Person').count() == 1:
        return True
        
def is_organiser(user):
    """Check if the user is having organiser rights"""
    try:
        if user.groups.filter(name='Organiser').count() == 1 and user.organiser and user.organiser.status == 1:
            return True
    except:
        pass

def is_invigilator(user):
    """Check if the user is having invigilator rights"""
    if user.groups.filter(name='Invigilator').count() == 1:
        return True

@login_required
def events_dashboard(request):
    user = request.user
    roles = user.groups.all()
    context = {
        'roles' : roles
    }
    return render(request, 'events/templates/events_dashboard.html', context)


@login_required
def new_ac(request):
    """ Create new academic center. Academic code generate by autimatic.
        if any code missing in between first assign that code then continue the serial
    """
    user = request.user
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page!')
        
    if request.method == 'POST':
        form = AcademicForm(user, request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user_id = user.id
            
            state = form.cleaned_data['state']
            # find the academic code available number
            try:
                ac = AcademicCenter.objects.filter(state = state).order_by('-academic_code')[:1].get()
            except:
                #print "This is first record!!!"
                ac = None
                academic_code = 1
                
            if ac:
                code_range = int(ac.academic_code.split('-')[1])
                available_code_range = []
                for i in range(code_range):
                    available_code_range.insert(i, i+1)
                
                #find the existing numbers
                ac = AcademicCenter.objects.filter(state = state).order_by('-academic_code')
                for record in ac:
                    a = int(record.academic_code.split('-')[1])-1
                    available_code_range[a] = 0
                
                academic_code = code_range + 1
                #finding Missing number
                for code in available_code_range:
                    if code != 0:
                        academic_code = code
                        break

            # Generate academic code
            if academic_code < 10:
                ac_code = '0000'+str(academic_code)
            elif academic_code <= 99:
                ac_code = '000'+str(academic_code)
            elif academic_code <= 999:
                ac_code = '00'+str(academic_code)
            elif academic_code <= 9999:
                ac_code = '0'+str(academic_code)
            
            #get state code
            state_code = State.objects.get(pk = state.id).code
            academic_code = state_code +'-'+ ac_code
            
            form_data.academic_code = academic_code
            form_data.save()
            messages.success(request, form_data.institution_name+" has been added!")
            return HttpResponseRedirect("/events/ac/")
        
        context = {'form':form}
        return render(request, 'events/templates/ac/form.html', context)
    else:
        context = {}
        context.update(csrf(request))
        context['form'] = AcademicForm(user=request.user)
        return render(request, 'events/templates/ac/form.html', context)

@login_required
def edit_ac(request, rid = None):
    """ Edit academic center """
    user = request.user
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page!')
        
    if request.method == 'POST':
        contact = AcademicCenter.objects.get(id = rid)
        form = AcademicForm(request.user, request.POST, instance=contact)
        if form.is_valid():
            if form.save():
                return HttpResponseRedirect("/events/ac/")
        context = {'form':form}
        return render(request, 'events/templates/ac/form.html', context)
    else:
        try:
            record = AcademicCenter.objects.get(id = rid)
            context = {}
            context['form'] = AcademicForm(user=request.user, instance = record)
            context['edit'] = rid
            context.update(csrf(request))
            return render(request, 'events/templates/ac/form.html', context)
        except:
            raise Http404('Page not found')

@login_required
def ac(request):
    """ Academic index page """
    user = request.user
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page!')
        
    context = {}
    context['collection'] = AcademicCenter.objects.all
    context['model'] = "Academic Center"
    context.update(csrf(request))
    return render(request, 'events/templates/ac/index.html', context)
    return HttpResponse('RP!')

def has_profile_data(request, user):
    ''' check weather user profile having blank data or not '''
    if user:
        profile = Profile.objects.filter(user=user).first()
        if not profile:
            return HttpResponseRedirect("/accounts/profile/"+user.username+"/")
    
        for field in profile._meta.get_all_field_names():
            if not getattr(profile, field, None):
                return HttpResponseRedirect("/accounts/profile/"+user.username+"/")

@login_required
def organiser_request(request, username):
    """ request to bacome a new organiser """
    user = request.user
    if not user.is_authenticated():
        raise Http404('You are not allowed to view this page!')
        
    if username == request.user.username:
        user = User.objects.get(username=username)
        if request.method == 'POST':
            form = OrganiserForm(request.POST)
            if form.is_valid():
                user.groups.add(Group.objects.get(name='Organiser'))
                organiser = Organiser()
                organiser.user_id=request.user.id
                organiser.academic_id=request.POST['college']
                organiser.save()
                return HttpResponseRedirect("/events/organiser/view/"+user.username+"/")
            context = {'form':form}
            return render(request, 'events/templates/organiser/form.html', context)
        else:
            try:
                organiser = Organiser.objects.get(user=user)
                #todo: send status message
                if organiser.status:
                    print "you have already organiser role !!"
                    return HttpResponseRedirect("/events/organiser/view/"+user.username+"/")
                else:
                    print "Organiser not yet approve !!"
                    return HttpResponseRedirect("/events/organiser/view/"+user.username+"/")
            except:
                context = {}
                context.update(csrf(request))
                context['form'] = OrganiserForm()
                return render(request, 'events/templates/organiser/form.html', context)
    else:
        raise Http404('You are not allowed to view this page!')

@login_required
def organiser_view(request, username):
    """ view organiser details """
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page!')
    
    user = User.objects.get(username=username)
    context = {}
    organiser = Organiser.objects.get(user=user)
    context['record'] = organiser
    try:
        profile = organiser.user.profile_set.get()
    except:
        profile = ''
    context['profile'] = profile
    return render(request, 'events/templates/organiser/view.html', context)

#@login_required
def organiser_edit(request, username):
    """ view organiser details """
    #todo: confirm event_manager and resource_center can edit organiser details
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page!')
        
    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = OrganiserForm(request.POST)
        if form.is_valid():
            organiser = Organiser.objects.get(user=user)
            #organiser.user_id=request.user.id
            organiser.academic_id=request.POST['college']
            organiser.save()
            return HttpResponseRedirect("/events/organiser/view/"+user.username+"/")
        context = {'form':form}
        return render(request, 'events/templates/organiser/form.html', context)
    else:
            #todo : if any workshop and test under this organiser disable the edit
            record = Organiser.objects.get(user=user)
            context = {}
            context['form'] = OrganiserForm(instance = record)
            context.update(csrf(request))
            return render(request, 'events/templates/organiser/form.html', context)

@login_required
def rp_organiser(request, status = None):
    """ Resource person: List all inactive organiser under resource person states """
    #todo: filter to diaplay block and active user
    user = request.user
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page!')
    if status == 'active':
        status = 1
    elif status == 'inactive':
        status = 0
    elif status == 'blocked':
        status = 2
    else:
        raise Http404('Page not found !!')
        
    user = User.objects.get(pk=user.id)
    try:
        organiser = Organiser.objects.filter(academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)), status=status)
    except:
        organiser = {}
    context = {}
    context['collection'] = organiser
    context['active'] = status
    return render(request, 'events/templates/rp/organiser.html', context)

@login_required
def rp_organiser_confirm(request, code, userid):
    """ Resource person: active organiser """
    user = request.user
    organiser_in_rp_state = Organiser.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)))
    if not (user.is_authenticated() and organiser_in_rp_state and ( is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied('You are not allowed to view this page!')

    try:
        if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
            organiser = Organiser.objects.get(user_id = userid)
            organiser.appoved_by_id = request.user.id
            organiser.status = 1
            organiser.save()
            return HttpResponseRedirect('/events/organiser/active/')
        else:
            raise Http404('Page not found !!')
    except:
        raise PermissionDenied('You are not allowed to view this page!')

@login_required
def rp_organiser_block(request, code, userid):
    """ Resource person: block organiser """
    #todo: if user block, again he trying to register, display message your accout blocked by rp contact rp
    user = request.user
    organiser_in_rp_state = Organiser.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)))
    if not (user.is_authenticated() and organiser_in_rp_state and ( is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied('You are not allowed to view this page!')

    try:
        if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
            organiser = Organiser.objects.get(user_id = userid)
            organiser.appoved_by_id = request.user.id
            organiser.status = 2
            organiser.save()
            return HttpResponseRedirect('/events/organiser/active/')
        else:
            raise Http404('Page not found !!')
    except:
        raise PermissionDenied('You are not allowed to view this page!')

@login_required
def invigilator_request(request, username):
    """ Request to bacome a invigilator """
    user = request.user
    if not user.is_authenticated():
        raise Http404('You are not allowed to view this page!')

    if username == user.username:
        user = User.objects.get(username=username)
        if request.method == 'POST':
            form = InvigilatorForm(request.POST)
            if form.is_valid():
                user.groups.add(Group.objects.get(name='invigilator'))
                invigilator = Invigilator()
                invigilator.user_id=request.user.id
                invigilator.academic_id=request.POST['college']
                invigilator.save()
                return HttpResponseRedirect("/events/invigilator/view/"+user.username+"/")
            context = {'form':form}
            return render(request, 'events/templates/invigilator/form.html', context)
        else:
            try:
                invigilator = Invigilator.objects.get(user=user)
                #todo: send status message
                if invigilator.status:
                    print "you have already invigilator role !!"
                    return HttpResponseRedirect("/events/invigilator/view/"+user.username+"/")
                else:
                    print "invigilator not yet approve !!"
                    return HttpResponseRedirect("/events/invigilator/view/"+user.username+"/")
            except:
                context = {}
                context.update(csrf(request))
                context['form'] = InvigilatorForm()
                return render(request, 'events/templates/invigilator/form.html', context)
    else:
        raise Http404('You are not allowed to view this page!')

@login_required
def invigilator_view(request, username):
    """ Invigilator view page """
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page!')
    
    user = User.objects.get(username=username)
    context = {}
    invigilator = Invigilator.objects.get(user=user)
    context['record'] = invigilator
    try:
        profile = invigilator.user.profile_set.get()
    except:
        profile = ''
    context['profile'] = profile
    return render(request, 'events/templates/invigilator/view.html', context)
    
@login_required
def invigilator_edit(request, username):
    """ Invigilator edit page """
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page!')
        
    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = InvigilatorForm(request.POST)
        if form.is_valid():
            invigilator = Invigilator.objects.get(user=user)
            invigilator.academic_id=request.POST['college']
            invigilator.save()
            return HttpResponseRedirect("/events/invigilator/view/"+user.username+"/")
        context = {'form':form}
        return render(request, 'events/templates/invigilator/form.html', context)
    else:
            #todo : if any workshop and test under this invigilator disable the edit
            record = Invigilator.objects.get(user=user)
            context = {}
            context['form'] = InvigilatorForm(instance = record)
            context.update(csrf(request))
            return render(request, 'events/templates/invigilator/form.html', context)

@login_required
def rp_invigilator(request, status = None):
    print "ssssss", status
    """ Resource person: List all inactive Invigilator under resource person states """
    #todo: filter to diaplay block and active user
    user = request.user
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise Http404('You are not allowed to view this page!')
    if status == 'active':
        status = 1
    elif status == 'inactive':
        status = 0
    elif status == 'blocked':
        status = 2
    else:
        raise Http404('Page not found !!')
        
    user = User.objects.get(pk=user.id)
    try:
        invigilator = Invigilator.objects.filter(academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)), status=status)
    except:
        invigilator = {}
    context = {}
    context['collection'] = invigilator
    context['active'] = status
    return render(request, 'events/templates/rp/invigilator.html', context)

@login_required
def rp_invigilator_confirm(request, code, userid):
    """ Resource person: active invigilator """
    user = request.user
    invigilator_in_rp_state = Invigilator.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)))
    if not (user.is_authenticated() and invigilator_in_rp_state and ( is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied('You are not allowed to view this page!')

    try:
        if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
            invigilator = Invigilator.objects.get(user_id = userid)
            invigilator.appoved_by_id = request.user.id
            invigilator.status = 1
            invigilator.save()
            return HttpResponseRedirect('/events/invigilator/active/')
        else:
            raise Http404('Page not found !!')
    except:
        raise PermissionDenied('You are not allowed to view this page!')

@login_required
def rp_invigilator_block(request, code, userid):
    """ Resource person: block invigilator """
    #todo: if user block, again he trying to register, display message your accout blocked by rp contact rp
    user = request.user
    invigilator_in_rp_state = Invigilator.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)))
    if not (user.is_authenticated() and invigilator_in_rp_state and ( is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied('You are not allowed to view this page!')

    try:
        if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
            invigilator = Invigilator.objects.get(user_id = userid)
            invigilator.appoved_by_id = request.user.id
            invigilator.status = 2
            invigilator.save()
            return HttpResponseRedirect('/events/invigilator/active/')
        else:
            raise Http404('Page not found !!')
    except:
        raise PermissionDenied('You are not allowed to view this page!')

@login_required
def workshop_request(request):
    ''' Workshop request by organiser '''
    user = request.user
    if not user.is_authenticated() or not is_organiser(user):
        raise Http404('You are not allowed to view this page!')
    
    if request.method == 'POST':
        form = WorkshopForm(request.POST, user = request.user)
        if form.is_valid():
            dateTime = request.POST['wdate'].split(' ')
            w = Workshop()
            w.organiser_id = user.id
            #w.academic_id = request.POST['academic']
            w.academic = user.organiser.academic
            w.language_id = request.POST['language']
            w.foss_id = request.POST['foss']
            w.wdate = dateTime[0]
            w.wtime = dateTime[1]
            w.skype = request.POST['skype']
            w.save()
            #M2M saving department
            for dept in form.cleaned_data.get('department'):
                w.department.add(dept)
            w.save()
            messages.success(request, "Your Workshop request has been send!")
            return HttpResponseRedirect("/events/workshop/organiser/pending/")
        
        context = {'form':form, }
        return render(request, 'events/templates/workshop/form.html', context)
    else:
        context = {}
        context.update(csrf(request))
        context['form'] = WorkshopForm(user = request.user)
        return render(request, 'events/templates/workshop/form.html', context)

def workshop_edit(request, role, rid):
    ''' Workshop edit by organiser or resource person '''
    user = request.user
    if not user.is_authenticated() or not is_organiser:
        raise Http404('You are not allowed to view this page!')
    
    if request.method == 'POST':
        form = WorkshopForm(request.POST, user = request.user)
        if form.is_valid():
            print form.cleaned_data
            dateTime = request.POST['wdate'].split(' ')
            w = Workshop.objects.get(pk=rid)
            
            #check if date time chenged or not
            if w.status == 1 and (str(w.wdate) != dateTime[0] or str(w.wtime)[0:5] != dateTime[1]):
                w.status = 4
            w.language_id = request.POST['language']
            w.foss_id = request.POST['foss']
            w.wdate = dateTime[0]
            w.wtime = dateTime[1]
            w.skype = request.POST['skype']
            w.save()
            messages.success(request, "Workshop has been sucessfully updated!")
            return HttpResponseRedirect("/events/workshop/"+role+"/pending/")
        
        context = {'form':form, }
        return render(request, 'events/templates/workshop/form.html', context)
    else:
        context = {}
        record = Workshop.objects.get(id = rid)
        context.update(csrf(request))
        context['form'] = WorkshopForm(instance = record)
        context['instance'] = record
        return render(request, 'events/templates/workshop/form.html', context)

def workshop_list(request, role, status):
    """ Organiser index page """
    user = request.user
    if not (user.is_authenticated() and ( is_organiser(user) or is_resource_person(user) or is_event_manager(user))):
        raise Http404('You are not allowed to view this page!')
        
    status_dict = {'pending': 0, 'approved' : 1, 'completed' : 2, 'rejected' : 3, 'reschedule' : 1}
    if status in status_dict:
        context = {}
        workshops = None
        if is_event_manager(user) and role == 'em':
            workshops = Workshop.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status])
        elif is_resource_person(user) and role == 'rp':
            workshops = Workshop.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status])
        elif is_organiser(user) and role == 'organiser':
            workshops = Workshop.objects.filter(organiser_id=user, status = status_dict[status])
        
        if workshops == None:
            raise Http404('You are not allowed to view this page!')

        paginator = Paginator(workshops, 30)
        page = request.GET.get('page')
        try:
            workshops =  paginator.page(page)
        except PageNotAnInteger:
            workshops =  paginator.page(1)
        except EmptyPage:
            workshops = paginator.page(paginator.num_pages)
        
        context['collection'] = workshops
        context['status'] = status
        context['role'] = role
        context.update(csrf(request))
        return render(request, 'events/templates/workshop/index.html', context)
    else:
        raise Http404('Page not foundddddd !!')

@login_required
@csrf_exempt
def workshop_approvel(request, role, rid):
    """ Resource person: confirm or reject workshop """
    user = request.user
    try:
        w = Workshop.objects.get(pk=rid)
        if request.GET['status'] == 'accept':
            status = 1
        if request.GET['status'] == 'reject':
            status = 3
        if request.GET['status'] == 'completed':
            status = 2
    except:
        raise Http404('Page not found !!')
    if status != 2:
        if not (user.is_authenticated() and w.academic.state in State.objects.filter(resourceperson__user_id=user) and ( is_event_manager(user) or is_resource_person(user))):
            raise PermissionDenied('You are not allowed to view this page!')
    
    w.status = status
    w.appoved_by_id = user.id
    #todo: add workshop code
    if w.status == 1:
        w.workshop_code = "WC-"+str(w.id)
    if request.GET['status'] == 'completed':
        # calculate the participant list
        wpcount = WorkshopAttendance.objects.filter(workshop_id = rid, status = 1).count()
        w.participant_counts = wpcount
        w.save()
        messages.success(request, "Selected workshop has been "+request.GET['status']+"!")
        return HttpResponseRedirect('/events/workshop/'+role+'/completed/')
    w.save()
    messages.success(request, "Selected workshop has been "+request.GET['status']+"!")
    return HttpResponseRedirect('/events/workshop/'+role+'/approved/')

@login_required
def workshop_permission(request):
    user = request.user
    permissions = Permission.objects.select_related().all()
    form = WorkshopPermissionForm()
    if request.method == 'POST':
        form = WorkshopPermissionForm(request.POST)
        if form.is_valid():
            wp = Permission()
            wp.permissiontype_id = form.cleaned_data['permissiontype']
            wp.user_id = form.cleaned_data['user']
            wp.state_id = form.cleaned_data['state']
            wp.assigned_by_id = user.id
            if form.cleaned_data['district']:
                wp.district_id = form.cleaned_data['district']
            if form.cleaned_data['institute']:
                wp.institute_id = form.cleaned_data['institute']
            elif form.cleaned_data['institutiontype']:
                wp.institute_type_id = form.cleaned_data['institutiontype']
            elif form.cleaned_data['university']:
                wp.university_id = form.cleaned_data['university']
            wp.save()
            return HttpResponseRedirect("/events/workshop/permission/")
    
    context = {}
    context.update(csrf(request))
    context['form'] = form
    context['collection'] = permissions
    return render(request, 'events/templates/accessrole/workshop_permission.html', context)
    
@login_required
def accessrole(request):
    user = request.user
    state =  list(AcademicCenter.objects.filter(state__in = Permission.objects.filter(user=user, permissiontype_id=1).values_list('state_id')).values_list('id'))
    district = list(AcademicCenter.objects.filter(district__in = Permission.objects.filter(user=user, permissiontype_id=2, district_id__gt=0).values_list('district_id')).values_list('id'))
    university = list(AcademicCenter.objects.filter(university__in = Permission.objects.filter(user=user, permissiontype_id=3, university_id__gt=0).values_list('university_id')).values_list('id'))
    institution_type = list(AcademicCenter.objects.filter(institution_type__in = Permission.objects.filter(user=user, permissiontype_id=4, institute_type_id__gt=0).values_list('institute_type_id')). values_list('id'))
    institute = list(AcademicCenter.objects.filter(id__in = Permission.objects.filter(user=user, permissiontype_id=5, institute_id__gt=0).values_list('institute_id')).values_list('id'))
    all_academic_ids = list(set(state) | set(district) | set(university) | set(institution_type) | set(institute)) 
    workshops = Workshop.objects.filter(academic__in = all_academic_ids)
    context = {'collection':workshops}
    return render(request, 'events/templates/accessrole/workshop_accessrole.html', context)

def workshop_attendance(request, wid):
    user = request.user
     
    try:
        workshop = Workshop.objects.get(pk = wid) 
    except:
        raise Http404('Page not found !!')
    #todo check request user and workshop organiser same or not
    if request.method == 'POST':
        users = request.POST
        if users:
            #set all record to 0 if status = 1
            WorkshopAttendance.objects.filter(workshop_id = wid, status = 1).update(status = 0)
            for u in users:
                if u != 'csrfmiddlewaretoken':
                    try:
                        wa = WorkshopAttendance.objects.get(mdluser_id = users[u], workshop_id = wid)
                        print wa.id, " => Exits"
                    except:
                        wa = WorkshopAttendance()
                        wa.workshop_id = wid
                        wa.mdluser_id = users[u]
                        wa.status = 0
                        wa.save()
                        print wa.id, " => Inserted"
                    if wa:
                        #todo: if the status = 2 check in moodle if he completed the test set status = 3 (completed)
                        w = WorkshopAttendance.objects.get(mdluser_id = wa.mdluser_id, workshop_id = wid)
                        w.status = 1
                        w.save()
            messages.success(request, "Marked Attandance has been updated!") 
    participant_ids = list(WorkshopAttendance.objects.filter(workshop_id = wid).values_list('mdluser_id'))
    mdlids = []
    for k in participant_ids:
        mdlids.append(k[0])
    if mdlids:
        wp = MdlUser.objects.filter(id__in = mdlids)
    context = {}
    context['collection'] = wp
    context['workshop'] = workshop
    context.update(csrf(request))
    return render(request, 'events/templates/workshop/attendance.html', context)


@login_required
def workshop_participant(request, wid=None):
    user = request.user
    can_download_certificate = 0
    if wid:
        try:
            wc = Workshop.objects.get(id=wid)
        except:
            raise Http404('Page not found')
            
        workshop_mdlusers = WorkshopAttendance.objects.using('default').filter(workshop_id=wid).values_list('mdluser_id')
        ids = []
        for wp in workshop_mdlusers:
            ids.append(wp[0])
            
        wp = MdlUser.objects.using('moodle').filter(id__in=ids)
        if user == wc.organiser:
            can_download_certificate = 1
        context = {'collection' : wp, 'wc' : wc, 'can_download_certificate':can_download_certificate}
        return render(request, 'events/templates/workshop/workshop_participant.html', context)


def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))
    
    
def workshop_participant_ceritificate(request, wid, participant_id):
    #response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    #p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    #p.drawString(200, 500, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    #p.showPage()
    #p.save()
    #return response
    # Using ReportLab to insert image into PDF
    
    #store Certificate details
    
    certificate_pass = ''
    if wid and participant_id:
        try:
            w = Workshop.objects.get(id = wid)
            mdluser = MdlUser.objects.get(id = participant_id)
            wcf = None
            # check if user can get certificate
            wa = WorkshopAttendance.objects.get(workshop_id = w.id, mdluser_id = participant_id)
            if wa.status < 1:
                raise Http404('Page not found')
            if wa.password:
                certificate_pass = wa.password
                wa.count += 1
                wa.status = 2
                wa.save()
            else:
                certificate_pass = str(mdluser.id)+id_generator(10-len(str(mdluser.id)))
                wa.password = certificate_pass
                wa.status = 2
                wa.count += 1
                wa.save()
        except:
            raise Http404('Page not found')
        
    response = HttpResponse(mimetype='application/pdf')
    filename = (mdluser.firstname+'-'+w.foss.foss+"-Participant-Certificate").replace(" ", "-");
    
    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'
    imgTemp = StringIO()
    imgDoc = canvas.Canvas(imgTemp)

    # Title 
    imgDoc.setFont('Helvetica', 40, leading=None)
    imgDoc.drawCentredString(415, 480, "Certificate of Learning")
    
    #password
    imgDoc.setFillColorRGB(211, 211, 211)
    imgDoc.setFont('Helvetica', 10, leading=None)
    imgDoc.drawString(10, 6, certificate_pass)
    #imgDoc.drawString(100, 100, 'transparent')
    

    # Draw image on Canvas and save PDF in buffer
    imgPath = "/home/deer/sign.jpg"
    imgDoc.drawImage(imgPath, 600, 100, 150, 76)    ## at (399,760) with size 160x160

    #paragraphe
    text = "This is to certify that <b>"+mdluser.firstname +" "+mdluser.lastname+"</b> participated in the <b>"+w.foss.foss+"</b> workshop at <b>"+w.academic.institution_name+"</b> organized by <b>"+w.organiser.username+"</b> on <b>"+custom_strftime('%B {S} %Y', w.wdate)+"</b>.  This workshop was conducted with the instructional material created by the Spoken Tutorial Project, IIT Bombay, funded by the National Mission on Education through ICT, MHRD, Govt., of India."
    
    centered = ParagraphStyle(name = 'centered',
        fontSize = 16,  
        leading = 30,  
        alignment = 0,  
        spaceAfter = 20)

    p = Paragraph(text, centered)
    p.wrap(650, 200)
    p.drawOn(imgDoc, 4.2 * cm, 9 * cm)

    imgDoc.save()

    # Use PyPDF to merge the image-PDF into the template
    page = PdfFileReader(file("/home/deer/Blank-Certificate.pdf","rb")).getPage(0)
    overlay = PdfFileReader(StringIO(imgTemp.getvalue())).getPage(0)
    page.mergePage(overlay)

    #Save the result
    output = PdfFileWriter()
    output.addPage(page)
    
    #stream to browser
    outputStream = response
    output.write(response)
    outputStream.close()

    return response
    
def test_request(request):
    ''' Test request by organiser '''
    user = request.user
    if not user.is_authenticated() or not is_organiser(user):
        raise Http404('You are not allowed to view this page!')
    
    if request.method == 'POST':
        form = TestForm(request.POST, user = request.user)
        if form.is_valid():
            dateTime = request.POST['tdate'].split(' ')
            t = Test()
            t.organiser_id = user.id
            t.invigilator_id = form.cleaned_data['invigilator']
            #t.academic_id = form.cleaned_data['academic']
            t.academic = user.organiser.academic
            t.workshop_id = form.cleaned_data['workshop']
            t.tdate = dateTime[0]
            t.ttime = dateTime[1]
            t.foss_id = form.cleaned_data['foss']
            t.save()
            #M2M saving department
            for dept in form.cleaned_data.get('department'):
                t.department.add(dept)
            t.save()
            messages.success(request, "Thank you, we have received your request")
            return HttpResponseRedirect("/events/test/organiser/pending/")
        
        context = {'form':form, }
        return render(request, 'events/templates/test/form.html', context)
    else:
        context = {}
        context.update(csrf(request))
        context['form'] = TestForm(user = request.user)
        return render(request, 'events/templates/test/form.html', context)

def test_list(request, role, status):
    """ Organiser test index page """
    user = request.user
    if not (user.is_authenticated() and ( is_organiser(user) or is_invigilator(user) or is_resource_person(user) or is_event_manager(user))):
        raise Http404('You are not allowed to view this page!')
        
    status_dict = {'pending': 0, 'waitingforinvigilator': 1, 'approved' : 2, 'ongoing': 3, 'completed' : 4, 'rejected' : 5, 'reschedule' : 1}
    if status in status_dict:
        context = {}
        test = None
        todaytest = None
        if is_event_manager(user) and role == 'em':
            if status == 'ongoing':
                test = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status], tdate = datetime.datetime.now().strftime("%Y-%m-%d"))
            else:
                test = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status])
        elif is_resource_person(user) and role == 'rp':
            if status == 'ongoing':
                test = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status], tdate = datetime.datetime.now().strftime("%Y-%m-%d"))
            else:
                test = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status])
        elif is_organiser(user) and role == 'organiser':
            if status == 'ongoing': 
                test = Test.objects.filter(organiser_id=user, status = status_dict[status], tdate = datetime.datetime.now().strftime("%Y-%m-%d"))
            else:
                test = Test.objects.filter(organiser_id=user, status = status_dict[status])
        elif is_invigilator(user) and role == 'invigilator':
            if status == 'ongoing':
                test = Test.objects.filter(invigilator_id=user, status = status_dict[status], tdate = datetime.datetime.now().strftime("%Y-%m-%d"))
            else:
                todaytest = datetime.datetime.now().strftime("%Y-%m-%d")
                test = Test.objects.filter(invigilator_id=user, status = status_dict[status])
        
        if test == None:
            raise Http404('You are not allowed to view this page!')
            
        context['collection'] = test
        context['status'] = status
        context['role'] = role
        context['todaytest'] = todaytest
        context['can_manage'] = user.groups.filter(Q(name="Event Manager") |  Q(name="Resource Person"))
        context.update(csrf(request))
        return render(request, 'events/templates/test/index.html', context)
    else:
        raise Http404('Page not found !!')

def test_edit(request, role, rid):
    ''' Workshop edit by organiser or resource person '''
    user = request.user
    if not user.is_authenticated() or not is_organiser:
        raise Http404('You are not allowed to view this page!')
    
    if request.method == 'POST':
        form = TestForm(request.POST, user = request.user)
        if form.is_valid():
            print form.cleaned_data
            dateTime = request.POST['tdate'].split(' ')
            t = Test.objects.get(pk=rid)
            #check if date time chenged or not
            if t.status == 1 and (str(t.tdate) != dateTime[0] or str(t.ttime)[0:5] != dateTime[1]):
                t.status = 4
            #t.organiser_id = user.id
            t.invigilator_id = form.cleaned_data['invigilator']
            #t.academic_id = form.cleaned_data['academic']
            t.workshop_id = form.cleaned_data['workshop']
            t.tdate = dateTime[0]
            t.ttime = dateTime[1]
            t.foss_id = form.cleaned_data['foss']
            t.save()
            messages.success(request, "Thank you, we have received your request")
            return HttpResponseRedirect("/events/test/"+role+"/pending/")
        
        context = {'form':form, }
        return render(request, 'events/templates/test/form.html', context)
    else:
        context = {}
        record = Test.objects.get(id = rid)
        context.update(csrf(request))
        context['form'] = TestForm(instance = record, user = user)
        context['instance'] = record
        return render(request, 'events/templates/test/form.html', context)

@login_required
@csrf_exempt
def test_approvel(request, role, rid):
    """ Resource person: confirm or reject workshop """
    user = request.user
    status = 0
    print "EEEEEEEEEEEEEEEEEEEEE"
    try:
        w = Test.objects.get(pk=rid)
        if request.GET['status'] == 'accept':
            status = 1
        if request.GET['status'] == 'invigilatoraccept':
            status = 2
        if request.GET['status'] == 'ongoing':
            status = 3
        if request.GET['status'] == 'completed':
            status = 4
        if request.GET['status'] == 'rejected':
            status = 5
        if request.GET['status'] == 'invigilatorreject':
            status = 6
        print status
        print w
    except:
        raise Http404('Page not found !!')
        
    #if status != 2:
    #    if not (user.is_authenticated() and w.academic.state in State.objects.filter(resourceperson__user_id=user) and ( is_event_manager(user) or is_resource_person(user))):
    #        raise PermissionDenied('You are not allowed to view this page!')
    w.status = status
    if w.status == 1:
        w.appoved_by_id = user.id
        w.workshop_code = "TC-"+str(w.id)
    
    if w.status == 4:
        w.participant_count = TestAttendance.objects.filter(test_id=1).count()
    
    w.save()
    
    if request.GET['status'] == 'completed':
        return HttpResponseRedirect('/events/test/'+role+'/completed/')
    return HttpResponseRedirect('/events/test/'+role+'/approved/')

def test_attendance(request, tid):
    user = request.user
    test = None
    try:
        test = Test.objects.get(pk=tid)
        test.status = 3
        test.save()
    except:
        raise Http404('Page not found !!')
    print test.foss_id
    if request.method == 'POST':
        users = request.POST
        if users:
            #set all record to 0 if status = 1
            TestAttendance.objects.filter(test_id = tid, status = 1).update(status = 0)
            for u in users:
                if u != 'csrfmiddlewaretoken':
                    try:
                        ta = TestAttendance.objects.get(mdluser_id = users[u], test_id = tid)
                        print ta.id, " => Exits"
                    except:
                        fossmdlcourse = FossMdlCourses.objects.get(foss_id = test.foss_id)
                        ta = TestAttendance()
                        ta.test_id = test.id
                        ta.mdluser_id = users[u]
                        ta.mdlcourse_id = fossmdlcourse.mdlcourse_id
                        ta.mdlquiz_id = fossmdlcourse.mdlquiz_id
                        ta.mdlattempt_id = 0
                        ta.status = 0
                        ta.save()
                        print ta.id, " => Inserted"
                    if ta:
                        #todo: if the status = 2 check in moodle if he completed the test set status = 3 (completed)
                        t = TestAttendance.objects.get(mdluser_id = ta.mdluser_id, test_id = tid)
                        t.status = 1
                        t.save()
                        #enroll to the course
                        #get the course enrole id
                        #todo: If mark absent delete enrolement
                        try:
                            mdlenrol = MdlEnrol.objects.get(enrol='self', courseid=2)
                            print "Role Exits!"
                        except Exception, e:
                            print "MdlEnrol => ", e
                            print "No self enrolement for this course"
                            
                        try:
                            MdlUserEnrolments.objects.get(enrolid = mdlenrol.id, userid = ta.mdluser_id)
                            print "MdlUserEnrolments Exits!"
                            #update dateTime
                        except Exception, e:
                            print "MdlUserEnrolments => ", e
                            MdlUserEnrolments.objects.create(enrolid = mdlenrol.id, userid = ta.mdluser_id, status = 0, timestart = datetime.datetime.now().strftime("%s"), timeend = 0, modifierid = ta.mdluser_id, timecreated = datetime.datetime.now().strftime("%s"), timemodified = datetime.datetime.now().strftime("%s"))
        
    participant_ids = list(WorkshopAttendance.objects.filter(workshop_id = test.workshop_id).values_list('mdluser_id'))
    mdlids = []
    wp = None
    for k in participant_ids:
        mdlids.append(k[0])
    if mdlids:
        wp = MdlUser.objects.filter(id__in = mdlids)
    context = {}
    context['collection'] = wp
    context['test'] = test
    context.update(csrf(request))
    return render(request, 'events/templates/test/attendance.html', context)

@login_required
def test_participant(request, tid=None):
    user = request.user
    can_download_certificate = 0
    if tid:
        try:
            t = Test.objects.get(id=tid)
        except:
            raise Http404('Page not found')
            
        test_mdlusers = TestAttendance.objects.using('default').filter(test_id=tid).values_list('mdluser_id')
        ids = []
        print test_mdlusers
        for tp in test_mdlusers:
            ids.append(tp[0])
            
        tp = MdlUser.objects.using('moodle').filter(id__in=ids)
        if user == t.organiser or user == t.invigilator:
            can_download_certificate = 1
        context = {'collection' : tp, 'wc' : t, 'can_download_certificate':can_download_certificate}
        return render(request, 'events/templates/test/test_participant.html', context)

def test_participant_ceritificate(request, wid, participant_id):
    #response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    #p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    #p.drawString(200, 500, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    #p.showPage()
    #p.save()
    #return response
    # Using ReportLab to insert image into PDF
    
    #store Certificate details
    
    certificate_pass = ''
    if wid and participant_id:
        try:
            w = Test.objects.get(id = wid)
            mdluser = MdlUser.objects.get(id = participant_id)
            ta = TestAttendance.objects.get(test_id = w.id, mdluser_id = participant_id)
            mdlgrade = MdlQuizGrades.objects.get(quiz = ta.mdlquiz_id, userid = participant_id)
            print "ss"
            if ta.status < 1 or round(mdlgrade.grade, 1) < 40:
                raise Http404('Page not found')
                
            if ta.password:
                certificate_pass = ta.password 
                ta.count += 1
                ta.status = 4
                ta.save() 
            else: 
                certificate_pass = str(mdluser.id)+id_generator(10-len(str(mdluser.id)))
                ta.password = certificate_pass 
                ta.status = 4
                ta.count += 1
                ta.save()
        except Exception, e:
            print e
            raise Http404('Page not found')
    response = HttpResponse(mimetype='application/pdf')
    filename = (mdluser.firstname+'-'+w.foss.foss+"-Participant-Certificate").replace(" ", "-");
    
    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'
    imgTemp = StringIO()
    imgDoc = canvas.Canvas(imgTemp)

    # Title 
    #imgDoc.setFont('Helvetica', 40, leading=None)
    #imgDoc.drawCentredString(415, 480, "Certificate for Completion of c ")
    
    imgDoc.setFont('Helvetica', 18, leading=None)
    imgDoc.drawCentredString(175, 115, custom_strftime('%B {S} %Y', w.tdate))
    
    #password
    imgDoc.setFillColorRGB(211, 211, 211)
    imgDoc.setFont('Helvetica', 10, leading=None)
    imgDoc.drawString(10, 6, certificate_pass)
    #imgDoc.drawString(100, 100, 'transparent')
    

    # Draw image on Canvas and save PDF in buffer
    imgPath = "/home/deer/sign.jpg"
    imgDoc.drawImage(imgPath, 600, 100, 150, 76)    ## at (399,760) with size 160x160
    
    #paragraphe
    text = "This is to certify that <b>"+ta.mdluser_firstname +" "+ta.mdluser_lastname+"</b> has sucessfully completed <b>"+w.foss.foss+"</b> test organized at <b>"+w.academic.institution_name+"</b> by <b>"+w.invigilator.username+"</b>  with course material provided by the Take To A Teacher project at IIT Bombay.  <br /><br /><p>pasing on online exam, conducted remotly from IIT Bombay, is a pre-requisite for completing this workshop. <b>"+w.organiser.username+"</b> at <b>"+w.academic.institution_name+"</b> invigilated this examination. This workshop is offered by the <b>Spoken Tutorial project, IIT Bombay, funded by National Mission on Education through ICT, MHRD, Govt of India.</b></p>"
    
    centered = ParagraphStyle(name = 'centered',
        fontSize = 16,  
        leading = 30,  
        alignment = 0,  
        spaceAfter = 20)

    p = Paragraph(text, centered)
    p.wrap(700, 200)
    p.drawOn(imgDoc, 4.2 * cm, 6 * cm)
    
    #paragraphe
    text = "Certificate for Completion of "+w.foss.foss+" Workshop"
    
    centered = ParagraphStyle(name = 'centered',
        fontSize = 40,  
        leading = 50,  
        alignment = 1,  
        spaceAfter = 20)

    p = Paragraph(text, centered)
    p.wrap(500, 200)
    p.drawOn(imgDoc, 6.2 * cm, 16 * cm)

    imgDoc.save()

    # Use PyPDF to merge the image-PDF into the template
    page = PdfFileReader(file("/home/deer/Blank-Certificate.pdf","rb")).getPage(0)
    overlay = PdfFileReader(StringIO(imgTemp.getvalue())).getPage(0)
    page.mergePage(overlay)

    #Save the result
    output = PdfFileWriter()
    output.addPage(page)
    
    #stream to browser
    outputStream = response
    output.write(response)
    outputStream.close()

    return response

def student_subscribe(request, events, eventid = None, mdluser_id = None):
    try:
        mdluser = MdlUser.objects.get(id = mdluser_id)
        if events == 'test':
            try:
                TestAttendance.objects.create(test_id=eventid, mdluser_id = mdluser_id, mdluser_firstname = mdluser.firstname, mdluser_lastname = mdluser.lastname)
            except Exception, e:
                print e
                pass
            messages.success(request, "You have sucessfully subscribe to the "+events+"!")
            return HttpResponseRedirect('/moodle/index/#Upcoming-Test')
        elif events == 'workshop':
            try:
                WorkshopAttendance.objects.create(workshop_id=eventid, mdluser_id = mdluser_id)
            except Exception, e:
                print e
                pass
            messages.success(request, "You have sucessfully subscribe to the "+events+"!")
            return HttpResponseRedirect('/moodle/index/#Upcoming-Workshop')
        else:
            raise Http404('Page not found')
    except:
        raise Http404('Page not found')
    
    return HttpResponseRedirect('/moodle/index/')

#Ajax Request and Responces
@csrf_exempt
def ajax_ac_state(request):
    """ Ajax: Get University, District, City based State selected """
    if request.method == 'POST':
        state = request.POST.get('state')
        data = {}
        if request.POST.get('fields[district]'):
            district = District.objects.filter(state=state)
            tmp = ''
            for i in district:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
                
            if(tmp):
                data['district'] = '<option value = None> -- None -- </option>'+tmp
            else:
                data['district'] = tmp
            
        if request.POST.get('fields[city]'):
            city = City.objects.filter(state=state)
            tmp = ''
            for i in city:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
                
            if(tmp):
                data['city'] = '<option value = None> -- None -- </option>'+tmp
            else:
                data['city'] = tmp
            
        if request.POST.get('fields[university]'):
            university = University.objects.filter(state=state)
            tmp = ''
            for i in university:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
            if(tmp):
                data['university'] = '<option value = None> -- None -- </option>'+tmp
            else:
                data['university'] = tmp
        
        return HttpResponse(json.dumps(data), mimetype='application/json')
        
@csrf_exempt
def ajax_ac_location(request):
    """ Ajax: Get the location based on district selected """
    if request.method == 'POST':
        district = request.POST.get('district')
        location = Location.objects.filter(district=district)
        tmp = '<option value = None> -- None -- </option>'
        for i in location:
            tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
        return HttpResponse(json.dumps(tmp), mimetype='application/json')

@csrf_exempt
def ajax_district_data(request):
    """ Ajax: Get the location based on district selected """
    data = {}
    if request.method == 'POST':
        tmp = ''
        district = request.POST.get('district')
        print district
        print "ddddddddddddd"
        if request.POST.get('fields[location]'):
            location = Location.objects.filter(district_id=district)
            tmp = '<option value = None> -- None -- </option>'
            for i in location:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
            data['location'] = tmp
        
        if request.POST.get('fields[institute]'):
            collages = AcademicCenter.objects.filter(district=district)
            tmp = '<option value = None> -- None -- </option>'
            for i in collages:
                tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
            data['institute'] = tmp
        
    return HttpResponse(json.dumps(data), mimetype='application/json')

@csrf_exempt
def ajax_ac_pincode(request):
    """ Ajax: Get the pincode based on location selected """
    if request.method == 'POST':
        location = request.POST.get('location')
        location = Location.objects.get(pk=location)
        return HttpResponse(json.dumps(location.pincode), mimetype='application/json')

@csrf_exempt
def ajax_district_collage(request):
    """ Ajax: Get the Colleges (Academic) based on District selected """
    if request.method == 'POST':
        district = request.POST.get('district')
        collages = AcademicCenter.objects.filter(district=district)
        tmp = '<option value = None> -- None -- </option>'
        for i in collages:
            tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
        return HttpResponse(json.dumps(tmp), mimetype='application/json')

@csrf_exempt
def ajax_dept_foss(request):
    """ Ajax: Get the dept and foss based on workshop selected """
    data = {}
    if request.method == 'POST':
        tmp = ''
        workshop = request.POST.get('workshop')
        print request.POST.get('fields[foss]')
        print "************"
        if request.POST.get('fields[dept]'):
            dept = Department.objects.filter(workshop__id = workshop)
            for i in dept:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
            data['dept'] = tmp
        
        if request.POST.get('fields[foss]'):
            workshop = Workshop.objects.filter(pk=workshop)
            tmp = '<option value = None> -- None -- </option>'
            if workshop:
                tmp +='<option value='+str(workshop[0].foss.id)+'>'+workshop[0].foss.foss+'</option>'
            data['foss'] = tmp
        
    return HttpResponse(json.dumps(data), mimetype='application/json')

@csrf_exempt
def test(request):
    return render_to_response('events/templates/test/test.html', { 'foo': 123, 'bar': 456 })
