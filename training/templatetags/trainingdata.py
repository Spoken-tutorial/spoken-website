from events.models import AcademicKey
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

register.filter('is_user_paid', is_user_paid)
