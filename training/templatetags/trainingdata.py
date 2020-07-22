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


register.filter('is_user_paid', is_user_paid)
register.filter('is_reg_valid', is_reg_valid)
register.filter('is_user_registered', is_user_registered)