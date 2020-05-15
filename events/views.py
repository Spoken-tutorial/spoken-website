from django.core.exceptions import PermissionDenied

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.views.decorators.csrf import csrf_exempt

from django.http import Http404
from django.db.models import Q
from django.db import IntegrityError

try:
    from urllib.parse import urlparse
except ImportError:
    from urllib.parse import urlparse

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import xml.etree.cElementTree as etree
from django.conf import settings
import json
import os,time, csv, random, string
from validate_email import validate_email

import os.path

try:
    import urllib.request, urllib.error, urllib.parse
except ImportError:
    import urllib.request as urllib2

from events.models import *
from cms.models import Profile
from mdldjango.forms import OfflineDataForm

from .forms import *
from django.utils import formats
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mdldjango.get_or_create_participant import get_or_create_participant, check_csvfile, update_participants_count, clone_participant
from mdldjango.helper import get_moodle_user
from django.template.defaultfilters import slugify

#pdf generate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from PyPDF2 import PdfFileWriter, PdfFileReader
from django.template.context_processors import csrf

from io import StringIO, BytesIO


#randon string
import string
import random

from  .filters import *
from cms.views import create_profile
from cms.sortable import *
from .events_email import send_email
import datetime
from django.http import JsonResponse


def can_clone_training(training):
    if training.tdate > datetime.datetime.strptime('01-02-2015', "%d-%m-%Y").date() and training.organiser.academic.institution_type.name != 'School':
        return True
    return False

def _get_training_participant(training):
    #if training.organiser.academic.institution_type.name == "School":
    #    if training.status == 4:
    #        return SchoolTrainingAttendance.objects.filter(training = training, status__gte=1)
    #    return SchoolTrainingAttendance.objects.filter(training = training)
    #else:
    participants = None
    if training.status == 4:
        participants = TrainingAttendance.objects.filter(training = training, status__gte=1)
    else:
        participants = TrainingAttendance.objects.filter(training = training)
    return participants

def _mark_training_attendance(training, participant_id):
    #if training.organiser.academic.institution_type.name == "School":
    #    ta = SchoolTrainingAttendance.objects.get(id = participant_id, training = training)
    #    ta.status = 1
    #    ta.save()
    #else:
    try:
        ta = TrainingAttendance.objects.get(id = participant_id, training = training)
        ta.status = 1
        ta.save()
    except:
        ta = TrainingAttendance()
        ta.training = training
        ta.mdluser_id = participant_id
        ta.status = 1
        ta.save()

def _mark_all_training_participants_to_zero(training):
    #if training.organiser.academic.institution_type.name == "School":
    #    SchoolTrainingAttendance.objects.filter(training = training).update(status = 0)
    #else:
    TrainingAttendance.objects.filter(training = training).update(status = 0)

@login_required
def init_events_app(request):
    try:
        # Group
        if Group.objects.filter(name = 'Resource Person').count() == 0:
            Group.objects.create(name = 'Resource Person')
        if Group.objects.filter(name = 'Organiser').count() == 0:
            Group.objects.create(name = 'Organiser')
        if Group.objects.filter(name = 'Invigilator').count() == 0:
            Group.objects.create(name = 'Invigilator')

        #testcategory
        try:
            TestCategory.objects.get_or_create(name= 'Workshop')
            TestCategory.objects.get_or_create(name= 'Training')
            TestCategory.objects.get_or_create(name= 'Others')
        except Exception as e:
            print((e, "test_category"))

        try:
            InstituteType.objects.get_or_create(name= 'Workshop')
            InstituteType.objects.get_or_create(name= 'Training')
            InstituteType.objects.get_or_create(name= 'ITI')
            InstituteType.objects.get_or_create(name= 'Vocational')
            InstituteType.objects.get_or_create(name= 'School')
            InstituteType.objects.get_or_create(name= 'Uncategorised')
        except Exception as e:
            print((e, "institute_type"))

        #institutecategory
        try:
            InstituteCategory.objects.get_or_create(name= 'Govt')
            InstituteCategory.objects.get_or_create(name= 'Private')
            InstituteCategory.objects.get_or_create(name= 'NGO')
            InstituteCategory.objects.get_or_create(name= 'Uncategorised')
        except Exception as e:
            print((e, "InstituteCategory"))

        #permissiontype
        try:
            PermissionType.objects.get_or_create(name= 'State')
            PermissionType.objects.get_or_create(name= 'District')
            PermissionType.objects.get_or_create(name= 'University')
            PermissionType.objects.get_or_create(name= 'Institution Type')
            PermissionType.objects.get_or_create(name= 'Institution')
        except Exception as e:
             print((e, "PermissionType"))

        #state
        state = None
        try:
            state = State.objects.get_or_create(name= 'Uncategorised')
        except Exception as e:
             print((e, "State"))
        #District
        try:
            District.objects.get_or_create(name= 'Uncategorised', state_id = state[0].id)
        except Exception as e:
             print((e, "District"))

        #City
        try:
            City.objects.get_or_create(name= 'Uncategorised', state_id = state[0].id)
        except Exception as e:
             print((e, "City"))

        #University
        try:
            University.objects.get_or_create(name= 'Uncategorised', state_id = state[0].id, user_id = 1)
        except Exception as e:
             print((e, "University"))

        messages.success(request, 'Events application initialised successfully!')
    except Exception as e:
        messages.error(request, str(e))
    return HttpResponseRedirect('/software-training/')

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

def is_accountexecutive(user):
    """Check if the user is having accountexecutive rights"""
    try:
        if user.groups.filter(name='Account Executive').count() == 1 and user.accountexecutive.status == 1:
            return True
    except:
        pass

def is_organiser_deactivated(user):
    try:
        if user.organiser and user.organiser.status == 3:
            return True
    except:
        pass

def is_invigilator_deactivated(user):
    try:
        if user.invigilator and user.invigilator.status == 3:
            return True
    except:
        pass

def is_organiser(user):
    """Check if the user is having organiser rights"""
    try:
        if user.groups.filter(name='Organiser').count() == 1 and user.organiser and user.organiser.status == 1:
            return True
    except:
        pass

def is_administrator(user):
    """Check if the user is having resource person  rights"""
    if user.groups.filter(name='Administrator').count() == 1:
        return True

def is_invigilator(user):
    """Check if the user is having invigilator rights"""
    if user.groups.filter(name='Invigilator').count() == 1 and user.invigilator and user.invigilator.status == 1:
        return True


def get_page(resource, page, limit=20):
    paginator = Paginator(resource, limit)
    if page is None:
        page = 1
    try:
        resource = paginator.page(page)
    except PageNotAnInteger:
        resource = paginator.page(1)
    except EmptyPage:
        resource = paginator.page(paginator.num_pages)
    return resource


def search_participant(form):
    if form.is_valid():
        onlinetest_user = {}
        if form.cleaned_data['email']:
            onlinetest_user  = MdlUser.objects.filter(email = form.cleaned_data['email'])
        #else:
        #    onlinetest_user  = MdlUser.objects.filter(Q(username__icontains = form.cleaned_data['username']) | Q(firstname__icontains = form.cleaned_data['username']))
        if not onlinetest_user:
            onlinetest_user = 'None'
        return onlinetest_user

def add_participant(request, cid, category ):
    userid = request.POST['userid']
    if userid:
        if category == 'Training':
            try:
                wa = TrainingAttendance.objects.get(mdluser_id = userid, training_id = cid)
                print((wa.id, " => Exits"))
                messages.success(request, "User has already in the attendance list")
            except:
                mdluser = MdlUser.objects.get(pk=userid)
                wa = TrainingAttendance()
                wa.training_id = cid
                wa.mdluser_id = mdluser.id
                wa.firstname = mdluser.firstname
                wa.lastname = mdluser.lastname
                wa.email = mdluser.email
                wa.gender = mdluser.gender
                wa.status = 0
                wa.save()
                messages.success(request, "User has added in the attendance list")
                print((wa.id, " => Inserted"))
        elif category == 'Training':
            try:
                wa = TrainingAttendance.objects.get(mdluser_id = userid, training_id = cid)
                print((wa.id, " => Exits"))
                messages.success(request, "User has already in the attendance list")
            except:
                wa = TrainingAttendance()
                wa.training_id = cid
                wa.mdluser_id = userid
                wa.status = 0
                wa.save()
                messages.success(request, "User has added in the attendance list")
                print((wa.id, " => Inserted"))

        elif category == 'Test':
            try:
                wa = TestAttendance.objects.get(mdluser_id = userid, test_id = cid)
                print((wa.id, " => Exits"))
                messages.success(request, "User has already in the attendance list")
            except:
                wa = TestAttendance()
                wa.test_id = cid
                wa.mdluser_id = userid
                wa.status = 0
                wa.save()
                messages.success(request, "User has added in the attendance list")
                print((wa.id, " => Inserted"))

def fix_date_for_first_training(request):
    organisers = Organiser.objects.exclude(id__in = Training.objects.values_list('organiser_id').distinct(), status=1).filter(Q(created__startswith=datetime.date.today() - datetime.timedelta(days=15)) | Q(created__startswith=datetime.date.today() - datetime.timedelta(days=30)))
    if organisers:
        status = 'Fix a date for your first training'
        for o in organisers:
            try:
                to = [o.user.email]
                send_email(status, to)
            except:
                pass
    return HttpResponse("Done!")

#def training_gentle_reminder(request):
#    tomorrow_training = Training.objects.filter(training_type__gt=0, status__lte=2, tdate=datetime.date.today() + datetime.timedelta(days=1))
#    if tomorrow_training:
#        for t in tomorrow_training:
#            status = 'How to upload the attendance on the Workshop day'
#            try:
#                to = [t.organiser.user.email]
#                #if t.training_type == 0:
#                #    status = 'How to upload the attendance on the Training day'
#                send_email(status, to, t)
#            except:
#                pass
#    return HttpResponse("Done!")

#def reminder_mail_to_close_training(request):
#    predated_ongoing_workshop = Training.objects.filter(Q(status = 2) | Q(status = 3), training_type__gte = 0, tdate__lt = datetime.date.today() - datetime.timedelta(days = 1))
#    if predated_ongoing_workshop:
#        status = "Reminder mail to close Training"
#        for w in predated_ongoing_workshop:
#            try:
#                to = [w.organiser.user.email]
#                send_email(status, to, w)
#            except:
#                pass
#    return HttpResponse("Done!")

#def training_completion_reminder(request):
#    training_need_to_complete = Training.objects.filter(training_type = 0, status__lte = 3, tdate__lte=datetime.date.today() - datetime.timedelta(days=30))
#    if training_need_to_complete:
#        status = 'How to upload the attendance on the Training day'
#        for t in training_need_to_complete:
#            try:
#                to = [t.organiser.user.email]
#                send_email(status, to, t)
#            except:
#                pass
#    return HttpResponse("Done!")

# only for workshop, pilot, live workshop
def close_predated_ongoing_workshop(request):
    predated_ongoing_workshop = Training.objects.filter(status = 3, training_type__gte = 0, tdate__lt = datetime.date.today() - datetime.timedelta(days = 2))
    if predated_ongoing_workshop:
        for w in predated_ongoing_workshop:
            try:
                present = TrainingAttendance.objects.filter(training = w, status__gte = 1).count()
                absentees = TrainingAttendance.objects.filter(training = w, status = 0).count()
                if not present and not absentees:
                    continue
                if present:
                    final_count = present
                else:
                    final_count = absentees
                    TrainingAttendance.objects.filter(training = w, status = 0).update(status = 1)

                w.participant_count = final_count
                w.status = 4
                w.trusted = 0
                w.save()
            except:
                pass
    return HttpResponse("Done!")

# Mark as complelete when invigilator forgot to close the Test
def close_predated_ongoing_test(request):
    predated_ongoing_test = Test.objects.filter(status = 3, tdate__lt = datetime.date.today())
    if predated_ongoing_test:
        for t in predated_ongoing_test:
            try:
                present = TestAttendance.objects.filter(test = t, status__gt = 1).count()
                # absentees = TestAttendance.objects.filter(test = t, status = 0).count()
                if present:
                    TestAttendance.objects.filter(test_id=t.id, status = 2).update(status = 3)
                    t.participant_count = present
                    t.status = 4
                    t.save()
            except:
                pass
    return HttpResponse("Done!")

def get_academic_code(state):
    # find the academic code available number
    try:
        ac = AcademicCenter.objects.filter(state = state).order_by('-academic_code')[:1].get()
    except:
        #print "This is first record"
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
    return state_code +'-'+ ac_code

@login_required
def old_training_attendance(request):
    user = request.user
    context = {}
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied()
    collectionSet = Training.objects.exclude(id__in=TrainingAttendance.objects.all().values_list('training_id').distinct()).filter(status=4, academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)))
    if not collectionSet:
        raise PermissionDenied()
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('training_type', True, 'Training Type'),
        3: SortableHeader('academic__state', True, 'State'),
        4: SortableHeader('academic__academic_code', True, 'Academic Code'),
        5: SortableHeader('academic', True, 'Institution'),
        6: SortableHeader('foss', True, 'FOSS'),
        7: SortableHeader('organiser__user', True, 'Organiser'),
        8: SortableHeader('tdate', True, 'Date'),
        9: SortableHeader('Participants', False),
        10: SortableHeader('Action', False)
    }

    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collectionSet, header, raw_get_data)
    ordering = get_field_index(raw_get_data)
    collection = TrainingFilter(request.GET, user = user, queryset=collection)
    context['form'] = collection.form

    page = request.GET.get('page')
    collection = get_page(collection, page)

    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering
    context.update(csrf(request))
    return render(request, 'events/templates/training/old-index.html', context)

