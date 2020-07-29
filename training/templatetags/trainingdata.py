from events.models import AcademicKey
from training.models import *
from django import template
from datetime import datetime,date
register = template.Library()


def is_user_paid(user_obj):
    try:
        idcase = AcademicKey.objects.get(academic_id=user_obj.organiser.academic_id)
        user_paid = True if (idcase.expiry_date >= date.today()) else False
        return user_paid
    except:
        user_paid = False
    try:
        idcase = AcademicKey.objects.get(academic_id=user_obj.invigilator.academic_id)
        user_paid = True if (idcase.expiry_date >= date.today()) else False
        return user_paid
    except:
        user_paid = False
    return user_paid


def is_reg_valid(reg_end_date):
    print(reg_end_date, date.today())

    if date.today() <= reg_end_date:
        return True
    return False

def is_user_registered(eventid, userid):
    print(userid)
    if Participant.objects.filter(user_id=userid, event_id=eventid):
        return True
    return False

def format_date(start_date, end_date):
    start = start_date.strftime("%d,%b,%Y").split(',')
    end = end_date.strftime("%d,%b,%Y").split(',')
    fdate = ''
    if start==end:
        fdate = start[0]+' '+start[1]+' , '+start[2]
    else:
        if start[2]==end[2]: #check year
            if start[1]==end[1]: #check month
                fdate = start[0] + ' - ' + end[0] + ' ' + start[1] + ' , ' + start[2]
            else: 
                fdate = start[0] + ' ' + start[1] + ' - ' + end[0] + ' ' + end[1] + ' , ' + start[2]
        else: 
            fdate = start[0] + ' ' + start[1] + ' , ' + start[2]+ ' - ' + end[0] + ' ' + end[1] + ' , ' + end[2]
    print(fdate)
    return fdate

def is_event_closed(eventid):
    event = TrainingEvents.objects.get(id=eventid)
    if event.training_status == 1:
        return True
    return False


register.filter('is_user_paid', is_user_paid)
register.filter('is_reg_valid', is_reg_valid)
register.filter('is_user_registered', is_user_registered)
register.filter('format_date', format_date)
register.filter('is_event_closed', is_event_closed)