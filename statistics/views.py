from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Count, Sum, Min
from django.db.models import Q
from events.models import *
import datetime

# Create your views here.
def maphome(request):
    states = State.objects.all().exclude(name = 'Uncategorized')
    context = {
        'states': states
    }
    return render(request, 'statistics/templates/maphome.html', context)

def get_state_info(request, code):
    state = None
    try:
        state = State.objects.get(code = code)
        #academic_list = AcademicCenter.objects.filter(state = state).values_list('id')
        resource_centers = AcademicCenter.objects.filter(state = state, resource_center = 1).count()
        #workshop_details = Training.objects.filter(academic_id__in = academic_list, status = 4).aggregate(Sum('participant_counts'), Count('id'), Min('trdate'))
        workshop_details = Training.objects.filter(Q(status = 4) | (Q(training_type = 0) & Q(status__gt = 0) & Q(trdate__lte = datetime.date.today())), academic__state_id = state.id).aggregate(Sum('participant_counts'), Count('id'), Min('trdate'))
        context = {
            'state_name': state.name,
            'workshops': workshop_details['id__count'],
            'participants': workshop_details['participant_counts__sum'],
            'resource_centers': resource_centers,
            'from_date': workshop_details['trdate__min']
        }
        return render(request, 'statistics/templates/get_state_info.html', context)
    except Exception, e:
        print e
        return HttpResponse('<h4 style="margin: 30px;">Permission Denied!</h4>')