def old_training_attendance_upload(request, wid):
    user = request.user
    form = OfflineDataForm()
    enable_form = True
    try:
        training = Training.objects.get(pk=wid, status=4)
        if TrainingAttendance.objects.filter(training=training).count():
            messages.info(request, "You have already submited the training attendance!")
            return HttpResponseRedirect('/software-training/training/old-training-attendance/')
    except Exception as e:
        raise PermissionDenied('You are not allowed to view this page!')
    if request.method == 'POST':
        form = OfflineDataForm(request.POST, request.FILES)
        if form.is_valid():
            file_path = settings.MEDIA_ROOT + 'training/' + str(wid) + str(time.time())
            f = request.FILES['xml_file']
            fout = open(file_path, 'wb+')
            for chunk in f.chunks():
                fout.write(chunk)
            fout.close()
            error_line_no = ''
            csv_file_error = 0
            csv_file_error, error_line_no = check_csvfile(user, file_path, training, 3)
            if not csv_file_error:
                csv_file_error, error_line_no = check_csvfile(user, file_path, training, 1)
            os.unlink(file_path)
            #update participant count
            #update_participants_count(training)
            if error_line_no:
                messages.error(request, error_line_no)
            else:
                enable_form = False
                messages.info(request, "Thank you for submitting attendance!. Now you can download the certificate.")
                #return HttpResponseRedirect('/software-training/training/old-training-attendance/')
    context = {
        'form': form,
        'enable_form' : enable_form
    }
    if enable_form:
        messages.info(request, """
            Please upload the CSV file which you have generated.
        To know more <a href="http://process.spoken-tutorial.org/images/9/96/Upload_Attendance.pdf" target="_blank">Click here</a>.
        <br><b>Note: Participant list should not be exced {0}</b>
        """.format(training.participant_count))
    context.update(csrf(request))
    return render(request, 'events/templates/training/old-attendance.html', context)

@login_required
def events_dashboard(request):
    user = request.user
    user_roles = user.groups.all()
    roles = []
    events_roles = ['Resource Person', 'Organiser', 'Invigilator']
    for role in user_roles:
        if role.name in events_roles:
            roles.append(role.name)

    # print roles

    organiser_workshop_notification = None
    organiser_test_notification = None
    invigilator_test_notification = None
    organiser_training_notification = None
    rp_workshop_notification = None
    rp_test_notification = None
    rp_training_notification = None
    institute_name = None

    if is_organiser(user):
        institution_type = AcademicCenter.objects.get(id=user.organiser.academic_id)
        institute_name = InstituteType.objects.get(id=institution_type.institution_type_id)
        organiser_test_notification = EventsNotification.objects.filter((Q(status = 1) | Q(status = 2)), category = 1, academic_id = user.organiser.academic_id, categoryid__in = user.organiser.academic.test_set.filter(organiser_id = user.id).values_list('id')).order_by('-created')[:30]

        organiser_test_notification = \
            EventsNotification.objects.filter(Q(status=1)
                | Q(status=2), category=1,
                academic_id=user.organiser.academic_id,
                categoryid__in=user.organiser.academic.test_set.filter(organiser_id=user.id).values_list('id'
                )).order_by('-created')[:30]

        # organiser_training_notification = EventsNotification.objects.filter((Q(status = 1) | Q(status = 3)), category = 2, status = 1, academic_id = user.organiser.academic_id, categoryid__in = user.organiser.academic.workshop_set.filter(organiser_id = user.id).values_list('id')).order_by('-created')[:30]

    if is_resource_person(user):
        rp_workshop_notification = \
            EventsNotification.objects.filter(Q(status=0) | Q(status=5)
                | Q(status=2), category=0).order_by('-created')[:30]
        rp_training_notification = \
            EventsNotification.objects.filter(Q(status=0) | Q(status=5)
                | Q(status=2), category=2).order_by('-created')[:30]
        rp_test_notification = \
            EventsNotification.objects.filter(Q(status=0) | Q(status=4)
                | Q(status=5) | Q(status=8) | Q(status=9), category=1,
                categoryid__in=Training.objects.filter(academic__in=AcademicCenter.objects.filter(state__in=State.objects.filter(resourceperson__user_id=user,
                resourceperson__status=1))).values_list('id'
                )).order_by('-created')[:30]
    if is_invigilator(user):
        invigilator_test_notification = \
            EventsNotification.objects.filter(Q(status=0)
                | Q(status=1), category=1,
                academic_id=user.invigilator.academic_id,
                categoryid__in=user.invigilator.academic.test_set.filter(invigilator_id=user.id).values_list('id'
                )).order_by('-created')[:30]

    context = {
        'roles': roles,
        'institution_type': institute_name,
        'organiser_workshop_notification': organiser_workshop_notification,
        'organiser_test_notification': organiser_test_notification,
        'organiser_training_notification': organiser_training_notification,
        'rp_test_notification': rp_test_notification,
        'rp_workshop_notification': rp_workshop_notification,
        'rp_training_notification': rp_training_notification,
        'invigilator_test_notification': invigilator_test_notification,
        }
    return render(request, 'events/templates/events_dashboard.html',
                  context)

@login_required
def delete_events_notification(request, notif_type, notif_id):
    notif_rec = None
    try:
        if notif_type == "organiser":
            notif_rec = EventsNotification.objects.select_related().get(pk = notif_id)
        elif notif_type == "invigilator":
            notif_rec = EventsNotification.objects.select_related().get(pk = notif_id)
        elif notif_type == "rp":
            notif_rec = EventsNotification.objects.select_related().get(pk = notif_id)
    except Exception as e:
        print(e)
        messages.warning(request, 'Selected notification is already deleted (or) You do not have permission to delete it.')
    if notif_rec:
        notif_rec.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def clear_events_notification(request, notif_type):
    notif_rec = None
    try:
        if notif_type == "organiser":
            notif_rec = EventsNotification.objects.filter(user = request.user).delete()
        elif notif_type == "invigilator":
            notif_rec = EventsNotification.objects.filter(user = request.user).delete()
        elif notif_type == "rp":
            notif_rec = EventsNotification.objects.filter(user = request.user).delete()
    except Exception as e:
        print(e)
        messages.warning(request, 'Something went wrong, contact site administrator.')

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def new_ac(request):
    """ Create new academic center. Academic code generate by autimatic.
        if any code missing in between first assign that code then continue the serial
    """
    user = request.user
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied()

    if request.method == 'POST':
        form = AcademicForm(user, request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user_id = user.id

            state = form.cleaned_data['state']
            academic_code = get_academic_code(state)

            form_data.academic_code = academic_code
            ic = InstituteCategory.objects.get(name = 'Uncategorised')
            form_data.institute_category = ic
            form_data.save()
            messages.success(request, form_data.institution_name+" has been added")
            return HttpResponseRedirect("/software-training/ac/")

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
        raise PermissionDenied()

    if request.method == 'POST':
        academic = AcademicCenter.objects.get(id = rid)
        form = AcademicForm(request.user, request.POST, instance=academic)
        if form.is_valid():
            #change academic_code if state change
            form_state = form.cleaned_data['state']
            if academic.state_id != form_state:
                form_data = form.save(commit=False)
                form_data.academic_code = get_academic_code(form_state)
            if form.save():
                return HttpResponseRedirect("/software-training/ac/")
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
            raise PermissionDenied()

@login_required
def ac(request):
    """ Academic index page """
    user = request.user
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied()

    context = {}
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('State', False),
        3: SortableHeader('academic_code', True, 'Academic Code'),
        4: SortableHeader('institution_name', True, 'Institution Name'),
        5: SortableHeader('university__name', True, 'University'),
        6: SortableHeader('institution_type__name', True, 'Institute Type'),
        7: SortableHeader('Action', False)
    }

    collectionSet = AcademicCenter.objects.filter(state__in = user.resource_person.filter(resourceperson__status=1))
    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collectionSet, header, raw_get_data)
    ordering = get_field_index(raw_get_data)

    collection = AcademicCenterFilter(request.GET, user = user, queryset=collection)
    context['form'] = collection.form

    page = request.GET.get('page')
    collection = get_page(collection.qs, page)

    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering

    context.update(csrf(request))
    return render(request, 'events/templates/ac/index.html', context)
    return HttpResponse('RP')

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
def accountexecutive_request(request, username):
    """ request to bacome a new accountexecutive """
    user = request.user
    if not user.is_authenticated():
        raise PermissionDenied()

    if username == request.user.username:
        user = User.objects.get(username=username)
        


        if request.method == 'POST':
            form = AccountexecutiveForm(request.POST)
            if form.is_valid():
                user.groups.add(Group.objects.get(name='Account Executive'))
                accountexecutive = Accountexecutive()
                accountexecutive.user_id=request.user.id
                accountexecutive.academic_id=request.POST['college']
                try:
                    accountexecutive.save()
                except:
                    accountexecutive = Accountexecutive.objects.get(user = user)
                    accountexecutive.academic_id=request.POST['college']
                    accountexecutive.save()
                messages.success(request, "<ul><li>Thank you. Your request has been sent for Training Manager's approval.</li><li>You will get the approval with in 24 hours. Once the request is approved, you can proceed with the payment. </li></ul>")
                return HttpResponseRedirect("/software-training/accountexecutive/view/"+user.username+"/")
            messages.error(request, "Please fill the following details")
            context = {'form':form}
            return render(request, 'events/templates/accountexecutive/form.html', context)
        
        else:
            try:
                accountexecutive = Accountexecutive.objects.get(user=user)

                if accountexecutive.status == 1:
                    messages.error(request, "You are already an accountexecutive ")
                    return HttpResponseRedirect("/software-training/accountexecutive/view/"+user.username+"/")
                else:
                    messages.info(request, "Your Account Executive request is yet to be approved. Please contact the Resource person of your State. For more details <a href='http://process.spoken-tutorial.org/images/5/5d/Create-New-Account.pdf' target='_blank'> Click Here</a> ")
                    print("Accountexecutive not yet approve ")
                    return HttpResponseRedirect("/software-training/accountexecutive/view/"+user.username+"/")
            except:
                messages.info(request, "Please fill the following details")
                context = {}
                context.update(csrf(request))
                context['form'] = AccountexecutiveForm()
                return render(request, 'events/templates/accountexecutive/form.html', context)

    else:
        raise PermissionDenied()

@login_required
def accountexecutive_view(request, username):
    """ view accountexecutive details """
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied()

    context = {}
    try:
        user = User.objects.get(username=username)
        accountexecutive = Accountexecutive.objects.get(user=user)
        context['record'] = accountexecutive
        context['profile'] = accountexecutive.user.profile_set.get(user= user)
    except Exception as e:
        print(e)
        raise PermissionDenied()
    return render(request, 'events/templates/accountexecutive/view.html', context)

#@login_required
def accountexecutive_edit(request, username):
    """ view accountexecutive details """
    #todo: confirm event_manager and resource_center can edit accountexecutive details
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied()

    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = AccountexecutiveForm(request.POST)
        if form.is_valid():
            accountexecutive = Accountexecutive.objects.get(user=user)
            #accountexecutive.user_id=request.user.id
            accountexecutive.academic_id=request.POST['college']
            accountexecutive.save()
            messages.success(request, "Details has been updated")
            return HttpResponseRedirect("/software-training/accountexecutive/view/"+user.username+"/")
        context = {'form':form}
        return render(request, 'events/templates/accountexecutive/form.html', context)
    else:
            #todo : if any training and test under this accountexecutive disable the edit
            record = Accountexecutive.objects.get(user=user)
            context = {}
            context['form'] = AccountexecutiveForm(instance = record)
            context.update(csrf(request))
            return render(request, 'events/templates/accountexecutive/form.html', context)


@login_required
def organiser_request(request, username):
    """ request to bacome a new organiser """
    user = request.user
    if not user.is_authenticated():
        raise PermissionDenied()

    if username == request.user.username:
        user = User.objects.get(username=username)
        if request.method == 'POST':
            form = OrganiserForm(request.POST)
            if form.is_valid():
                user.groups.add(Group.objects.get(name='Organiser'))
                organiser = Organiser()
                organiser.user_id=request.user.id
                organiser.academic_id=request.POST['college']
                try:
                    organiser.save()
                except:
                    organiser = Organiser.objects.get(user = user)
                    organiser.academic_id=request.POST['college']
                    organiser.save()
                messages.success(request, "<ul><li>Thank you. Your request has been sent for Training Manager's approval.</li><li>You will get the approval with in 24 hours. Once the request is approved, you can request for the Training. </li><li>For more details <a target='_blank' href='http://process.spoken-tutorial.org/images/1/1f/Training-Request-Sheet.pdf'> Click Here</a></li></ul>")
                return HttpResponseRedirect("/software-training/organiser/view/"+user.username+"/")
            messages.error(request, "Please fill the following details")
            context = {'form':form}
            return render(request, 'events/templates/organiser/form.html', context)
        else:
            try:
                organiser = Organiser.objects.get(user=user)
                if not is_organiser(organiser):
                    messages.info(request, "Please fill the following details")
                    context = {}
                    context.update(csrf(request))
                    context['form'] = OrganiserForm()
                    return render(request, 'events/templates/organiser/form.html', context)
                if organiser.status:
                    messages.error(request, "You are already an Organiser ")
                    return HttpResponseRedirect("/software-training/organiser/view/"+user.username+"/")
                else:
                    messages.info(request, "Your Organiser request is yet to be approved. Please contact the Resource person of your State. For more details <a href='http://process.spoken-tutorial.org/images/5/5d/Create-New-Account.pdf' target='_blank'> Click Here</a> ")
                    print("Organiser not yet approve ")
                    return HttpResponseRedirect("/software-training/organiser/view/"+user.username+"/")
            except:
                pass

            messages.info(request, "Please fill the following details")
            context = {}
            context.update(csrf(request))
            context['form'] = OrganiserForm()
            return render(request, 'events/templates/organiser/form.html', context)
    else:
        raise PermissionDenied()

@login_required
def organiser_view(request, username):
    """ view organiser details """
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied()

    context = {}
    try:
        user = User.objects.get(username=username)
        organiser = Organiser.objects.get(user=user)
        context['record'] = organiser
        context['profile'] = organiser.user.profile_set.get(user= user)
    except Exception as e:
        print(e)
        raise PermissionDenied()
    return render(request, 'events/templates/organiser/view.html', context)

