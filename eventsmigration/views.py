from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db import connection
from django.conf import settings
from shutil import copyfile
from django.db.models import Sum
from django.db.models import Q
from django.db.models import Count, Sum, Min
import random, string
import datetime
#from datetime import date, datetime, time, timedelta
import os, sys
from django.core.validators import validate_email
from events.models import *
from events2.models import *

def participants(request):
    emails = TrainingAttendance.objects.all().values('email').distinct()
    student = Group.objects.get(name = 'Student')
    error_log_file_head = open('error-log.txt',"w")
    for email in emails:
        if email['email'] == None or (not email['email'].strip()):
            continue
        mail = email['email'].lower()
        try:
            validate_email(mail)
        except:
            print "Invalide => ", mail
            continue
        print mail
        user = None
        try:
            user = User.objects.get(email = mail)
            try:
                Student.objects.get(user = user)
                continue
            except:
                pass
        except:
            pass
        row = TrainingAttendance.objects.filter(email = mail).order_by('-password', '-firstname', '-lastname', '-updated').first()
        if row:
            if (row.firstname == None or row.firstname.strip() == '') and (row.lastname != None or row.lastname.strip() != ''):
                firstname = row.lastname
                lastname = None
            elif ((row.firstname == None or row.firstname.strip() == '') and (row.lastname == None or row.lastname.strip() == '')):
                continue
            else:
                firstname = row.firstname
                lastname = row.lastname
            if row.gender == 'Male' or row.gender == 'M':
                gender = 'Male'
            else:
                gender = 'Female'
            password = row.password
            if not user:
                try:
                    user = User.objects.create_user(mail, mail, firstname)
                except Exception, e:
                    error_log_file_head.write(mail+','+mail+','+firstname)
                    continue
            user.is_active = False
            user.first_name = firstname.upper()
            if lastname:
                user.last_name = lastname.upper()
            user.save()
            try:
                user.groups.add(student)
            except:
                pass
            Student.objects.create(user = user, gender = gender)

    return HttpResponse('Success')


def course_map(request):
    foss = Training.objects.all().values_list('foss_id').distinct()
    for f in foss:
        cm = CourseMap()
        cm.name = None
        cm.foss_id = f[0]
        cm.save()
    return HttpResponse('Success')

def _create_training_planner(year, academic_id, organiser_id, created, even=False):
    try:
        tp = TrainingPlanner()
        tp.semester_id = 2
        tp.year = year
        if even:
            tp.year = int(year) -1
            tp.semester_id = 1
        tp.academic_id = academic_id
        tp.organiser_id = organiser_id
        tp.created = created
        tp.updated = created
        tp.save()
        
        # Get old training request
        trainings = None
        if even:
            trainings = Training.objects.filter((Q(tdate__gte = year + '-01-01') & Q(tdate__lte = year + '-06-30')), organiser_id = organiser_id, academic_id = academic_id, status=4)
        else:
            trainings = Training.objects.filter((Q(tdate__gte = year + '-07-01') & Q(tdate__lte = year + '-12-31')), organiser_id = organiser_id, academic_id = academic_id, status=4)
        # create new training request
        for training in trainings:
            tr = TrainingRequest()
            tr.id = training.id
            tr.sem_start_date = created
            tr.participants = training.participant_count
            tr.created = training.created
            tr.updated = training.updated
            tr.batch_id = None
            tr.course = _find_course(training.foss, 0)
            tr.department = training.department.first() # what to do if multiple dept
            tr.language = training.language
            tr.training_planner = tp
            tr.status = 1
            tr.save()
    except Exception, e:
        print e,  "************************************************"

def _find_course(foss, category):
    return CourseMap.objects.get(foss= foss, category = category)

