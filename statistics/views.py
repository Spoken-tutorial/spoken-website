from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum, Min
from django.db.models import Q
from events.models import *
from cms.sortable import *
from events.filters import TrainingFilter, TestFilter, AcademicCenterFilter
from events.views import get_page
import datetime
from django.http import Http404, HttpResponseRedirect
from django.template.defaultfilters import slugify

# Create your views here.
def maphome(request):
    states = State.objects.all().exclude(name = 'Uncategorized')
    counts = Training.objects.filter(status = 4, participant_count__gt=0).aggregate(Count('id'), Sum('participant_count'))
    institution_count = AcademicCenter.objects.filter(id__in=Training.objects.filter(status = 4, participant_count__gt=0).values_list('academic_id').distinct()).aggregate(Count('id'))
    print institution_count
    context = {
        'states': states,
        'participant_count': counts['participant_count__sum'],
        'training_count': counts['id__count'],
        'institution_count': institution_count['id__count'],
    }
    return render(request, 'statistics/templates/maphome.html', context)

def get_state_info(request, code):
    state = None
    try:
        state = State.objects.get(code = code)
        #academic_list = AcademicCenter.objects.filter(state = state).values_list('id')
        academic_centers = AcademicCenter.objects.filter(state = state, id__in=Training.objects.filter(status = 4, participant_count__gt=0).values_list('academic_id').distinct()).count()
        #workshop_details = Training.objects.filter(academic_id__in = academic_list, status = 4).aggregate(Sum('participant_count'), Count('id'), Min('tdate'))
        workshop_details = Training.objects.filter(Q(status = 4) | (Q(training_type = 0) & Q(status__gt = 1) & Q(tdate__lte = datetime.date.today())), participant_count__gt=0, academic__state_id = state.id).aggregate(Sum('participant_count'), Count('id'), Min('tdate'))
        context = {
            'state': state,
            'workshops': workshop_details['id__count'],
            'participants': workshop_details['participant_count__sum'],
            'academic_centers': academic_centers,
            'from_date': workshop_details['tdate__min']
        }
        return render(request, 'statistics/templates/get_state_info.html', context)
    except Exception, e:
        print e
        return HttpResponse('<h4 style="margin: 30px;">Permission Denied!</h4>')

def training(request, slug = 'training'):
    """ Organiser index page """
    user = request.user
    collectionSet = None
    state = None
    participant_count = 0
    event_type = ['Training', 'Test']
    model_type = {
        'training' : 0,
        'onlinetest' : 1
    }
    if  not (slug in model_type.keys()):
        return HttpResponseRedirect('/statistics/training/')
    model_index = int(request.GET.get('event_type', model_type[slug]))
    model_filter = eval(event_type[model_index] + 'Filter')
    model = eval(event_type[model_index])
    collectionSet = model.objects.filter(status = 4, participant_count__gt=0).order_by('-tdate')
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('academic__state', True, 'State'),
        3: SortableHeader('academic__city', True, 'City'),
        4: SortableHeader('academic', True, 'Institution'),
        5: SortableHeader('foss', True, 'FOSS'),
        6: SortableHeader('organiser__user', True, 'Organiser'),
        7: SortableHeader('tdate', True, 'Date'),
        8: SortableHeader('participant_count', 'True', 'Participants'),
        9: SortableHeader('Action', False)
    }
    
    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collectionSet, header, raw_get_data)
    ordering = get_field_index(raw_get_data)
    
    # find state id
    state_id = None
    if 'academic__state' in request.GET and request.GET['academic__state'] and slug:
        # todo
        pass
    elif 'academic__state' in request.GET and request.GET['academic__state']:
        state = State.objects.get(id=request.GET['academic__state'])
    
    collection = model_filter(request.GET, queryset=collection, state=state)
    # find participants count
    participant_count = collection.qs.aggregate(Sum('participant_count'))
    
    #
    chart_query_set = collection.qs.extra(select={'year': "EXTRACT(year FROM tdate)"}).values('year').annotate(total_training=Count('tdate'), total_participant=Sum('participant_count'))
    chart_data = ''
    for data in chart_query_set:
        chart_data += "['" + str(data['year']) + "', " + str(data['total_participant']) + "],"
    context = {}
    context['form'] = collection.form
    context['chart_data'] = chart_data
    page = request.GET.get('page')
    collection = get_page(collection, page)
    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering
    context['state'] = slug
    context['participant_count'] = participant_count
    context['event_type'] = event_type[model_index].lower
    if model_index:
        context['model'] = 'Online-Test'
    else:
        context['model'] = 'Workshop/Training'
    return render(request, 'statistics/templates/training.html', context)
    