#@login_required
def organiser_edit(request, username):
    """ view organiser details """
    #todo: confirm event_manager and resource_center can edit organiser details
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied()

    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = OrganiserForm(request.POST)
        if form.is_valid():
            organiser = Organiser.objects.get(user=user)
            #organiser.user_id=request.user.id
            organiser.academic_id=request.POST['college']
            organiser.save()
            messages.success(request, "Details has been updated")
            return HttpResponseRedirect("/software-training/organiser/view/"+user.username+"/")
        context = {'form':form}
        return render(request, 'events/templates/organiser/form.html', context)
    else:
            #todo : if any training and test under this organiser disable the edit
            record = Organiser.objects.get(user=user)
            context = {}
            context['form'] = OrganiserForm(instance = record)
            context.update(csrf(request))
            return render(request, 'events/templates/organiser/form.html', context)

@login_required
def rp_organiser(request, status, code, userid):
    """ Resource person: active organiser """
    user = request.user
    organiser_in_rp_state = Organiser.objects.filter(user_id=userid, academic__in=AcademicCenter.objects.filter(state__in=State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)))
    if not (user.is_authenticated() and organiser_in_rp_state and ( is_event_manager(user) or is_resource_person(user) or (status == 'active' or status == 'block'))):
        raise PermissionDenied('You are not allowed to view this page ')

    try:
        if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
            organiser = Organiser.objects.get(user_id = userid)
            organiser.appoved_by_id = request.user.id
            message = "activated"
            organiser.status = 1
            if status == 'block':
                organiser.status = 2
                message = "blocked"
            organiser.save()
            messages.success(request, "The Organiser account has been "+message)
            return HttpResponseRedirect('/software-training/organiser/inactive/')
        else:
            raise PermissionDenied()
    except:
        raise PermissionDenied('You are not allowed to view this page')

@login_required
def invigilator_request(request, username):
    """ Request to bacome a invigilator """
    user = request.user
    if not user.is_authenticated():
        raise PermissionDenied()

    if username == user.username:
        user = User.objects.get(username=username)
        if request.method == 'POST':
            form = InvigilatorForm(request.POST)
            if form.is_valid():
                user.groups.add(Group.objects.get(name='Invigilator'))
                invigilator = Invigilator()
                invigilator.user_id=request.user.id
                invigilator.academic_id=request.POST['college']
                try:
                    invigilator.save()
                except:
                    invigilator = Invigilator.objects.get(user = user)
                    invigilator.academic_id=request.POST['college']
                    invigilator.save()

                messages.success(request, "Thank you. Your request has been sent for Training Manager's approval. You will get the approval with in 24 hours. Once the request is approved, you can request for the workshop. For more details Click Here")
                return HttpResponseRedirect("/software-training/invigilator/view/"+user.username+"/")
            messages.error(request, "Please fill the following details")
            context = {'form':form}
            return render(request, 'events/templates/invigilator/form.html', context)
        else:
            try:
                invigilator = Invigilator.objects.get(user=user)
                #todo: send status message
                if not is_invigilator(invigilator):
                    messages.info(request, "Please fill the following details")
                    context = {}
                    context.update(csrf(request))
                    context['form'] = InvigilatorForm()
                    return render(request, 'events/templates/invigilator/form.html', context)

                if invigilator.status:
                    messages.success(request, "You have already  invigilator role ")
                    return HttpResponseRedirect("/software-training/invigilator/view/"+user.username+"/")
                else:
                    messages.info(request, "<ul><li>Your Invigilator request is yet to be approved.</li><li>Please contact the Resource person of your State. For more details <a href='http://process.spoken-tutorial.org/images/5/5d/Create-New-Account.pdf' traget='_blank'>Click Here</a> </li></ul>")
                    return HttpResponseRedirect("/software-training/invigilator/view/"+user.username+"/")
            except:
                messages.info(request, "Please fill the following details")
                context = {}
                context.update(csrf(request))
                context['form'] = InvigilatorForm()
                return render(request, 'events/templates/invigilator/form.html', context)
    else:
        raise PermissionDenied()

@login_required
def invigilator_view(request, username):
    """ Invigilator view page """
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied()

    context = {}
    try:
        user = User.objects.get(username=username)
        invigilator = Invigilator.objects.get(user=user)
        context['record'] = invigilator
        context['profile'] = invigilator.user.profile_set.get(user= user)
    except Exception as e:
        print(e)
        raise PermissionDenied()
    return render(request, 'events/templates/invigilator/view.html', context)

@login_required
def invigilator_edit(request, username):
    """ Invigilator edit page """
    user = request.user
    if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied()

    user = User.objects.get(username=username)
    if request.method == 'POST':
        form = InvigilatorForm(request.POST)
        if form.is_valid():
            invigilator = Invigilator.objects.get(user=user)
            invigilator.academic_id=request.POST['college']
            invigilator.save()
            messages.success(request, "Details has been updated")
            return HttpResponseRedirect("/software-training/invigilator/view/"+user.username+"/")
        context = {'form':form}
        return render(request, 'events/templates/invigilator/form.html', context)
    else:
            #todo : if any training and test under this invigilator disable the edit
            record = Invigilator.objects.get(user=user)
            context = {}
            context['form'] = InvigilatorForm(instance = record)
            context.update(csrf(request))
            return render(request, 'events/templates/invigilator/form.html', context)

@login_required
def rp_invigilator(request, status, code, userid):
    """ Resource person: active invigilator """
    user = request.user
    invigilator_in_rp_state = Invigilator.objects.filter(user_id=userid, academic__in=AcademicCenter.objects.filter(state__in=State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)))
    if not (user.is_authenticated() and invigilator_in_rp_state and ( is_event_manager(user) or is_resource_person(user) or (status == 'active' or status == 'block'))):
        raise PermissionDenied('You are not allowed to view this page')

    try:
        if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
            invigilator = Invigilator.objects.get(user_id = userid)
            invigilator.appoved_by_id = request.user.id
            invigilator.status = 1
            message = "accepted"
            if status == 'block':
                invigilator.status = 2
                message = "blocked"
            invigilator.save()
            messages.success(request, "Invigilator has "+message)
            return HttpResponseRedirect('/software-training/invigilator/inactive/')
        else:
            raise PermissionDenied()
    except:
        raise PermissionDenied('You are not allowed to view this page')

@login_required
def rp_accountexecutive(request, status, code, userid):
    """ Resource person: active accountexecutive """
    user = request.user
    accountexecutive_in_rp_state = Accountexecutive.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)))
    if not (user.is_authenticated() and accountexecutive_in_rp_state and ( is_event_manager(user) or is_resource_person(user) or (status == 'active' or status == 'block'))):
        raise PermissionDenied('You are not allowed to view this page')

    try:
        if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
            accountexecutive = Accountexecutive.objects.get(user_id = userid)
            accountexecutive.appoved_by_id = request.user.id
            accountexecutive.status = 1
            message = "accepted"
            if status == 'block':
                accountexecutive.status = 2
                message = "blocked"
            accountexecutive.save()
            messages.success(request, "Accountexecutive has "+message)
            return HttpResponseRedirect('/software-training/accountexecutive/inactive/')
        else:
            raise PermissionDenied()
    except:
        raise PermissionDenied('You are not allowed to view this page')


@login_required
def training_request(request, role, rid = None):
    ''' Training request by organiser '''
    user = request.user
    context = {}
    if not (user.is_authenticated() and ( is_organiser(user) or is_resource_person(user) or is_event_manager(user))):
        raise PermissionDenied()
    form = None
    if request.method == 'POST':
        if rid:
            form = TrainingForm(request.POST, request.FILES, instance = Training.objects.get(pk = rid), user = request.user)
        else:
            form = TrainingForm(request.POST, request.FILES, user = request.user)
        if form.is_valid():
            #existing_training = Training.objects.filter(organiser = request.user.organiser, academic = request.user.organiser.academic, foss = request.POST['foss'], tdate = request.POST['tdate'])
            #if existing_training:
            #    messages.error(request, "You have already scheduled <b>"+ str(request.POST['tdate']) + "</b> training on <b>"+ str(master_training.tdate) + "</b>. Please select some other date.")
            #    break
            ####
            csv_file_error = 0
            error_line_no = ''
            wid = 1
            f = None
            file_path = settings.MEDIA_ROOT +'training/' + str(wid) + str(time.time())
            if 'xml_file' in request.FILES:
                f = request.FILES['xml_file']

            if f:
                fout = open(file_path, 'wb+')
                for chunk in f.chunks():
                    fout.write(chunk)
                fout.close()

                #validate file
                csv_file_error, error_line_no = check_csvfile(user, file_path, form_data = request.POST)
                #return
            ####
            if not csv_file_error:
                dateTime = request.POST['tdate'].split(' ')
                w = Training()
                if rid:
                    w = Training.objects.get(pk = rid)
                else:
                    w.organiser_id = user.organiser.id
                    w.academic = user.organiser.academic
                w.course_id = request.POST['course']
                if request.POST['no_of_lab_session'] == '1':
                    w.training_type = 1
                else:
                    w.training_type = request.POST['training_type']
                w.language_id = request.POST['language']
                w.foss_id = request.POST['foss']
                w.tdate = dateTime[0]
                w.ttime = '00:00'
                w.skype = request.POST['skype']

                error = 0
                try:
                    w.save()
                except IntegrityError:
                    error = 1
                    prev_training = Training.objects.filter(organiser = w.organiser_id, academic = w.academic, foss = w.foss_id, tdate = w.tdate, ttime = w.ttime)
                    if prev_training:
                        messages.error(request, "You have already scheduled <b>"+ w.foss.foss + "</b> training on <b>"+w.tdate + " "+ w.ttime + "</b>. Please select some other time.")
                except:
                    messages.error(request, "Sorry, Something went wrong. try again!")
                    error = 1

                if not error:
                    w.training_code = "WC-"+str(w.id)
                    w.department.clear()
                    for dept in form.cleaned_data.get('department'):
                        w.department.add(dept)
                    #if request.POST['training_type'] == '1':
                    if rid and w.extra_fields:
                        w.extra_fields.paper_name = request.POST['course_number']
                        w.extra_fields.no_of_lab_session = request.POST['no_of_lab_session']
                        w.extra_fields.save()
                    elif not rid and not w.extra_fields:
                        tef = TrainingExtraFields.objects.create(paper_name = request.POST['course_number'], no_of_lab_session = request.POST['no_of_lab_session'])
                        w.extra_fields_id = tef.id
                    elif rid and not w.extra_fields:
                        tef = TrainingExtraFields.objects.create(paper_name = request.POST['course_number'], no_of_lab_session = request.POST['no_of_lab_session'])
                        w.extra_fields_id = tef.id
                    else:
                       pass
                    #else:
                    #    if w.extra_fields:
                    #        eid = w.extra_fields_id
                    #        w.extra_fields_id = None
                    #        w.save()
                    #        TrainingExtraFields.objects.filter(pk=eid).delete()
                    w.status = 1
                    w.save()
                    #####
                    #get or create participants list
                    if f:
                        csv_file_error, error_line_no = check_csvfile(user, file_path, w, flag=1)
                        os.unlink(file_path)

                        #file the participant count
                        w.participant_count = TrainingAttendance.objects.filter(training = w, status__gte = 1).count()
                        w.save()
                    #####
                        '''messages.success(request, """
                            <ul>
                                <li>
                                    Before the Training/Workshop date upload the Participants name
                                    list. It is necessary for approving your Training/Workshop request.
                                </li>
                                <li>
                                    Please click on <b>Upload Participant Data</b> and upload the <b>
                                    CSV </b>(.csv) file which you have generated (using LibreOffice
                                    Calc / MS Excel) and click <b>Submit</b>.
                                </li>
                                <li>
                                    For more details on how to create the .csv file.
                                    Please <a href="http://process.spoken-tutorial.org/images/9/96/Upload_Attendance.pdf" target="_blank">Click here</a>
                                </li>
                            </ul>
                        """)'''
                    #update logs
                    message = None
                    if rid:
                        if w.training_type == 0:
                            message = w.academic.institution_name+" has updated training request for "+w.foss.foss+" on dated "+w.tdate
                        else:
                            message = w.academic.institution_name+" has updated a Workshop request for "+w.foss.foss+" on dated "+w.tdate
                    else:
                        if w.training_type == 0:
                            message = w.academic.institution_name+" has made a training request for "+w.foss.foss+" on dated "+w.tdate
                        else:
                            message = w.academic.institution_name+" has made a Workshop request for "+w.foss.foss+" on dated "+w.tdate

                    update_events_log(user_id = user.id, role = 0, category = 0, category_id = w.id, academic = w.academic_id, status = 0)
                    update_events_notification(user_id = user.id, role = 0, category = 0, category_id = w.id, academic = w.academic_id, status = 0, message = message)

                    if role == 'organiser' and not rid:
                        return HttpResponseRedirect("/software-training/training/" + str(w.id) + "/attendance/?clone=1")
                    return HttpResponseRedirect("/software-training/training/" + role + "/pending/")
            else:
                os.unlink(file_path)
                messages.error(request, error_line_no)
            messages.error(request, "Please fill the following details ")
            context = {'form' : form, 'role' : role, 'status' : 'request'}
            return render(request, 'events/templates/training/form.html', context)
    else:
        messages.info(request, """
            <ul>
        <li><b>TO HAVE YOUR TRAINING REQUEST APPROVED IT IS NECESSARY TO UPLOAD THE LIST OF PARTICIPANTS <a href="http://process.spoken-tutorial.org/images/9/96/Upload_Attendance.pdf" class="link alert-link" target="_blank"><b>Click Here</b></a></b></li>
        <li><b style="color:red;">PLEASE ENSURE THAT YOU FILL IN ONLY THE GENUINE EMAIL ID'S OF THE PARTICIPANTS / STUDENTS. IF THEY DON'T HAVE ANY, PLEASE HELP THEM CREATE ONE.</b></li>
        <li>Select a Timing in the Training Request where the chosen FOSS is relevant/useful/matching to the Course/Paper. </li>
        <li>One can also select FOSS which might not be relevant/matching to any Course/Paper.</li>
                <li>Please download a copy of tutorials on all the machines. For instructions to download tutorials <a href="http://process.spoken-tutorial.org/images/1/1b/Download-Tutorials.pdf" class="link alert-link" target="_blank">Click Here</a></li>
                <li>Please check if your machine is ready. For the Machine Readiness document <a href='http://process.spoken-tutorial.org/images/5/58/Machine-Readiness.pdf' class='link alert-link' target='_blank'> Click Here</a>.</li>
            </ul>
        """)
    if rid and not form:
        form = TrainingForm(instance = Training.objects.get(pk = rid), user = request.user)

    if not form:
         form = TrainingForm(user = request.user)

    context['form'] = form
    context['role'] = role
    context.update(csrf(request))
    return render(request, 'events/templates/training/form.html', context)