def training_planner(request):
    #organisers = Training.objects.filter().values('organiser').distinct()[:100]
    organisers = Training.objects.filter(organiser_id=44).values('organiser').distinct()[:10]
    for organiser in organisers:
        # organiser training per year
        organiser_id = int(organiser['organiser'])
        organiser_training_by_year = Training.objects.filter(organiser_id = organiser_id).exclude(academic__institution_type__name='School').extra(select={'year': "EXTRACT(year FROM tdate)"}).values('year', 'academic').distinct().order_by('academic', 'year')
        for record in organiser_training_by_year:
            year = str(record['year'])
            academic_id = record['academic']
            evensem = Training.objects.exclude(academic__institution_type__name='School').filter((Q(tdate__gte = year + '-01-01') & Q(tdate__lte = year +'-06-30')), organiser_id = organiser_id, academic_id = academic_id, status=4).aggregate(Min('tdate')) # 2010 - 2011
            oddsem = Training.objects.exclude(academic__institution_type__name='School').filter((Q(tdate__gte = year + '-07-01') & Q(tdate__lte = year + '-12-31')), organiser_id = organiser_id, academic_id = academic_id, status=4).aggregate(Min('tdate')) # 2011 - 2012
            tp = None
            odd_date = oddsem['tdate__min']
            even_date = evensem['tdate__min']
            if odd_date:
                tp = _create_training_planner(year, academic_id, organiser_id, odd_date)
            if even_date:
                tp = _create_training_planner(year, academic_id, organiser_id, even_date, even=True)
    return HttpResponse('Success')

def attendance(request):
    training_requests = TrainingRequest.objects.all()
    for tr in training_requests:
        attendance = TrainingAttendance.objects.filter(training_id = tr.id)
        for record in attendance:
            record.email = record.email.lower()
            record.firstname = record.firstname.upper()
            record.lastname = record.lastname.upper()
            if User.objects.filter(email = record.email).exists():
                try:
                    user = User.objects.get(email = record.email, first_name = record.firstname, last_name = record.lastname)
                    if Student.objects.filter(user = user).exists():
                        student = Student.objects.get(user = user)
                        # Create Attendance
                        ta = TrainingAttend()
                        ta.training = tr
                        ta.student = student
                        ta.created = record.created
                        ta.updated = record.updated
                        ta.save()

                        # Create Certificate
                        tc = TrainingCertificate()
                        tc.student = student
                        tc.training = tr
                        tc.password = record.password
                        tc.updated = record.updated
                        tc.save()
                    else:
                        print "No student => ", record.id, ", ", record.training_id,", ", record.email
                except Exception, e:
                    print e, "name mismatch => ", record.id, ", ", record.training_id,", ", record.email
            else:
                print "No user => ", record.id, ", ", record.training_id,", ", record.email
            print "************************************************"
    return HttpResponse('Success')

def _get_training_type(training):
    if training.training_type == 0:
        return 0
    return training.training_type - 1

# School, Live Workshop, Pilot Workshop
def school_training(request):
    trainings = Training.objects.filter(Q(training_type=2) | Q(training_type=3) | Q(academic__institution_type__name='School'), status=4)
    for tr in trainings:
        try:
            SingleTraining.objects.get(pk=tr.id)
            print tr.id, "Exist"
            continue
        except Exception, e:
            print tr.id, "Creating.."
            t = SingleTraining()
            t.id = tr.id
            t.organiser = tr.organiser
            t.academic = tr.academic
            t.course = _find_course(tr.foss, 0)
            t.training_type = _get_training_type(tr)
            t.language = tr.language
            t.tdate = tr.tdate
            t.ttime = tr.ttime
            t.status = 2
            t.participant_count = tr.participant_count
            t.created = tr.created
            t.updated = tr.updated
            t.save()

            # Attendance
            tas = TrainingAttendance.objects.filter(training_id = t.id, status__gt=0)
            for ta in tas:
                sta = SingleTrainingAttendance()
                sta.training = t
                sta.firstname = ta.firstname
                sta.lastname = ta.lastname
                sta.gender = ta.gender
                sta.password = ta.password
                sta.count = ta.count
                sta.status = 2
                sta.created = ta.created
                sta.updated = ta.updated
                sta.save()

    return HttpResponse('Success')
