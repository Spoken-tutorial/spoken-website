from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Count, Sum, Min
from django.db.models import Q
from events.models import *
from cms.sortable import *
from events.filters import TrainingFilter
from events.views import get_page
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
        workshop_details = Training.objects.filter(Q(status = 4) | (Q(training_type = 0) & Q(status__gt = 1) & Q(trdate__lte = datetime.date.today())), academic__state_id = state.id).aggregate(Sum('participant_counts'), Count('id'), Min('trdate'))
        context = {
            'state': state,
            'workshops': workshop_details['id__count'],
            'participants': workshop_details['participant_counts__sum'],
            'resource_centers': resource_centers,
            'from_date': workshop_details['trdate__min']
        }
        return render(request, 'statistics/templates/get_state_info.html', context)
    except Exception, e:
        print e
        return HttpResponse('<h4 style="margin: 30px;">Permission Denied!</h4>')

def training(request, slug = None):
    """ Organiser index page """
    user = request.user
    collectionSet = None
    if slug:
        collectionSet = Training.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(slug=slug)), status = 4, participant_counts__gt=0).order_by('-trdate')
    else:
        collectionSet = Training.objects.filter(status = 4, participant_counts__gt=0).order_by('-trdate')
        
    if not collectionSet:
        raise Http404('You are not allowed to view this page')

    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('training_type', True, 'Training Type'),
        3: SortableHeader('academic__state', True, 'State'),
        4: SortableHeader('academic__academic_code', True, 'Academic Code'),
        5: SortableHeader('academic', True, 'Institution'),
        6: SortableHeader('foss', True, 'FOSS'),
        7: SortableHeader('organiser__user', True, 'Organiser'),
        8: SortableHeader('trdate', True, 'Date'),
        9: SortableHeader('Participants', False),
        10: SortableHeader('Action', False)
    }
    
    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collectionSet, header, raw_get_data)
    ordering = get_field_index(raw_get_data)
    
    collection = TrainingFilter(request.GET, queryset=collection)
    context = {}
    context['form'] = collection.form
    
    page = request.GET.get('page')
    collection = get_page(collection, page)
    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering
    context['state'] = slug
    return render(request, 'statistics/templates/training.html', context)
    
def training_participant(request, wid=None):
    user = request.user
    if wid:
        try:
            wc = Training.objects.get(id=wid)
        except:
            raise Http404('Page not found')
        if wc.status == 4:
            workshop_mdlusers = TrainingAttendance.objects.using('default').filter(training_id = wid, status__gt = 0).values_list('mdluser_id')
        else:
            workshop_mdlusers = TrainingAttendance.objects.using('default').filter(training_id = wid).values_list('mdluser_id')
        ids = []
        for wp in workshop_mdlusers:
            ids.append(wp[0])
            
        wp = MdlUser.objects.using('moodle').filter(id__in=ids)
        context = {
            'collection' : wp,
            'wc' : wc,
        }
        return render(request, 'statistics/templates/participant.html', context)