def copy_participant(training, participants):
    for p in participants:
        ta = TrainingAttendance()
        ta.training_id = training.id
        ta.mdluser_id = p.mdluser_id
        ta.status = 1
        ta.firstname = p.firstname
        ta.lastname = p.lastname
        ta.gender = p.gender
        ta.email = p.email
        ta.save()

@login_required
def training_clone(request, role, rid = None):
    ''' Training request by organiser '''
    user = request.user
    context = {}
    participant = None
    csv_file_error = 0
    if not (user.is_authenticated() and ( is_organiser(user) or is_resource_person(user) or is_event_manager(user))):
        raise PermissionDenied()

    if not rid and request.method=="POST" and 'clone-training' in request.POST:
        return HttpResponseRedirect('/software-training/training/organiser/'+str(request.POST['clone-training'])+'/clone/')
    master_training = None
    try:
        master_training = Training.objects.get(pk=rid)
        if not can_clone_training(master_training):
            raise PermissionDenied()
    except:
        raise PermissionDenied()

    form = TrainingReUseForm()
    if rid and request.method=="POST":
        form = TrainingReUseForm(request.POST, user = request.user)
        if form.is_valid():
            csv_file_error, error_line_no, reattempt_list,  more_then_two_per_day_list = clone_participant(master_training, request.POST)
            if csv_file_error:
                messages.error(request, error_line_no)
            existing_training = Training.objects.filter(organiser = request.user.organiser, academic = request.user.organiser.academic, foss = request.POST['foss'], tdate = request.POST['tdate'])
            if existing_training:
                csv_file_error = 1
                messages.error(request, "You have already scheduled <b>"+ str(request.POST['tdate']) + "</b> training on <b>"+ str(master_training.tdate) + "</b>. Please select some other date.")


            if not csv_file_error:# and request.POST.get('remove-error')):
                existing_emails = None
                if reattempt_list and more_then_two_per_day_list:
                    existing_emails = set(reattempt_list.split(',')).union(set(more_then_two_per_day_list.split(',')))
                elif reattempt_list:
                    existing_emails = reattempt_list.split(',')
                else:
                    existing_emails = more_then_two_per_day_list.split(',')
                participants = master_training.trainingattendance_set.exclude(email__in=existing_emails)
                if participants:
                    training = master_training
                    training.id = None
                    training.status = 1
                    training.appoved_by_id = None
                    training.foss = form.cleaned_data['foss']
                    training.language = form.cleaned_data['language']
                    training.tdate = form.cleaned_data['tdate']
                    training.extra_fields.id = None
                    training.extra_fields.save()
                    training.extra_fields_id = training.extra_fields.id
                    training.save()
                    training.training_code = "WC-" + str(training.id)
                    training.save()
                    copy_participant(training, participants)
                    messages.success(request, "Training has been created! ")
                    return HttpResponseRedirect("/software-training/training/" + str(training.id) + "/attendance/?clone=1")
                messages.error(request, "Participants are empty!")
    context['form'] = form
    context['role'] = role
    context['participant'] = participant
    context['error'] = csv_file_error
    context['rid'] = rid
    context.update(csrf(request))
    return render(request, 'events/templates/training/request-reuse.html', context)

@login_required
def training_list(request, role, status):
    """ Organiser index page """
    user = request.user
    if not (user.is_authenticated() and ( is_organiser(user) or is_resource_person(user) or is_event_manager(user))):
        raise PermissionDenied()

    status_dict = {'pending': 0, 'approved' : 2, 'completed' : 4, 'rejected' : 5, 'reschedule' : 2, 'ongoing': 2, 'predated' : ''}
    if status in status_dict:
        context = {}
        collectionSet = None
        if is_event_manager(user) and role == 'em':
            collectionSet = Training.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), status = status_dict[status])
        elif is_resource_person(user) and role == 'rp':
            if status == 'approved':
                collectionSet = Training.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), status = status_dict[status], tdate__gt=datetime.date.today()).order_by('-tdate')
            elif status == 'predated':
                collectionSet = Training.objects.filter((Q(status = 0) | Q(status = 1) | Q(status = 2) | Q(status = 3)), academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), tdate__lt=datetime.date.today()).order_by('-tdate')
            elif status =='ongoing':
                collectionSet = Training.objects.filter((Q(status = 2) | Q(status = 3)), academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), tdate__lte=datetime.date.today()).order_by('-tdate')
            elif status =='pending':
                collectionSet = Training.objects.filter((Q(status = 0) | Q(status = 1)), academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), tdate__gte = datetime.date.today()).order_by('-tdate')

            else:
                collectionSet = Training.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), status = status_dict[status]).order_by('-tdate')
        elif is_organiser(user) and role == 'organiser':
            if status == 'approved':
                collectionSet = Training.objects.filter(organiser__user = user, status = status_dict[status], tdate__gt=datetime.date.today()).order_by('-tdate')
            elif status == 'predated':
                collectionSet = Training.objects.filter((Q(status = 0) | Q(status = 1) | Q(status = 2) | Q(status = 3)), organiser__user = user, tdate__lt=datetime.date.today()).order_by('-tdate')
            elif status == 'ongoing':
                collectionSet = Training.objects.filter((Q(status = 2) | Q(status = 3)), organiser__user = user, tdate__lte=datetime.date.today()).order_by('-tdate')
            elif status == 'pending':
                collectionSet = Training.objects.filter((Q(status = 0) | Q(status = 1)), organiser__user = user, tdate__gte=datetime.date.today()).order_by('-tdate')
                #print collectionSet
            else:
                collectionSet = Training.objects.filter(organiser__user = user, status = status_dict[status]).order_by('-tdate')

        if collectionSet == None:
            raise PermissionDenied()

        header = {
            1: SortableHeader('#', False),
            2: SortableHeader('training_type', True, 'Training Type'),
            3: SortableHeader('academic__state__name', True, 'State'),
            4: SortableHeader('academic__academic_code', True, 'Academic Code'),
            5: SortableHeader('academic__institution_name', True, 'Institution'),
            6: SortableHeader('foss__foss', True, 'FOSS'),
            7: SortableHeader('organiser__user__first_name', True, 'Organiser'),
            8: SortableHeader('tdate', True, 'Date'),
            9: SortableHeader('participant_count', True, 'Participants'),
            10: SortableHeader('Action', False)
        }

        raw_get_data = request.GET.get('o', None)
        collection = get_sorted_list(request, collectionSet, header, raw_get_data)
        ordering = get_field_index(raw_get_data)

        collection = TrainingFilter(request.GET, user = user, queryset=collection)
        context['form'] = collection.form

        page = request.GET.get('page')
        collection = get_page(collection.qs, page)

        context['collection'] = collection
        context['header'] = header
        context['ordering'] = ordering
        context['status'] = status
        context['status_code'] = status_dict[status]
        context['role'] = role
        context.update(csrf(request))
        return render(request, 'events/templates/training/index.html', context)
    else:
        raise PermissionDenied()

@login_required
@csrf_exempt
def training_approvel(request, role, rid):
    """ Resource person: confirm or reject training """
    user = request.user
    if not (user.is_authenticated() and (is_resource_person(user) or (is_organiser(user) and request.GET['status'] == 'completed'))):
        raise PermissionDenied()
    try:
        w = Training.objects.get(pk=rid)
        if request.GET['status'] == 'accept':
            w.status = 2
            w.appoved_by_id = user.id
        if request.GET['status'] == 'reject':
            w.status = 5
            w.appoved_by_id = user.id
        if request.GET['status'] == 'completed':
            if w.tdate <= datetime.date.today():
                update_participants_count(w)
                w.status = 4
            else:
                raise PermissionDenied()
    except Exception as e:
        print(e)
        raise PermissionDenied()
    #todo: add training code
    if w.status == 2:
        w.training_code = "WC-"+str(w.id)
        send_email('Instructions to be followed before conducting the training', [w.organiser.user.email], w)
    w.save()
    #send email
    if w.status == 4:
        status = 'Future activities after conducting the Training'
        to = [w.organiser.user.email]
        send_email(status, to, w)
        message = w.academic.institution_name +" has completed "+w.foss.foss+" training dated "+w.tdate.strftime("%Y-%m-%d")
    if request.GET['status'] == 'accept':
        #delete admin notification
        try:
            EventsNotification.objects.get(academic_id = w.academic_id, categoryid = w.id, status = 0).delete()
        except Exception as e:
            print(e)
        message = "Training Manager has approved your "+w.foss.foss+" training request dated "+w.tdate.strftime("%Y-%m-%d")
    if request.GET['status'] == 'reject':
        message = "Training Manager has rejected your "+w.foss.foss+" training request dated "+w.tdate.strftime("%Y-%m-%d")
    #update logs
    update_events_log(user_id = user.id, role = 2, category = 0, category_id = w.id, academic = w.academic_id, status = w.status)
    update_events_notification(user_id = user.id, role = 2, category = 0, category_id = w.id, academic = w.academic_id, status = w.status, message = message)
    if w.status == 4:
        messages.success(request, "Training has been completed. For downloading the learner's certificate click on View Participants ")
        return HttpResponseRedirect('/software-training/training/'+role+'/completed/')
    elif w.status == 5:
        messages.success(request, "Training has been rejected ")
        return HttpResponseRedirect('/software-training/training/'+role+'/rejected/')
    elif w.status == 2:
        messages.success(request, "Training has been approved ")
        return HttpResponseRedirect('/software-training/training/'+role+'/approved/')
    return HttpResponseRedirect('/software-training/training/'+role+'/approved/')

@login_required
def training_permission(request):
    user = request.user
    if not (user.is_authenticated() and (is_resource_person(user) or is_event_manager(user))):
        raise PermissionDenied()

    permissions = Permission.objects.select_related().all()
    form = TrainingPermissionForm()
    if request.method == 'POST':
        form = TrainingPermissionForm(request.POST)
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
            return HttpResponseRedirect("/software-training/training/permission/")

    context = {}
    context.update(csrf(request))
    context['form'] = form
    context['collection'] = permissions
    return render(request, 'events/templates/accessrole/workshop_permission.html', context)

@login_required
def training_completion(request, rid):
    user = request.user
    if not (user.is_authenticated() and is_organiser(user)):
        raise PermissionDenied()

    context = {}
    form = TrainingCompletionForm(user = user)
    if request.method == 'POST':
        form = TrainingCompletionForm(request.POST, user = user)
        if form.is_valid():
            t = Training.objects.get(pk = rid)
            t.extra_fields.approximate_hour = form.cleaned_data['approximate_hour']
            t.extra_fields.online_test = form.cleaned_data['online_test']
            t.extra_fields.is_tutorial_useful = int(form.cleaned_data['is_tutorial_useful'])
            t.extra_fields.future_training = int(form.cleaned_data['future_training'])
            t.extra_fields.recommend_to_others = int(form.cleaned_data['recommend_to_others'])
            t.extra_fields.save()

            t.participant_count = t.trainingattendance_set.filter(status__gte = 1).count()
            t.status = 4
            t.save()
            messages.success(request, "Training has been completed. Close the window and download the learner's certificate.")
            form = None
    context['form'] = form
    context.update(csrf(request))
    return render(request, 'events/templates/training/training_approvel_form.html', context)

@login_required
def view_training_completion(request, rid):
    user = request.user
    context = {}
    if not (user.is_authenticated() and is_resource_person(user)):
        raise PermissionDenied()
    try:
        context['training'] = Training.objects.get(pk = rid)
    except Exception as e:
        raise PermissionDenied()
    return render(request, 'events/templates/training/view_training_completion.html', context)

@login_required
def accessrole(request):
    user = request.user
    state =  list(AcademicCenter.objects.filter(state__in = Permission.objects.filter(user=user, permissiontype_id=1).values_list('state_id')).values_list('id'))
    district = list(AcademicCenter.objects.filter(district__in = Permission.objects.filter(user=user, permissiontype_id=2, district_id__gt=0).values_list('district_id')).values_list('id'))
    university = list(AcademicCenter.objects.filter(university__in = Permission.objects.filter(user=user, permissiontype_id=3, university_id__gt=0).values_list('university_id')).values_list('id'))
    institution_type = list(AcademicCenter.objects.filter(institution_type__in = Permission.objects.filter(user=user, permissiontype_id=4, institute_type_id__gt=0).values_list('institute_type_id')). values_list('id'))
    institute = list(AcademicCenter.objects.filter(id__in = Permission.objects.filter(user=user, permissiontype_id=5, institute_id__gt=0).values_list('institute_id')).values_list('id'))
    all_academic_ids = list(set(state) | set(district) | set(university) | set(institution_type) | set(institute))
    workshops = Training.objects.filter(academic__in = all_academic_ids)
    context = {'collection':workshops}
    return render(request, 'events/templates/accessrole/workshop_accessrole.html', context)

