from django.db.models import Q
from events.models import AcademicKey
from training.models import *
from cms.models import Profile
from django import template
from datetime import datetime,date
from health_app.models import HNLanguage, Category
from spoken.config import HN_URL, HN_API
from collections import defaultdict

register = template.Library()

def is_user_paid(user_obj):
    if not user_obj.is_authenticated():
      return False
    academic_id = None
    organiser = Organiser.objects.filter(user=user_obj).first()
    if organiser:
      academic_id = user_obj.organiser.academic_id
    else:
      invigilator = Invigilator.objects.filter(user=user_obj).first()
      if invigilator:
        academic_id = user_obj.invigilator.academic_id
      else:
        student = Student.objects.filter(user=user_obj)
        if student.exists():
          student = student.first()
          try:
            academic_id = StudentMaster.objects.get(student=student).batch.academic.id
          except StudentMaster.DoesNotExist:
            return False
    if academic_id:
      return AcademicKey.objects.filter(Q(academic_id=academic_id) & Q(expiry_date__gte=date.today())).exists()
    return False

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
    if event.training_status == 1 and event.event_end_date < date.today():
        return True
    return False

@register.filter
def is_reg_approved_ongoing(eventid):
    event = TrainingEvents.objects.get(id=eventid)
    if event.training_status == 1 and event.event_end_date >= date.today():
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
    if event.training_status == 0 and event.event_end_date < date.today():
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

@register.filter
def get_ilw_mdlcourseid(eventfossid):
  try:
    ilwcourse = ILWFossMdlCourses.objects.filter(foss=eventfossid)
  except ILWFossMdlCourses.DoesNotExist:
    return None

  return ilwcourse

@register.filter
def check_passgrade_exists(event,testfossid):

  # arg_list = [arg.strip() for arg in args.split(',')]
  # email= arg_list[0]
  # testfossid = arg_list[1]
  # print("@@@@@@@@@@@@@@@",email, arg_list)

  ilwmdlgradeentry = EventTestStatus.objects.filter(event=event.event, fossid=testfossid, mdlemail=event.email, part_status__gte=2, mdlgrade__gte=40.00)
  if ilwmdlgradeentry:
    return True
  else:
    return False

@register.filter
def check_hn_passgrade_exists(participant):
   ilwmdlgradeentry = EventTestStatus.objects.filter(participant=participant, event=participant.event, mdlemail=participant.email, part_status__gte=2, mdlgrade__gte=40.00).exists()
   return ilwmdlgradeentry


@register.filter
def get_grade(event, testfossid):
  # fossid = event.foss_id
  # email,event, testfossid
  # arg_list = [arg.strip() for arg in args.split(',')]

  # email= arg_list[0]
  # testfossid = arg_list[1]
  ilwmdlgradeentry = EventTestStatus.objects.filter(event=event.event, fossid=testfossid, mdlemail=event.email, part_status__gte=2, mdlgrade__gte=40.00).order_by('-mdlgrade').first()

  return ilwmdlgradeentry.mdlgrade

@register.filter
def get_hn_grade(participant):
  ilwmdlgradeentry = EventTestStatus.objects.filter(participant=participant, event=participant.event, mdlemail=participant.email, part_status__gte=2, mdlgrade__gte=40.00).order_by('-mdlgrade').first()

  return ilwmdlgradeentry.mdlgrade

@register.filter
def get_item(dictionary, key):
   """
    retrieve a value from a dictionary using either the key or its string representation (handles int/str mismatches).
    """
   if key in dictionary:
      return dictionary[key]
   elif str(key) in dictionary:
      return dictionary[str(key)]
   return None


@register.filter
def get_hn_categories(event):
  foss_ids = [x.id for x in event.course.foss.all()]
  categories = [str(x.external_course) for x in ExternalCourseMap.objects.filter(foss_id__in=foss_ids)]
  return ','.join(categories)

@register.filter
def get_hn_tutorial_links(participant):
   event = participant.event
   foss_ids = [x.id for x in event.course.foss.all()]
   categories = [str(x.external_course) for x in ExternalCourseMap.objects.filter(foss_id__in=foss_ids)]
   data = []
   categories = Category.objects.filter(category_id__in=categories)
   for item in categories:
      url = f"{HN_URL}?categoryName={item.category_id}&lan=22"
      data.append((item.category_name, url))
   return data


@register.filter
def get_hn_course_id(participant):
   event = participant.event
   try:
    hn_course_id = ExternalEventCourse.objects.filter(event=event).first().external_course
    return hn_course_id
   except :
      return 1

@register.filter
def get_hn_part_lang(participant):
   lang_id = participant.language_hn
   if lang_id is not None and lang_id != 22:
    lang = HNLanguage.objects.get(lan_id=lang_id)
    return [(lang.lang_name, lang.lan_id), ("English", 22)] #Default English
   return [("English", 22)] #English only


@register.filter
def get_hn_test(event):
   try:
    obj = ExternalEventCourse.objects.filter(event=event).first()
    return obj.mdl_quiz, obj.mdl_course, 1
   except Exception as e:
    return None


register.filter('is_user_paid', is_user_paid)
register.filter('is_reg_valid', is_reg_valid)
register.filter('is_user_registered', is_user_registered)
register.filter('format_date', format_date)
register.filter('is_event_closed', is_event_closed)

