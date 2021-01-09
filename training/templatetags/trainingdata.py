from events.models import AcademicKey
from training.models import *
from cms.models import Profile
from django import template
from datetime import datetime,date
register = template.Library()

today = date.today()

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

    if date.today() <= reg_end_date:
        return True
    return False

def is_user_registered(eventid, userid):
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
    return fdate

def is_event_closed(eventid):
    event = TrainingEvents.objects.get(id=eventid)
    if event.training_status == 2:
        return True
    return False

@register.filter
def is_tr_completed(eventid):
    event = TrainingEvents.objects.get(id=eventid)
    if event.training_status == 1 and event.event_end_date < today:
        return True
    return False

@register.filter
def is_reg_approved_ongoing(eventid):
    event = TrainingEvents.objects.get(id=eventid)
    if event.training_status == 1 and event.event_end_date >= today:
        return True
    return False

@register.filter
def is_tr_ongoing(eventid):
    event = TrainingEvents.objects.get(id=eventid)
    if event.training_status == 0:
        return True
    return False

@register.filter
def is_tr_expired(eventid):
    event = TrainingEvents.objects.get(id=eventid)
    if event.training_status == 0 and event.event_end_date < today:
        return True
    return False

@register.filter
def event_has_attendance(eventid):
  if EventAttendance.objects.filter(event_id=eventid).exists():
    return True
  return False


@register.filter
def is_attendance_marked(eventid, participantid):
  if EventAttendance.objects.filter(event_id=eventid, participant_id=participantid).exists():
    return True
  return False


@register.filter
def is_reg_confirmed(eventid, participantid):
  if Participant.objects.filter(id=participantid, event_id=eventid, reg_approval_status=1).exists():
    return True
  return False

@register.filter
def event_has_registration(eventid):
  if Participant.objects.filter(event_id=eventid, reg_approval_status=1).exists():
    return True
  return False


@register.filter
def registartion_successful(user, event):
  # Payee status 1 - complete , 2 - Failed
  # Registration Type 1 - Subcribed clg, 2 -Unsubscribed clg, 3 - Unsubscribed colg added via csv(DB Payment checks not possible)
  participant = Participant.objects.filter(user = user, event = event)
  if participant.filter(payment_status__status=1).exists():
    return True
  if participant.filter(registartion_type__in=(1,3)).exists():
    return True
  return False 

@register.filter
def get_user_detail(user):
  try:
    profile = Profile.objects.get(user=user)
  except Profile.DoesNotExist:
    return None

  return profile.phone

@register.filter
def get_participant_count(eventid):
  try:
    event = TrainingEvents.objects.get(id=eventid)
    print()
    if event.training_status <= 1 :
      #completed state
      pcount = Participant.objects.filter(event_id=eventid, reg_approval_status=1).count()
    elif event.training_status == 2:
      #closed
      pcount = EventAttendance.objects.filter(event_id=eventid).count()
  except TrainingEvents.DoesNotExist:
    return pcount

  return pcount

@register.filter
def get_event_details(eventid):
  try:
    event = TrainingEvents.objects.get(id=eventid)
  except TrainingEvents.DoesNotExist:
    return None

  return event

register.filter('is_user_paid', is_user_paid)
register.filter('is_reg_valid', is_reg_valid)
register.filter('is_user_registered', is_user_registered)
register.filter('format_date', format_date)
register.filter('is_event_closed', is_event_closed)