@login_required
def training_attendance(request, wid):
    user = request.user
    onlinetest_user = ''
    psform = ParticipantSearchForm()
    sform = TrainingScanCopyForm()
    if not (user.is_authenticated() and (is_organiser(user))):
        raise PermissionDenied()
    try:
        training = Training.objects.get(pk = wid)
        if training.status == 4:
            return HttpResponseRedirect("/software-training/training/" + str(training.id) + "/participant/")
    except Exception as e:
        print(e)
        raise PermissionDenied()
    #todo check request user and training organiser same or not
    show_success_message = False
    if request.method == 'POST':
        if 'submit-mark-attendance' in request.POST:
            users = request.POST
            if users:
                #set all record to 0 if status = 1
                _mark_all_training_participants_to_zero(training)
                training.status = 3
                training.save()
                for u in users:
                    if not (u =='submit-mark-attendance' or u == 'csrfmiddlewaretoken'):
                        _mark_training_attendance(training, users[u])
                #update participant
                #update_participants_count(training)

                message = training.academic.institution_name+" has submited training attendance"
                update_events_log(user_id = user.id, role = 2, category = 0, category_id = training.id, academic = training.academic_id,  status = 6)
                update_events_notification(user_id = user.id, role = 2, category = 0, category_id = training.id, academic = training.academic_id, status = 6, message = message)

                messages.success(request, """
                <ul>
                    <li>Thank you for uploading the Attendance. Now make sure that you cross check and verify the details before submiting.</li>
                </ul>
                    """
                )
                show_success_message = True
        if 'search-participant' in request.POST:
            psform = ParticipantSearchForm(request.POST)
            onlinetest_user = search_participant(psform)

        if 'add-participant' in request.POST:
            add_participant(request, wid, 'Training')

        if 'submit-attendance' in request.POST:
            training.status = 1
            training.save()

        if 'submit-scaned-copy' in request.POST:
                form = TrainingScanCopyForm(request.POST, request.FILES)
                file_type = ['application/pdf']
                if 'scan_copy' in request.FILES:
                    if request.FILES['scan_copy'].content_type in file_type:
                        file_path = settings.MEDIA_ROOT + 'training/'
                        try:
                            os.mkdir(file_path)
                        except Exception as e:
                            print(e)
                        file_path = settings.MEDIA_ROOT + 'training/'+wid+'/'
                        try:
                            os.mkdir(file_path)
                        except Exception as e:
                            print(e)
                        full_path = file_path + wid +".pdf"
                        fout = open(full_path, 'wb+')
                        f = request.FILES['scan_copy']
                        # Iterate through the chunks.
                        for chunk in f.chunks():
                            fout.write(chunk)
                        fout.close()
                        messages.success(request, "Waiting for Training Manager approval.")
                    else:
                        messages.success(request, "Choose a PDF File")
                else:
                    messages.success(request, "Choose a PDF File.")

    wp = _get_training_participant(training)

    if not show_success_message:
        messages.success(request, """
            <ul>
                <li>
                    Before the Training/Workshop date upload the Participants name
                    list. It is necessary for approving your Training/Workshop request.
                </li>
                <li>
                    Please click on <b>Upload Participant Data</b> and upload the <b>
                    CSV </b>(.csv) file which you have generated (using LibreOffice
                    Calc / MS Excel) and click <b>Submit</b>.
                </li>
                <li>
                    For more details on how to create the .csv file.
                    Please <a href="http://process.spoken-tutorial.org/images/9/96/Upload_Attendance.pdf" target="_blank">Click here</a>
                </li>
            </ul>
        """)

    context = {}
    context['psform'] = psform
    context['sform'] = sform
    context['collection'] = wp
    context['onlinetest_user'] = onlinetest_user
    context['training'] = training
    context['file_path'] = '/media/training/'+wid+'/'+wid+'.pdf'
    context['clone'] = request.GET.get('clone', None)
    context.update(csrf(request))
    return render(request, 'events/templates/training/attendance.html', context)


def training_participant(request, wid=None):
    user = request.user
    training = None
    if user.is_authenticated():
        if not ((is_resource_person(user) or is_event_manager(user) or is_organiser(user))):
            raise PermissionDenied()
    can_download_certificate = 0
    if wid:
        try:
            training = Training.objects.get(id=wid)
        except:
            raise PermissionDenied()
        wp = _get_training_participant(training)
        if (is_resource_person(user) or is_event_manager(user) or user == training.organiser.user) and training.status == 4:
            can_download_certificate = 1
        context = {
            'collection' : wp,
            'wc' : training,
            'can_download_certificate':can_download_certificate,
            'file_path' : '/media/training/'+wid+'/'+wid+'.pdf',
        }
        return render(request, 'events/templates/training/participant.html', context)


def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


def training_participant_ceritificate(request, wid, participant_id):
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
            w = Training.objects.get(id = wid)
            # check if user can get certificate
            wa = TrainingAttendance.objects.get(training_id = w.id, id = participant_id)
            #if wa.status < 1:
            #    raise PermissionDenied()
            if wa.password:
                certificate_pass = wa.password
                wa.count += 1
                wa.status = 3
                wa.save()
            else:
                certificate_pass = str(wa.id)+id_generator(10-len(str(wa.id)))
                wa.password = certificate_pass
                wa.status = 3
                wa.count += 1
                wa.save()
        except Exception as e:
            print(e)
            raise PermissionDenied()

    response = HttpResponse(content_type='application/pdf')
    filename = (wa.firstname+'-'+w.foss.foss+"-Participant-Certificate").replace(" ", "-");

    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'
    imgTemp = BytesIO()
    imgDoc = canvas.Canvas(imgTemp)

    # Title
    imgDoc.setFont('Helvetica', 40, leading=None)
    imgDoc.drawCentredString(415, 480, "Certificate of Appreciation")

    #date
    imgDoc.setFont('Helvetica', 18, leading=None)
    imgDoc.drawCentredString(211, 115, "29 August 2015")

    #password
    imgDoc.setFillColorRGB(211, 211, 211)
    imgDoc.setFont('Helvetica', 10, leading=None)
    imgDoc.drawString(10, 6, certificate_pass)
    #imgDoc.drawString(100, 100, 'transparent')


    # Draw image on Canvas and save PDF in buffer
    imgPath = settings.MEDIA_ROOT +"sign.jpg"
    imgDoc.drawImage(imgPath, 600, 100, 150, 76)    ## at (399,760) with size 160x160

    #paragraphe
    text = "This is to certify that <b>"+wa.firstname +" "+wa.lastname+"</b> participated in the <b>"+w.foss.foss+"</b> workshop organized at <b>"+w.academic.institution_name+"</b> by  <b>Spoken Tutorial Project</b> on <b> 29 August 2015</b><br /><br />A comprehensive set of topics pertaining to <b>"+w.foss.foss+"</b> were covered in the workshop. <br />The Spoken Tutorial Project, IIT Bombay, funded by National Mission on Education <br />through ICT, MHRD, Govt. of India."

    centered = ParagraphStyle(name = 'centered',
        fontSize = 16,
        leading = 30,
        alignment = 0,
        spaceAfter = 20)

    p = Paragraph(text, centered)
    p.wrap(650, 200)
    p.drawOn(imgDoc, 4.2 * cm, 7 * cm)

    imgDoc.save()

    # Use PyPDF to merge the image-PDF into the template
    page = PdfFileReader(file(settings.MEDIA_ROOT +"Blank-Certificate.pdf","rb")).getPage(0)
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

@login_required
def test_request(request, role, rid = None):
    ''' Test request by organiser '''
    user = request.user
    if not (user.is_authenticated() and ( is_organiser(user) or is_resource_person(user) or is_event_manager(user))):
        raise PermissionDenied()
    context = {}
    form = TestForm(user = user)
    if rid:
        t = Test.objects.get(pk = rid)
        user = t.organiser.user
        form = TestForm(user = user, instance = t)
        context['instance'] = t
    if request.method == 'POST':
        form = TestForm(request.POST, user = user)
        if form.is_valid():
            dateTime = request.POST['tdate'].split(' ')
            t = Test()
            if rid:
                t = Test.objects.get(pk = rid)
            else:
                print("New Test.............")
                t.organiser_id = user.organiser.id
                t.academic = user.organiser.academic
            t.test_category_id = request.POST['test_category']

            """if int(request.POST['test_category']) == 1:
                t.training_id = request.POST['workshop']"""
            if int(request.POST['test_category']) == 2:
                t.training_id = request.POST['training']
            if int(request.POST['test_category']) == 3:
                t.training_id = None
            test_trainings = request.POST['training']
            test_training_dept = t.training.department_id
            if request.POST['id_foss']:
                test_foss = request.POST['id_foss']
            else:
                test_foss = t.training.course.foss_id

            t.invigilator_id = request.POST['invigilator']
            t.foss_id = test_foss
            t.tdate = dateTime[0]
            t.ttime = dateTime[1]
            error = 0
            errmsg = ""
            try:
                t.save()
            except IntegrityError:
                error = 1
                errmsg = "Test already created"
                prev_test = Test.objects.filter(organiser = t.organiser_id, academic = t.academic, foss = t.foss_id, tdate = t.tdate, ttime = t.ttime)
                if prev_test:
                    messages.error(request, "You have already scheduled <b>"+ t.foss.foss + "</b> Test on <b>"+t.tdate + " "+ t.ttime + "</b>. Please select some other time.")
                
            if t and t.training_id:
                tras = TrainingAttend.objects.filter(training=t.training)
                fossmdlcourse = FossMdlCourses.objects.get(foss_id = t.foss_id)
                for tra in tras:
                    user = tra.student.user
                    mdluser = get_moodle_user(tra.training.training_planner.academic_id, user.first_name, user.last_name, tra.student.gender, tra.student.user.email)# if it create user rest password for django user too
                    
                    if mdluser:
                        print("mdluser present", mdluser.id)                       
                        try:
                            instance = TestAttendance.objects.get(test_id=t.id, mdluser_id=mdluser.id)
                        except Exception as e:
                            print(e)
                            instance = TestAttendance()
                        instance.student_id = tra.student.id
                        instance.test_id = t.id
                        instance.mdluser_id = mdluser.id
                        instance.mdlcourse_id = fossmdlcourse.mdlcourse_id
                        instance.mdlquiz_id = fossmdlcourse.mdlquiz_id
                        instance.mdlattempt_id = 0
                        instance.status = 0
                        instance.save()

                        print("test_attendance created for ",tra.student.id)
                    else:
                        print("mdluser not found for", user.email)
                        error = 1
            if not error:
                t.department.clear()
                t.department.add(test_training_dept)
                #update logs
                message = t.academic.institution_name+" has made a test request for "+t.foss.foss+" on "+t.tdate
                if rid:
                    message = t.academic.institution_name+" has updated test for "+t.foss.foss+" on  dated "+t.tdate
                update_events_log(user_id = user.id, role = 0, category = 1, category_id = t.id, academic = t.academic_id, status = 0)
                update_events_notification(user_id = user.id, role = 0, category = 1, category_id = t.id, academic = t.academic_id, status = 0, message = message)

                return HttpResponseRedirect("/software-training/test/"+role+"/pending/")
        messages.info(request, """
            <ul>
                <li>Please make sure that before making the test request a faculty/trainer should have registered as invigilator.</li>
                <li>Same person cannot be an organiser and the invigilator for the same test.</li>
                <li>Please confirm the Invigilator's availability and acceptance to invigilate before selecting his name in this form.</li>
                <li>Upgrade the browser with version of Mozilla Firefox 30 or higher on all the systems before the test.</li>
            </ul>
        """)
    context['role'] = role
    context['status'] = 'request'
    context.update(csrf(request))
    context['form'] = form
    return render(request, 'events/templates/test/form.html', context)

@login_required
def test_list(request, role, status):
    """ Organiser test index page """
    user = request.user
    if not (user.is_authenticated() and ( is_organiser(user) or is_invigilator(user) or is_resource_person(user) or is_event_manager(user))):
        raise PermissionDenied()

    status_dict = {'pending': 0, 'waitingforinvigilator': 1, 'approved' : 2, 'ongoing': 3, 'completed' : 4, 'rejected' : 5, 'reschedule' : 2, 'predated' : ''}
    if status in status_dict:
        context = {}
        collectionSet = None
        todaytest = None
        if is_event_manager(user) and role == 'em':
            if status == 'ongoing':
                collectionSet = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), status = status_dict[status], tdate = datetime.datetime.now().strftime("%Y-%m-%d")).order_by('-tdate')
            else:
                collectionSet = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), status = status_dict[status]).order_by('-tdate')
        elif is_resource_person(user) and role == 'rp':
            if status == 'ongoing':
                collectionSet = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), status = status_dict[status], tdate = datetime.datetime.now().strftime("%Y-%m-%d")).order_by('-tdate')
            elif status == 'predated':
                collectionSet = Test.objects.filter((Q(status = 0) | Q(status = 1) | Q(status = 2) | Q(status = 3)), academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), tdate__lt=datetime.date.today()).order_by('-tdate')
            else:
                collectionSet = Test.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), status = status_dict[status]).order_by('-tdate')
        elif is_organiser(user) and role == 'organiser':
            if status == 'ongoing':
                collectionSet = Test.objects.filter((Q(status = 2) | Q(status = 3)), organiser__user = user ,  tdate__lte = datetime.date.today().strftime("%Y-%m-%d")).order_by('-tdate')
            elif status == 'predated':
                collectionSet = Test.objects.filter((Q(status = 0) | Q(status = 1) | Q(status = 2) | Q(status = 3)), organiser__user = user, tdate__lt=datetime.date.today()).order_by('-tdate')
            elif status == 'approved':
                collectionSet = Test.objects.filter(organiser__user = user, status = status_dict[status], tdate__gt=datetime.date.today()).order_by('-tdate')
            else:
                collectionSet = Test.objects.filter(organiser__user = user, status = status_dict[status]).order_by('-tdate')
        elif is_invigilator(user) and role == 'invigilator':
            if status == 'ongoing':
                collectionSet = Test.objects.filter((Q(status = 2) | Q(status = 3)),  tdate__lte = datetime.date.today(), invigilator_id = user.invigilator.id).order_by('-tdate')
                messages.info(request, "Click on the Attendance link below to see the participant list.")
            elif status == 'predated':
                collectionSet = Test.objects.none()
            elif status == 'approved':
                collectionSet = Test.objects.filter(invigilator_id=user.invigilator.id, status = status_dict[status], tdate__gt=datetime.date.today()).order_by('-tdate')
            else:
                todaytest = datetime.datetime.now().strftime("%Y-%m-%d")
                collectionSet = Test.objects.filter(invigilator_id=user.invigilator.id, status = status_dict[status]).order_by('-tdate')

        if collectionSet == None:
            raise PermissionDenied()

        header = {
            1: SortableHeader('#', False),
            2: SortableHeader('academic__state', True, 'State'),
            3: SortableHeader('academic__academic_code', True, 'Academic Code'),
            4: SortableHeader('academic', True, 'Institution'),
            5: SortableHeader('organiser', True, 'Organiser'),
            6: SortableHeader('foss', True, 'FOSS'),
            7: SortableHeader('tdate', True, 'Date'),
            8: SortableHeader('Participants', False),
            9: SortableHeader('', False)
        }
        raw_get_data = request.GET.get('o', None)
        collection = get_sorted_list(request, collectionSet, header, raw_get_data)
        ordering = get_field_index(raw_get_data)

        collection = TestFilter(request.GET, user = user, queryset=collection)
        context['form'] = collection.form

        page = request.GET.get('page')
        collection = get_page(collection.qs, page)

        context['collection'] = collection
        context['header'] = header
        context['ordering'] = ordering

        context['status'] = status
        context['role'] = role
        context['todaytest'] = todaytest
        context['can_manage'] = user.groups.filter(Q(name="Event Manager") |  Q(name="Resource Person"))
        context.update(csrf(request))
        return render(request, 'events/templates/test/index.html', context)
    else:
        raise PermissionDenied()