def training_participant(request, model ,rid):
    user = request.user
    event_type = ['Training', 'Test']
    context = {}
    if not model.title() in event_type or not rid:
        raise PermissionDenied()
    try:
        context['model_label'] = model
        context['model'] = eval(model.title()).objects.get(id=rid)
        if model == 'training':
            context['collection'] = TrainingAttendance.objects.filter(training_id = rid, status__gt = 0)
        else:
             
            test_mdlusers = TestAttendance.objects.using('default').filter(test_id=rid).values_list('mdluser_id')
            ids = []
            for wp in test_mdlusers:
                ids.append(wp[0])
            context['collection'] = MdlUser.objects.using('moodle').filter(id__in=ids)
        
    except Exception, e:
        raise PermissionDenied()
    return render(request, 'statistics/templates/participant.html', context)

def academic_center(request, slug = None):
    context = {}
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('State', False),
        3: SortableHeader('institution_name', True, 'Institution Name'),
        4: SortableHeader('num_training', True, 'Training'),
        5: SortableHeader('num_participant', True, 'Participants'),
        6: SortableHeader('Action', False)
    }
    
    collection = None
    training_index = int(request.GET.get('training', 0))
    if slug:
        collection = AcademicCenter.objects.filter(state__slug = slug).order_by('state__name', 'institution_name')
    elif training_index:
        collection = AcademicCenter.objects.filter(training__status=4, training__participant_count__gt=0).annotate(num_training=Count('training'), num_participant=Sum('training__participant_count')).filter(num_training__gte=training_index).order_by('state__name', 'institution_name')
    else:
        collection = AcademicCenter.objects.filter(training__status=4, training__participant_count__gt=0).annotate(num_training=Count('training'), num_participant=Sum('training__participant_count')).order_by('state__name', 'institution_name')
    
    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collection, header, raw_get_data)
    ordering = get_field_index(raw_get_data)
    
    collection = AcademicCenterFilter(request.GET, queryset=collection)
    context['form'] = collection.form
    context['total_training'] = collection.qs.aggregate(Sum('num_training'))
    context['total_participant'] = collection.qs.aggregate(Sum('num_participant'))
    
    page = request.GET.get('page')
    collection = get_page(collection, page)
    options = '<option value="0"> --------- </option><option value="1">at least 1</option>'
    for i in range(5, 105, 5):
        options += '<option value="' + str(i) + '"> at least ' + str(i) + '</option>'
    options += '<option value="101">more than 100</option>'
    options = options.replace('<option value="' + str(training_index) + '">', \
        '<option value="' + str(training_index) + '" selected="selected">')
    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering
    context['options'] = options
    
    return render(request, 'statistics/templates/academic-center.html', context)

def academic_center_view(request, academic_id = None, slug = None):
    collection = get_object_or_404(AcademicCenter, id=academic_id)
    slug_title =  slugify(collection.institution_name)
    if slug != slug_title:
        return HttpResponseRedirect('/statistics/academic-center/'+ str(collection.id) + '/' + slug_title)
    context = {
        'collection' : collection
    }
    return render(request, 'statistics/templates/view-academic-center.html', context)

def motion_chart(request):
    collection = Training.objects.filter(status = 4, participant_count__gt=0).values('academic__state__name', 'tdate').annotate(tcount=Count('tdate'), pcount=Sum('participant_count'))
    interactive_workshop_data = ""
    static_workshop_data = ""
    states = {}
    for row in collection:
        curr_state = str(row['academic__state__name'])
        if curr_state in states:
            states[curr_state]['tcount'] += int(row['tcount'])
            states[curr_state]['pcount'] += int(row['pcount'])
        else:
            states[curr_state] = {}
            states[curr_state]['tcount'] = int(row['tcount'])
            states[curr_state]['pcount'] = int(row['pcount'])
        js_date = 'new Date(' + str(row['tdate'].year) + ', ' + str(int(row['tdate'].month) - 1) + ', ' + str(row['tdate'].day) + ')'
        interactive_workshop_data += "['" + curr_state + "', " + js_date + ", " + str(row['tcount']) + ", " + str(row['pcount']) + "],"
    
    for key, value in states.iteritems():
        curr_year = str(datetime.datetime.now().year)
        static_workshop_data += "['" + key + "', " + curr_year + ", " + str(value['tcount']) + ", " + str(value['pcount']) + "],"
    
    context = {
        'interactive_workshop_data': interactive_workshop_data,
        'static_workshop_data': static_workshop_data,
    }
    
    return render(request, 'statistics/templates/motion_charts.html', context)
