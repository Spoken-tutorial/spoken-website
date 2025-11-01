import os
import datetime as dt
# Third Party Stuff
from django import template
from django.db.models import Q
# Spoken Tutorial Stuff
from cms.models import Notification

register = template.Library()

@register.assignment_tag
def get_notifications():
    return Notification.objects.filter(Q(start_date__lte=dt.datetime.today()) & Q(
        expiry_date__gte=dt.datetime.today())).order_by('expiry_date')