@login_required
@csrf_exempt
def test_approvel(request, role, rid):
    """ Resource person: confirm or reject training """
    user = request.user
    status = 0
    message = None
    alert = None
    logrole = 0
    try:
        t = Test.objects.get(pk=rid)
        if request.GET['status'] == 'accept':
            print("!!!!!!!!")
            status = 1
            t.test_code = "TC-" + str(t.id)
            message = "The Training Manager has approved "+t.foss.foss+" test dated "+t.tdate.strftime("%Y-%m-%d")
            alert = "Test has been approved"
            #send email
            send_email('Instructions to be followed before conducting the test-organiser', [t.organiser.user.email], t)
            send_email('Instructions to be followed before conducting the test-invigilator', [t.invigilator.user.email], t)
            logrole = 2
        if request.GET['status'] == 'invigilatoraccept':
            message = "The Invigilator "+t.organiser.user.first_name +" "+t.organiser.user.last_name+" has approved "+t.foss.foss+" test dated "+t.tdate.strftime("%Y-%m-%d")
            status = 2
            logrole = 1
            alert = "Test has been approved"
        if request.GET['status'] == 'ongoing':
            status = 3
        if request.GET['status'] == 'completed':
            status = 4
            logrole = 1
            alert = "Test has been Completed"
            message = t.academic.institution_name +" has completed "+t.foss.foss+" test dated "+t.tdate.strftime("%Y-%m-%d")
        if request.GET['status'] == 'reject':
            message = "The Training Manager has rejected "+t.foss.foss+" test dated "+t.tdate.strftime("%Y-%m-%d")
            status = 5
            logrole = 2
            alert = "Test has been rejected"
        if request.GET['status'] == 'invigilatorreject':
            message = "The Invigilator "+t.organiser.user.first_name +" "+t.organiser.user.last_name+" has rejected "+t.foss.foss+" test dated "+t.tdate.strftime("%Y-%m-%d")
            status = 6
            logrole = 1
            alert = "Test has been rejected"
    except Exception as e:
        print(e)
        raise PermissionDenied()

    #if status = 2:
    #    if not (user.is_authenticated() and w.academic.state in State.objects.filter(resourceperson__user_id=user, resourceperson__status=1) and ( is_event_manager(user) or is_resource_person(user))):
    #        raise PermissionDenied('You are not allowed to view this page')
    if status == 1:
        t.appoved_by_id = user.id
        t.workshop_code = "TC-"+str(t.id)
    if status == 4:
        TestAttendance.objects.filter(test_id=t.id, status = 2).update(status = 3)
        testatten = TestAttendance.objects.filter(test_id=t.id, status__gt=2)
        if  not testatten:
            messages.error(request, "Students are processing the test. Check the status for each students!")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        t.participant_count = TestAttendance.objects.filter(test_id=t.id, status__gte=2).count()

    t.status = status
    t.save()

    #events log
    #message = user.first_name+" "+user.last_name+" has accepted your "+t.foss.foss+" Test"
    update_events_log(user_id = user.id, role = logrole, category = 1, category_id = t.id, academic = t.academic_id, status = status)
    update_events_notification(user_id = user.id, role = logrole, category = 1, category_id = t.id, academic = t.academic_id, status = status, message = message)
    messages.success(request, alert)
    if request.GET['status'] == 'completed':
        return HttpResponseRedirect('/software-training/test/'+role+'/completed/')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def test_attendance(request, tid):
    user = request.user
    test = None
    onlinetest_user = ''
    form = ParticipantSearchForm()
    try:
        test = Test.objects.get(pk=tid)
        if test.status == 4 or test.status == 1:
            return HttpResponseRedirect('/software-training/test/' + str(test.id) + '/participant/')

        test.status = 3
        test.save()
    except:
        raise PermissionDenied()
    print((test.foss_id))
    if request.method == 'POST':
        users = request.POST
        if users:
            #set all record to 0 if status = 1
            if 'submit-attendance' in users:
                TestAttendance.objects.filter(test_id = tid, status = 1).update(status = 0)
                for u in users:
                    if not (u == 'csrfmiddlewaretoken' or u == 'submit-attendance'):
                        try:
                            ta = TestAttendance.objects.get(mdluser_id = users[u], test_id = tid)
                            if ta.status > 1:
                                continue
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
                        if ta:
                            #todo: if the status = 2 check in moodle if he completed the test set status = 3 (completed)
                            t = TestAttendance.objects.get(mdluser_id = ta.mdluser_id, test_id = tid)
                            fossmdlcourse = FossMdlCourses.objects.get(foss_id = test.foss_id)
                            t.mdlcourse_id = fossmdlcourse.mdlcourse_id
                            t.mdlquiz_id = fossmdlcourse.mdlquiz_id
                            t.status = 1
                            t.save()
                            #enroll to the course
                            #get the course enrole id
                            #todo: If mark absent delete enrolement
                            mdlenrol = None
                            try:
                                mdlenrol = MdlEnrol.objects.get(enrol='self', courseid = fossmdlcourse.mdlcourse_id )
                                print("Role Exits")
                            except Exception as e:
                                print(("MdlEnrol => ", e))
                                print("No self enrolement for this course")

                            #if mdlenrol:
                            #    try:
                            #        MdlUserEnrolments.objects.get(enrolid = mdlenrol.id, userid = ta.mdluser_id)
                            #        print "MdlUserEnrolments Exits"
                            #        #update dateTime
                            #    except Exception as e:
                            #        print "MdlUserEnrolments => ", e
                            #        MdlRoleAssignments.objects.create(roleid = 5, contextid = 16, userid = ta.mdluser_id, timemodified = datetime.datetime.now().strftime("%s"), modifierid = ta.mdluser_id, itemid = 0, sortorder = 0)
                            #        MdlUserEnrolments.objects.create(enrolid = mdlenrol.id, userid = ta.mdluser_id, status = 0, timestart = datetime.datetime.now().strftime("%s"), timeend = 0, modifierid = ta.mdluser_id, timecreated = datetime.datetime.now().strftime("%s"), timemodified = datetime.datetime.now().strftime("%s"))

            if 'search-participant' in request.POST:
                form = ParticipantSearchForm(request.POST)
                onlinetest_user = search_participant(form)

            if 'add-participant' in request.POST:
                add_participant(request, tid, 'Test')

            message = test.academic.institution_name+" has submited Test attendance dated "+test.tdate.strftime("%Y-%m-%d")
            update_events_log(user_id = user.id, role = 1, category = 1, category_id = test.id, academic = test.academic_id, status = 8)
            update_events_notification(user_id = user.id, role = 1, category = 1, category_id = test.id, academic = test.academic_id, status = 8, message = message)
            messages.success(request, """
                <ul>
                    <li>Thank you for uploading the Attendance. Now make sure that you cross check and verify the details before submiting.</li>
                    <li>If you want to add more participants please upload a new CSV file containing the missing participants details.</li>
                    <li>Once you confirm the list of participants please click on <b>'Mark as Complete'</b></li>
                </ul>
            """)
    mdlids = []
    participant_ids = []
    online_participant_ids = list(TestAttendance.objects.filter(test_id = test.id).values_list('mdluser_id'))
    for k in online_participant_ids:
        mdlids.append(k[0])

    if test.test_category_id == 1:
        participant_ids = list(TrainingAttendance.objects.filter(training_id = test.training_id).values_list('mdluser_id'))
    elif test.test_category_id == 2:
        participant_ids = list(TrainingAttendance.objects.filter(training_id = test.training_id).values_list('mdluser_id'))
    else:
        participant_ids = list(TestAttendance.objects.filter(test_id = test.id).values_list('mdluser_id'))

    wp = None
    for k in participant_ids:
        mdlids.append(k[0])
    if mdlids:
        wp = MdlUser.objects.filter(id__in = mdlids)
    #check can close the test
    testatten = TestAttendance.objects.filter(test_id=test.id, status__gte=2)
    enable_close_test = None
    if testatten:
        enable_close_test = True
    context = {}
    context['collection'] = wp
    context['test'] = test
    context['form'] = form
    context['onlinetest_user'] = onlinetest_user
    context['enable_close_test'] = enable_close_test
    context.update(csrf(request))
    messages.info(request, "Instruct the students to Register and Login on the Online Test link of Spoken Tutorial. Click on the checkbox so that usernames of all the students who are present for the test are marked, then click the submit button. Students can now proceed for the Test.")
    return render(request, 'events/templates/test/attendance.html', context)

@login_required
def test_participant(request, tid=None):
    user = request.user
    can_download_certificate = 0
    if tid:
        try:
            t = Test.objects.get(id=tid)
        except:
            raise PermissionDenied()

        if t.status == 4:
            test_mdlusers = TestAttendance.objects.filter(test_id=tid, status__gte=2)
        else:
            test_mdlusers = TestAttendance.objects.filter(test_id=tid)
        #ids = []
        #print test_mdlusers
        #for tp in test_mdlusers:
        #    ids.append(tp[0])
        #print ids, 'ssssssssssss', tid
        #tp = MdlUser.objects.using('moodle').filter(id__in=ids)
        #if t.status == 4 and (user == t.organiser or user == t.invigilator):
        #    can_download_certificate = 1
        context = {'collection' : test_mdlusers, 'test' : t, 'can_download_certificate':can_download_certificate}
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
            if ta.status < 1 or round(mdlgrade.grade, 1) < 40 or not w.invigilator:
                raise PermissionDenied()

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
        except Exception as e:
            print(e)
            raise PermissionDenied()
    response = HttpResponse(content_type='application/pdf')
    filename = (ta.mdluser_firstname+'-'+ta.mdluser_lastname+"-Participant-Certificate").replace(" ", "-");

    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'
    imgTemp = BytesIO()
    imgDoc = canvas.Canvas(imgTemp)

    # Title
    #imgDoc.setFont('Helvetica', 40, leading=None)
    #imgDoc.drawCentredString(415, 480, "Certificate for Completion of c ")

    imgDoc.setFont('Helvetica', 18, leading=None)
    imgDoc.drawCentredString(211, 115, custom_strftime('%B {S} %Y', w.tdate))

    #password
    imgDoc.setFillColorRGB(211, 211, 211)
    imgDoc.setFont('Helvetica', 10, leading=None)
    imgDoc.drawString(10, 6, certificate_pass)
    #imgDoc.drawString(100, 100, 'transparent')


    # Draw image on Canvas and save PDF in buffer
    imgPath = settings.MEDIA_ROOT +"sign.jpg"
    imgDoc.drawImage(imgPath, 600, 80, 150, 76)    ## at (399,760) with size 160x160

    #paragraphe
    text = "This is to certify that <b>"+ta.mdluser_firstname +" "+ta.mdluser_lastname+"</b> has successfully completed <b>"+w.foss.foss+"</b> test organized at <b>"+w.academic.institution_name+"</b> by <b>"+w.organiser.user.first_name + " " + w.organiser.user.last_name+"</b>  with course material provided by the Spoken Tutorial Project, IIT Bombay.  <br /><br /><p>Passing an online exam, conducted remotely from IIT Bombay, is a pre-requisite for completing this training. <b>"+w.invigilator.user.first_name + " "+w.invigilator.user.last_name+"</b> at <b>"+w.academic.institution_name+"</b> invigilated this examination. This training is offered by the <b>Spoken Tutorial Project, IIT Bombay, funded by National Mission on Education through ICT, MHRD, Govt., of India.</b></p>"

    centered = ParagraphStyle(name = 'centered',
        fontSize = 16,
        leading = 24,
        alignment = 0,
        spaceAfter = 20)

    p = Paragraph(text, centered)
    p.wrap(700, 200)
    p.drawOn(imgDoc, 4.2 * cm, 6 * cm)

    #paragraphe
    text = "Certificate for Completion of "+w.foss.foss+" Training"

    centered = ParagraphStyle(name = 'centered',
        fontSize = 30,
        leading = 50,
        alignment = 1,
        spaceAfter = 15)

    p = Paragraph(text, centered)
    p.wrap(500,50)
    p.drawOn(imgDoc, 6.2 * cm, 16 * cm)


    imgDoc.save()

    # Use PyPDF to merge the image-PDF into the template
    page = PdfFileReader(open(settings.MEDIA_ROOT +"Blank-Certificate.pdf","rb")).getPage(0)
    overlay = PdfFileReader(BytesIO(imgTemp.getvalue())).getPage(0)
    page.mergePage(overlay)

    #Save the result
    output = PdfFileWriter()
    output.addPage(page)

    #stream to browser
    outputStream = response
    output.write(response)
    outputStream.close()

    return response


def test_participant_ceritificate_all(request, testid):
    certificate_pass = ''
    w = Test.objects.get(id = testid)
    if not w.organiser.user == request.user:
        raise PermissionDenied()
    testattendances = TestAttendance.objects.filter(test_id = testid)

    response = HttpResponse(content_type='application/pdf')
    filename = (w.foss.foss+"-Participant-Certificate").replace(" ", "-");

    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'

    output = PdfFileWriter()

    for ta in testattendances: 
        try:
            mdlgrade = MdlQuizGrades.objects.get(quiz = ta.mdlquiz_id, userid = ta.mdluser_id)
        except:
            continue
        if ta.status < 1 or round(mdlgrade.grade, 1) < 40:
            continue

        if ta.password:
            certificate_pass = ta.password
            ta.count += 1
            ta.status = 4
            ta.save()
        else:
            certificate_pass = str(ta.mdluser_id)+id_generator(10-len(str(ta.mdluser_id)))
            ta.password = certificate_pass
            ta.status = 4
            ta.count += 1
            ta.save()        
        imgTemp = BytesIO()
        imgDoc = canvas.Canvas(imgTemp)

        imgDoc.setFont('Helvetica', 18, leading=None)
        imgDoc.drawCentredString(211, 115, custom_strftime('%B {S} %Y', w.tdate))

        #password
        imgDoc.setFillColorRGB(211, 211, 211)
        imgDoc.setFont('Helvetica', 10, leading=None)
        imgDoc.drawString(10, 6, certificate_pass)
        #imgDoc.drawString(100, 100, 'transparent')


        # Draw image on Canvas and save PDF in buffer
        imgPath = settings.MEDIA_ROOT +"sign.jpg"
        imgDoc.drawImage(imgPath, 600, 80, 150, 76)    ## at (399,760) with size 160x160

        #paragraphe
        text = "This is to certify that <b>"+ta.mdluser_firstname +" "+ta.mdluser_lastname+"</b> has successfully completed <b>"+w.foss.foss+"</b> test organized at <b>"+w.academic.institution_name+"</b> by <b>"+w.organiser.user.first_name + " " + w.organiser.user.last_name+"</b>  with course material provided by the Spoken Tutorial Project, IIT Bombay.  <br /><br /><p>Passing an online exam, conducted remotely from IIT Bombay, is a pre-requisite for completing this training. <b>"+w.invigilator.user.first_name + " "+w.invigilator.user.last_name+"</b> at <b>"+w.academic.institution_name+"</b> invigilated this examination. This training is offered by the <b>Spoken Tutorial Project, IIT Bombay, funded by National Mission on Education through ICT, MHRD, Govt., of India.</b></p>"

        centered = ParagraphStyle(name = 'centered',
            fontSize = 16,
            leading = 24,
            alignment = 0,
            spaceAfter = 20)

        p = Paragraph(text, centered)
        p.wrap(700, 200)
        p.drawOn(imgDoc, 4.2 * cm, 6 * cm)

        #paragraphe
        text = "Certificate for Completion of "+w.foss.foss+" Training"

        centered = ParagraphStyle(name = 'centered',
            fontSize = 30,
            leading = 50,
            alignment = 1,
            spaceAfter = 15)

        p = Paragraph(text, centered)
        p.wrap(500,50)
        p.drawOn(imgDoc, 6.2 * cm, 16 * cm)


        imgDoc.save()

        # Use PyPDF to merge the image-PDF into the template
        page = PdfFileReader(open(settings.MEDIA_ROOT +"Blank-Certificate.pdf","rb")).getPage(0)
        overlay = PdfFileReader(BytesIO(imgTemp.getvalue())).getPage(0)
        page.mergePage(overlay)

        #Save the result
        output.addPage(page)

    #stream to browser
    outputStream = response
    output.write(response)
    outputStream.close()

    return response


@csrf_exempt
def training_subscribe(request, events, eventid = None, mdluser_id = None):
    try:
        mdluser = MdlUser.objects.get(id = mdluser_id)
        if events == 'test':
            try:
                TestAttendance.objects.create(test_id=eventid, mdluser_id = mdluser_id, mdluser_firstname = mdluser.firstname, mdluser_lastname = mdluser.lastname)
            except Exception as e:
                print(e)
                pass
            messages.success(request, "You have sucessfully subscribe to the "+events+"")
            return HttpResponseRedirect('/participant/index/#Upcoming-Test')
        elif events == 'training':
            try:
                TrainingAttendance.objects.create(training_id=eventid, mdluser_id = mdluser_id)
            except Exception as e:
                print(e)
                pass
            messages.success(request, "You have sucessfully subscribe to the "+events+"")
            return HttpResponseRedirect('/participant/index/#Upcoming-Training')
        else:
            raise PermissionDenied()
    except:
        raise PermissionDenied()

    return HttpResponseRedirect('/participant/index/')

@login_required
def organiser_invigilator_index(request, role, status):
    """ Resource person: List all inactive organiser under resource person states """
    #todo: filter to diaplay block and active user
    active = status
    user = request.user
    context = {}
    if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
        raise PermissionDenied()
    if status == 'active':
        status = 1
    elif status == 'inactive':
        status = 0
    elif status == 'blocked':
        status = 2
    elif status == 'deactivated':
        status = 3
    else:
        raise PermissionDenied()

    user = User.objects.get(pk=user.id)

    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('academic__state', True, 'State'),
        3: SortableHeader('academic__academic_code', True, 'Academic Code'),
        4: SortableHeader('academic__institution_name', True, 'Institution'),
        5: SortableHeader('user__first_name', True, 'Name'),
        6: SortableHeader('Email', False),
        7: SortableHeader('Phone', False),
        8: SortableHeader('Action', False)
    }

    if role == 'organiser':
        try:
            #collectionSet = Organiser.objects.select_related().filter(academic__in=AcademicCenter.objects.filter(state__in=State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), status=status)
            states =  user.resource_person.prefetch_related().filter(resourceperson__status = 1,resourceperson__user_id=user)
            academics = AcademicCenter.objects.filter(state__in = states)
            collectionSet = Organiser.objects.filter(academic__in = academics, status = status)
            
            raw_get_data = request.GET.get('o', None)
            collection = get_sorted_list(request, collectionSet, header, raw_get_data)
            ordering = get_field_index(raw_get_data)

            collection = OrganiserFilter(request.GET, user = user, queryset=collection)
            context['form'] = collection.form

            page = request.GET.get('page')
            collection = get_page(collection.qs, page)
        except Exception as e:
            print(e)
            collection = {}
    elif role == 'invigilator':
        try:
            #collectionSet = Invigilator.objects.select_related().filter(academic__in=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), status=status)
            states = user.resource_person.prefetch_related().filter(resourceperson__status=1, resourceperson__user_id=user)
            academics = AcademicCenter.objects.filter(state__in=states)
            collectionSet = Invigilator.objects.filter(academic__in=academics, status=status)

            raw_get_data = request.GET.get('o', None)
            collection = get_sorted_list(request, collectionSet, header, raw_get_data)
            ordering = get_field_index(raw_get_data)

            collection = InvigilatorFilter(request.GET, user = user, queryset=collection)
            context['form'] = collection.form

            page = request.GET.get('page')
            collection = get_page(collection.qs, page)

        except Exception as e:
            print(e)
            collection = {}
    elif role == 'accountexecutive':
        try:
            #collectionSet = Accountexecutive.objects.select_related().filter(academic__in=AcademicCenter.objects.filter(state__in=State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)), status=status)
            states = user.resource_person.prefetch_related().filter(resourceperson__status=1, resourceperson__user_id=user)
            academics = AcademicCenter.objects.filter(state__in=states)
            collectionSet = Accountexecutive.objects.filter(academic__in=academics, status=status)


            raw_get_data = request.GET.get('o', None)
            collection = get_sorted_list(request, collectionSet, header, raw_get_data)
            ordering = get_field_index(raw_get_data)

            collection = AccountexecutiveFilter(request.GET, user = user, queryset=collection)
            context['form'] = collection.form

            page = request.GET.get('page')
            collection = get_page(collection.qs, page)

        except Exception as e:
            print(e)
            collection = {}    
    else:
        raise PermissionDenied()

    for record in collection:
        try:
            record.user.profile_set.get()
        except:
            create_profile(record.user, None)

    context['header'] = header
    context['ordering'] = ordering
    context['collection'] = collection
    context['status'] = active
    context['role'] = role
    context.update(csrf(request))
    return render(request, 'events/templates/organiser_invigilator_index.html', context)


def update_events_log(user_id, role, category, category_id, academic, status):
    if category == 0:
        try:
            TrainingLog.objects.create(user_id = user_id, training_id = category_id, role = role, academic_id = academic, status = status)
        except Exception as e:
            print(("Training Log =>",e))
    elif category == 1:
        try:
            TestLog.objects.create(user_id = user_id, test_id = category_id, role = role, academic_id = academic, status = status)
        except Exception as e:
            print(("Test Log => ",e))
    else:
        print("************ Error in events log ***********")

def update_events_notification(user_id, role, category, category_id, status, academic, message):
    try:
        EventsNotification.objects.create(user_id = user_id, role = role, category = category, categoryid = category_id, academic_id = academic, status = status, message = message)
    except Exception as e:
        print(("Error in Events Notification => ", e))

def training_participant_feedback(request, training_id, participant_id):
    try:
        tf = TrainingFeedback.objects.get(training_id = training_id, mdluser_id = participant_id)
    except:
        messages.success(request, 'Feedback does not exist!')
        return HttpResponseRedirect("/software-training/training/" + str(training_id) + "/participant/")
    context = {
        'feedback' : tf,
    }
    context.update(csrf(request))
    return render(request, 'events/templates/training/view-feedback.html', context)

def training_participant_language_feedback(request, training_id, user_id):
    w = None
    try:
        w = TrainingRequest.objects.get(pk=training_id)
        MdlUser.objects.get(id = user_id)
    except Exception as e:
        raise PermissionDenied()
    form = TrainingLanguageFeedbackForm(training = w)
    if request.method == 'POST':
        form = TrainingLanguageFeedbackForm(request.POST, training = w)
        if form.is_valid():
            try:
                form_data = form.save(commit=False)
                form_data.training_id = w.id
                form_data.mdluser_id = user_id
                form_data.language_id = form.cleaned_data['language_prefered']
                form_data.save()
                messages.success(request, "Thank you for your valuable feedback.")
                return HttpResponseRedirect('/')
            except Exception as e:
                print(e)
                messages.success(request, "Sorry, something went wrong, Please try again!")
                #return HttpResponseRedirect('/')
    context = {
        'form' : form,
        'w' : w
    }


    context = {}
    context['form'] = form
    return render(request, 'events/templates/training/language_feedback.html', context)

def live_training(request, training_id=None):

    context = {}
    if not training_id:
        context['training_list'] = SingleTraining.objects.filter(
          training_type = 2
        )
    else:
        try:
            context['training'] = TrainingLiveFeedback.objects.filter(
              training_id = training_id
            )
        except Exception as e:
            print(e)
            raise PermissionDenied()

    context.update(csrf(request))
    return render(request, 'events/templates/training/live-feedback-list.html', context)

def training_participant_livefeedback(request, training_id):
    form = LiveFeedbackForm()
    w = None
    try:
        w = SingleTraining.objects.get(pk=training_id)
    except Exception as e:
        raise PermissionDenied()
    if request.method == 'POST':
        form = LiveFeedbackForm(request.POST)
        if form.is_valid():
            try:
                form_data = form.save(commit=False)
                form_data.training_id = w.id
                form_data.save()
                messages.success(request, "Thank you for your valuable feedback.")
                return HttpResponseRedirect('/')
            except Exception as e:
                print(e)
                messages.success(request, "Something went wrong, please contact site administrator.")
                return HttpResponseRedirect('/')
    context = {
        'form' : form,
        'w' : w
    }
    return render(request, 'events/templates/training/lfeedback.html', context)

def training_participant_viewlivefeedback(request, training_id, feedback_id):
    tf = None
    try:
        tf = TrainingLiveFeedback.objects.get(training_id = training_id, id = feedback_id)
    except:
        raise PermissionDenied()
    context = {
        'feedback' : tf,
        'live' : True
    }
    context.update(csrf(request))
    return render(request, 'events/templates/training/view-feedback.html', context)

def resource_center(request, slug = None):
    context = {}
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('State', False),
        3: SortableHeader('institution_name', True, 'Institution Name'),
        4: SortableHeader('Address', False),
        5: SortableHeader('Contact Person', False),
        6: SortableHeader('Action', False)
    }

    collection = None
    if slug:
        collection = AcademicCenter.objects.filter(resource_center = 1, state__slug = slug).order_by('state__name', 'institution_name')
    else:
        collection = AcademicCenter.objects.filter(resource_center = 1).order_by('state__name', 'institution_name')

    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collection, header, raw_get_data)
    ordering = get_field_index(raw_get_data)

    collection = AcademicCenterFilter(request.GET, queryset=collection)
    context['form'] = collection.form

    page = request.GET.get('page')
    collection = get_page(collection.qs, page)

    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering
    return render(request, 'events/templates/ac/resource-center.html', context)

def academic_center(request, academic_id = None, slug = None):
    collection = get_object_or_404(AcademicCenter, id=academic_id)
    slug_title =  slugify(collection.institution_name)
    if slug != slug_title:
        return HttpResponseRedirect('/software-training/academic-center/'+ str(collection.id) + '/' + slug_title)
    context = {
        'collection' : collection
    }
    return render(request, 'events/templates/ac/academic-center.html', context)

#Ajax Request and Responces
@csrf_exempt
def ajax_ac_state(request):
    """ Ajax: Get University, District, City based State selected """
    if request.method == 'POST':
        state = request.POST.get('state')
        data = {}
        if request.POST.get('fields[district]'):
            district = District.objects.filter(state=state).order_by('name')
            tmp = ''
            for i in district:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'

            if(tmp):
                data['district'] = '<option value=""> -- None -- </option>'+tmp
            else:
                data['district'] = tmp

        if request.POST.get('fields[city]'):
            city = City.objects.filter(state=state).order_by('name')
            tmp = ''
            for i in city:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'

            if(tmp):
                data['city'] = '<option value=""> -- None -- </option>'+tmp
            else:
                data['city'] = tmp

        if request.POST.get('fields[university]'):
            university = University.objects.filter(state=state).order_by('name')
            tmp = ''
            for i in university:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
            if(tmp):
                data['university'] = '<option value=""> -- None -- </option>'+tmp
            else:
                data['university'] = tmp

        return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def ajax_state_details(request):
    """ Ajax: Get District, City based State selected """
    if request.method == 'POST':
        state = request.POST.get('state')
        data = {}
        if request.POST.get('fields[district]'):
            district = District.objects.filter(state=state).order_by('name')
            tmp = ''
            for i in district:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
            if(tmp):
                data['district'] = '<option value=""> -- None -- </option>'+tmp
            else:
                data['district'] = tmp
        if request.POST.get('fields[city]'):
            city = City.objects.filter(state=state).order_by('name')
            tmp = ''
            for i in city:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
            if(tmp):
                data['city'] = '<option value=""> -- None -- </option>'+tmp
            else:
                data['city'] = tmp
        return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def ajax_ac_location(request):
    """ Ajax: Get the location based on district selected """
    if request.method == 'POST':
        district = request.POST.get('district')
        location = Location.objects.filter(district=district).order_by('name')
        tmp = '<option value = None> -- None -- </option>'
        for i in location:
            tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
        return HttpResponse(json.dumps(tmp), content_type='application/json')

@csrf_exempt
def ajax_district_data(request):
    """ Ajax: Get the location based on district selected """
    data = {}
    if request.method == 'POST':
        tmp = ''
        district = request.POST.get('district')
        if district and district != None:
            if request.POST.get('fields[location]'):
                location = Location.objects.filter(district_id=district).order_by('name')
                tmp = '<option value = None> -- None -- </option>'
                for i in location:
                    tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
                data['location'] = tmp

        if request.POST.get('fields[institute]'):
            collages = AcademicCenter.objects.filter(district=district).order_by('institution_name')
            if collages:
                tmp = '<option value = None> -- None -- </option>'
                for i in collages:
                    tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
                data['institute'] = tmp

    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def ajax_ac_pincode(request):
    """ Ajax: Get the pincode based on location selected """
    if request.method == 'POST':
        location = request.POST.get('location')
        location = Location.objects.get(pk=location)
        return HttpResponse(json.dumps(location.pincode), content_type='application/json')

@csrf_exempt
def ajax_district_collage(request):
    """ Ajax: Get the Colleges (Academic) based on District selected """
    if request.method == 'POST':
        district = request.POST.get('district')
        collages = AcademicCenter.objects.filter(district=district).order_by('institution_name')
        tmp = None
        if collages:
            tmp = '<option value = None> -- None -- </option>'
            for i in collages:
                tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
        return HttpResponse(json.dumps(tmp), content_type='application/json')

@csrf_exempt
def ajax_state_collage(request):
    """ Ajax: Get the Colleges (Academic) based on District selected """
    if request.method == 'POST':
        state = request.POST.get('state')
        collages = AcademicCenter.objects.filter(state=state).order_by('institution_name')
        tmp = '<option value = None> --------- </option>'
        if collages:
            for i in collages:
                tmp +='<option value='+str(i.id)+'>'+i.institution_name+', '+i.academic_code+'</option>'
        return HttpResponse(json.dumps(tmp), content_type='application/json')


@csrf_exempt
def ajax_academic_center(request):
    """Ajax: Get academic centers according to institute type and state"""

    if request.method == 'POST':
        state = request.POST.get('state')
        itype = request.POST.get('itype')
        center = AcademicCenter.objects.filter(state=state,
            institution_type=itype).order_by('institution_name')
        html = '<option value=None> --------- </option>'
        if center:
            for ac in center:
                html += '<option value={0}>{1}</option>'.format(ac.id,
                        ac.institution_name)
    return HttpResponse(json.dumps(html),
                        content_type='application/json')


@csrf_exempt
def ajax_dept_foss(request):
    """ Ajax: Get the dept and foss based on training selected """
    data = {}
    if request.method == 'POST':
        tmp = ''
        category =  int(request.POST.get('fields[type]'))
        print(category)
        print((request.POST))
        if category == 1:
            print((request.POST))
            training = request.POST.get('workshop')
            if request.POST.get('fields[dept]'):
                dept = Department.objects.filter(training__id = training).order_by('name')
                for i in dept:
                    tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
                data['dept'] = tmp

            if request.POST.get('fields[foss]'):
                training = Training.objects.filter(pk=training).order_by('name')
                tmp = '<option value = None> -- None -- </option>'
                if training:
                    tmp +='<option value='+str(training[0].foss.id)+'>'+training[0].foss.foss+'</option>'
                data['foss'] = tmp
        elif category == 0:
            workshop = request.POST.get('workshop')
            if request.POST.get('fields[dept]'):
                dept = Department.objects.filter(training__id = workshop).order_by('name')
                for i in dept:
                    tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
                data['dept'] = tmp

            if request.POST.get('fields[foss]'):
                workshop = Training.objects.filter(pk=workshop)
                tmp = '<option value = None> -- None -- </option>'
                if workshop:
                    tmp +='<option value='+str(workshop[0].foss.id)+'>'+workshop[0].foss.foss+'</option>'
                data['foss'] = tmp
        else:
            dept = Department.objects.all().order_by('name')
            for i in dept:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
            data['dept'] = tmp

            tmp = '<option value = None> -- None -- </option>'
            foss = FossCategory.objects.all(status = 1)
            for i in foss:
                tmp +='<option value='+str(i.id)+'>'+i.foss+'</option>'
            data['foss'] = tmp
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def ajax_language(request):
    """ Ajax: Get the Colleges (Academic) based on District selected """
    if request.method == 'POST':
        foss = request.POST.get('foss')
        tmp = '<option value = None> --------- </option>'
        if foss:
            language = FossAvailableForWorkshop.objects.select_related().filter(foss_id=foss)
            for i in language:
                tmp +='<option value='+str(i.language.id)+'>'+i.language.name+'</option>'
        return HttpResponse(json.dumps(tmp), content_type='application/json')

@csrf_exempt
def test(request):
    academics = AcademicCenter.objects.filter(Q(institution_name__icontains="Engineering")).exclude(Q(institution_type__name="Engineering") | Q(institution_type__name="Polytechnic") | Q(institution_type__name="ITI") | Q(institution_type__name="University"))
    for academic in academics:
        print((academic.institution_name, " => ", academic.institution_type))
        academic.institution_type = InstituteType.objects.get(name='Engineering')
        academic.save()
    return HttpResponsei("Done!")

@csrf_exempt
def ajax_check_foss(request):
    """ Ajax: Get the get the foss name of selected batch """
    training = request.GET.get('training',None)
    trid = TrainingRequest.objects.get(pk=training)
    foss_id = trid.course.foss.id

    # is_c_and_cpp = False

    is_multiquiz_foss = False
    multiquiz_foss = 0

    if foss_id == 43:
        is_multiquiz_foss = True
        multiquiz_foss = 43
    
    if foss_id == 97:
        is_multiquiz_foss = True
        multiquiz_foss = 97
    data = {
    "is_multiquiz_foss": is_multiquiz_foss,
    "multiquiz_foss": multiquiz_foss
    }
    return JsonResponse(data)

@csrf_exempt
def activate_academics(request):
    context = {}
    collection = None
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('State', False),
        3: SortableHeader('institution_name', True, 'Institution Name'),
        4: SortableHeader('academic_code', True, 'Academic Code'),
        5: SortableHeader('Action', False),
        6: SortableHeader('Status', False)
    }
    print(request)
    if request.method == 'POST':
        collegeid = request.POST.get('collegeid')
        action = request.POST.get('action')
        
        if action == 'activate':
            activate_academic_org(collegeid)

        if action == 'deactivate':
            deactivate_academic_org(collegeid)

        return HttpResponseRedirect("/software-training/activate-academics/")
    else:
        status = request.GET.get('status')
        if status:
            collection = AcademicCenter.objects.filter(status=status).order_by('state__name', 'institution_name')
        else:
            collection = AcademicCenter.objects.filter(status=3).order_by('state__name', 'institution_name')
        
        raw_get_data = request.GET.get('o', None)
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)

        collection = ActivateAcademicCenterFilter(request.GET, queryset=collection)

        context['form'] = collection.form
        page = request.GET.get('page')
        collection = get_page(collection.qs, page)
        

    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering



    return render(request, 'activate_academics.html', context)

def activate_academic_org(academic_id):
    ac = AcademicCenter.objects.get(id=academic_id)
    deactivate_status = 3
    if ac:
        #check if college paid the subscription fees
        #activate all organiser fom this college
        organisers_from_academic = Organiser.objects.filter(status=deactivate_status, academic_id=ac.id)
        invigilators_from_academic = Invigilator.objects.filter(status=deactivate_status, academic_id=ac.id)

        for organiser in organisers_from_academic:
            #all the organisers from this academic are activated here.
            organiser.status = 1 
            organiser.save()
        
        for invigilator in invigilators_from_academic:
            #all the organisers from this academic are activated here.
            invigilator.status = 1 
            invigilator.save()

        #Activate that collge
        ac.status = 1
        ac.save()


def deactivate_academic_org(academic_id):
    ac = AcademicCenter.objects.get(id=academic_id)
    activate_status = 1
    if ac:
        #check if college paid the subscription fees
        #activate all organiser fom this college
        organisers_from_academic = Organiser.objects.filter(status=activate_status, academic_id=ac.id)
        invigilators_from_academic = Invigilator.objects.filter(status=activate_status, academic_id=ac.id)
        for organiser in organisers_from_academic:
            #all the organisers from this academic are activated here.
            organiser.status = 3 
            organiser.save()

        for invigilator in invigilators_from_academic:
            #all the organisers from this academic are activated here.
            invigilator.status = 3
            invigilator.save()

        #Activate that collge
        ac.status = 3
        ac.save()

def key_verification(serial):
    context = {}
    try:
        certificate = TestAttendance.objects.get(password=serial)
        if not certificate.student:
            name = certificate.mdluser_firstname+" "+certificate.mdluser_lastname
        else:    
            name = certificate.student.user.first_name+ " "+certificate.student.user.last_name
        foss = certificate.test.foss.foss
        tdate = certificate.test.tdate
        detail = {}
        detail['Participant_Name'] = name
        detail['Foss'] = foss
        detail['Test_Date'] = tdate

        context['certificate'] = certificate
        context['detail'] = detail
        context['serial_no'] = True
    except TestAttendance.DoesNotExist:
        context["invalidserial"] = 1
    return context

@csrf_exempt
def verify_test_certificate(request):
    context = {}
    ci = RequestContext(request)
    if request.method == 'POST':
        serial_no = request.POST.get('serial_no').strip()
        context = key_verification(serial_no)
        return render(request, 'verify_test_certificate.html', context)
    return render(request, 'verify_test_certificate.html', {})

def check_user_email_exist(email):
    users = User.objects.filter(email=email)
    if users.exists():
        user = users.first()
        return user
    return None

def check_email_already_organiser(userid):
    org = Organiser.objects.filter(user_id=userid)
    if org.exists():
        return org
    return None

@login_required
def handover(request):
    user = request.user
    context = {}
    if not (user.is_authenticated() and (is_event_manager(user))):
        raise PermissionDenied()
    # ci = RequestContext(request)
    if request.method == 'POST':
        old_email = request.POST.get('old_email').strip()
        new_email = request.POST.get('new_email').strip()

        #check if old email id registerd or not
        old_user = check_user_email_exist(old_email)
        if old_user:
            #check if old email id organiser or not
            old_org = check_email_already_organiser(old_user.id)
            if not old_org:
                context['msg'] = 'Old organiser entry not found.'
                context['error_status'] = 'True'
                return render(request, 'handover.html', context)
        else:
            context['msg'] = 'Old organiser entry not found. Not a registered user.'
            context['error_status'] = 'True'
            return render(request, 'handover.html', context)


        #check if new email id registerd or not
        new_user = check_user_email_exist(new_email)    
        if new_user:           
            new_org = check_email_already_organiser(new_user.id)
            if new_org:
                context['msg'] = 'New user is already an organiser. Can not continue work handover.'
                context['error_status'] = 'True'
                return render(request, 'handover.html', context)
            else:
                organiser = Organiser.objects.filter(user_id=old_user.id).update(user_id=new_user.id)
                
                old_user.groups.remove(Group.objects.get(name='Organiser'))
                new_user.groups.add(Group.objects.get(name='Organiser'))

                context['msg'] = 'Organiser work handover completed successfully.'
                context['error_status'] = 'False'

        else:
            context['msg'] = 'New user is not registerd with spoken-tutorial'
            context['error_status'] = 'True'
            return render(request, 'handover.html', context)

    return render(request, 'handover.html', context)








