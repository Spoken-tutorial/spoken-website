# Standard Library
from builtins import str
from datetime import datetime
import collections
from hashlib import md5
from time import sleep

# Third Party Stuff
from django.core.exceptions import PermissionDenied,ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Min, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import slugify
from django.utils.timezone import now

# Spoken Tutorial Stuff
from cms.sortable import *
from events.filters import AcademicCenterFilter, TestFilter, TrainingRequestFilter, EventStatsFilter
from events.models import *
from training.models import *
from creation.models import TutorialResource
from creation.filters import CreationStatisticsFilter
from events.views import get_page
from .forms import LearnerForm
from django.core.cache import cache
from spoken.decorators import rate_limited_view

# Create your views here.
@rate_limited_view
def maphome(request):
    states = State.objects.filter(has_map=1)

    counts = TrainingRequest.objects.filter(
        participants__gt=0,
        sem_start_date__lte=datetime.now()
    ).aggregate(Count('id'), Sum('participants'))

    institution_count = AcademicCenter.objects.filter(
        id__in=TrainingRequest.objects.filter(
            participants__gt=0,
            sem_start_date__lte=datetime.now()
        ).values_list('training_planner__academic_id').distinct()
    ).aggregate(Count('id'))

    context = {
        'states': states,
        'participant_count': counts['participants__sum'],
        'training_count': counts['id__count'],
        'institution_count': institution_count['id__count'],
    }
    return render(request, 'statistics/templates/maphome.html', context)

@rate_limited_view
def get_state_info(request, code):
    state = None
    try:
        state = State.objects.get(code=code)
        # academic_list = AcademicCenter.objects.filter(state = state).values_list('id')

        academic_centers = AcademicCenter.objects.filter(
            state=state,
            id__in=TrainingRequest.objects.filter(
                participants__gt=0,
                sem_start_date__lte=datetime.now()
            ).values_list('training_planner__academic_id').distinct()
        ).count()
        # workshop_details = Training.objects.filter(academic_id__in = academic_list, status = 4).aggregate(Sum('participant_count'), Count('id'), Min('tdate'))
        workshop_details = TrainingRequest.objects.filter(
            participants__gt=0,
            sem_start_date__lte=datetime.now(),
            training_planner__academic__state_id=state.id
        ).aggregate(Sum('participants'), Count('id'), Min('sem_start_date'))
        context = {
            'state': state,
            'workshops': workshop_details['id__count'],
            'participants': workshop_details['participants__sum'],
            'academic_centers': academic_centers,
            'from_date': workshop_details['sem_start_date__min']
        }
        return render(request, 'statistics/templates/get_state_info.html', context)
    except Exception as e:
        print(e)
        return HttpResponse('<h4 style="margin: 30px;">Permission Denied!</h4>')

@rate_limited_view
def training(request):
    """ Organiser index page """
    stats_key = 'stats:' + md5(str(sorted(request.GET.items())).encode()).hexdigest()
    cached_page = cache.get(stats_key)
    while cached_page and cached_page == 'In progress':
        sleep(60)
        cached_page = cache.get(stats_key)
    if cached_page:
        return HttpResponse(cached_page)
    cache.set(stats_key, 'In progress', 60 * 30)  # 30 min
    collectionSet = TrainingRequest.objects.filter(
            sem_start_date__lte=datetime.now()
        ).select_related('training_planner__academic__state', 'training_planner__academic__city', 'training_planner__organiser__user', 'course', 'course__foss', 'department').order_by('-sem_start_date')
    state = None
    TRAINING_COMPLETED = '1'
    TRAINING_PENDING = '0'
    if request.method == 'GET':
        status = request.GET.get('status')
        if status not in [TRAINING_COMPLETED, TRAINING_PENDING]:
            status = TRAINING_COMPLETED

        lang= request.GET.get('lang')
        if status == TRAINING_COMPLETED:
            if lang and '---------' not in lang:
                print(f"\033[92m Lang ******* \033[0m")
                training_attend_lang = TrainingAttend.objects.filter(language__name=lang).values_list('training_id').distinct()
                collectionSet= collectionSet.filter(id__in=training_attend_lang)
        
        
    if status == TRAINING_PENDING:
        collectionSet = collectionSet.filter(participants=0, status=TRAINING_COMPLETED)
        
    else:
        collectionSet = collectionSet.filter(participants__gt=0)
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('training_planner__academic__state__name', True, 'State'),
        3: SortableHeader('training_planner__academic__city__name', True, 'City'),
        4: SortableHeader('training_planner__academic__institution_name', True, 'Institution'),
        5: SortableHeader('course__foss__foss', True, 'FOSS'),
        6: SortableHeader('department', True, 'Department'),
        7: SortableHeader('course__category', True, 'Type'),
        8: SortableHeader('training_planner__organiser__user__first_name', True, 'Organiser'),
        9: SortableHeader('sem_start_date', True, 'Date'),
        10: SortableHeader('participants', 'True', 'Participants'),
        11: SortableHeader('Action', False)
    }

    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collectionSet, header, raw_get_data)
    ordering = get_field_index(raw_get_data)

    
    # find state id
    if 'training_planner__academic__state' in request.GET and request.GET['training_planner__academic__state']:
        state = State.objects.get(id=request.GET['training_planner__academic__state'])
    collection = TrainingRequestFilter(request.GET, queryset=collection, state=state)
    # find participants count
    
    participants = collection.qs.aggregate(Sum('participants'))
    if lang == 'English':
        participants = participants['participants__sum']+294593

    else:
        participants = participants['participants__sum']

    chart_query_set = collection.qs.extra(select={'year': "EXTRACT(year FROM sem_start_date)"}).values('year').order_by(
            '-year').annotate(total_training=Count('sem_start_date'), total_participant=Sum('participants'))
    chart_data = ''
    
    get_year = []
    pending_attendance_participant_count = 0
    key = ''.join('None' if i == '' or i == '---------' else str(i).replace(" ", "") for i in request.GET.values())
    key = key if key else 'NoneNoneNoneNoneNoneNoneNoneNoneNoneNone1'
    # female_key = key + 'female'
    # male_key = key + 'male'
    # femalecount = cache.get(female_key)
    # malecount = cache.get(male_key)
    # if status != 0:
    #     if not femalecount or not malecount:
    #         gender_counts = TrainingAttend.objects.filter(training__in=collection.qs).values('student__gender').annotate(gender_count=Count('student__gender'))

    #         for item in gender_counts:
    #             if item['student__gender'] == 'Female':
    #                 femalecount = item['gender_count']
    #             if item['student__gender'] == 'Male':
    #                 malecount = item['gender_count']
    #         try:
    #             cache.set(female_key, femalecount)
    #             cache.set(male_key, malecount)
    #         except Exception:
    #             print('Error setting cache key values')

    year_data_all=dict()
    visited=dict()
    if status == TRAINING_PENDING:

        pending_attendance_student_batches = StudentBatch.objects.filter(
            id__in=(collection.qs.filter(status=TRAINING_COMPLETED,participants=0,batch_id__gt=0).values('batch_id'))
            )
        pending_attendance_training = collection.qs.filter(batch_id__in = pending_attendance_student_batches.filter().values('id')).distinct()

        for batch in pending_attendance_student_batches:
            pending_attendance_participant_count += batch.stcount
        for a_traning in pending_attendance_training:
            if a_traning.batch_id not in visited:
                if a_traning.sem_start_date.year in year_data_all:
                    visited[a_traning.batch_id] = [a_traning.batch_id]
                    year_data_all[a_traning.sem_start_date.year] +=  a_traning.batch.stcount
                else:
                    visited[a_traning.batch_id] = [a_traning.batch_id]
                    year_data_all[a_traning.sem_start_date.year] =  a_traning.batch.stcount


    if status == TRAINING_COMPLETED:
        for data in chart_query_set:
            chart_data += "['" + str(data['year']) + "', " + str(data['total_participant']) + "],"
    else:
        for year,count in list(year_data_all.items()):
            chart_data += "['" + str(year) + "', " + str(count) + "],"
    
    no_of_colleges=collection.qs.filter().values('training_planner__academic_id').distinct().count()
    context = {}
    context['form'] = collection.form
    context['chart_data'] = chart_data
    page = request.GET.get('page')    
    collection = get_page(collection.qs, page )
    context['collection'] = collection
    participants_attended = {}
    training_ids = [training.id for training in collection.object_list]
    data = (TrainingAttend.objects.filter(training_id__in=training_ids).values('training_id').annotate(student_count=Count('student_id')))

    participants_attended = {entry['training_id']: entry['student_count'] for entry in data} 
    context['participants_attended'] = participants_attended
    context['header'] = header
    context['ordering'] = ordering
    if status == TRAINING_PENDING:
        context['participants'] = pending_attendance_participant_count
    else:
        context['participants'] = participants
    context['model'] = 'Workshop/Training'
    context['status']=status
    # context['femalecount'] = femalecount
    # context['malecount'] = malecount
    context['no_of_colleges'] = no_of_colleges

    context['language'] = Language.objects.values('id','name')

    #render without cache
    response = render(request, 'statistics/templates/training.html', context)
    cache.set(stats_key, response.content, 60 * 30) # 30 min
    return response


@rate_limited_view
def fdp_training(request):
    """ Organiser index page """
    collectionSet = None
    state = None

    collectionSet = TrainingRequest.objects.filter(
        participants__gt=0,
        department=169,
        sem_start_date__lte=datetime.now()
    ).order_by('-sem_start_date')
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('training_planner__academic__state__name', True, 'State'),
        3: SortableHeader('training_planner__academic__city__name', True, 'City'),
        4: SortableHeader('training_planner__academic__institution_name', True, 'Institution'),
        5: SortableHeader('course__foss__foss', True, 'FOSS'),
        6: SortableHeader('department', True, 'Department'),
        7: SortableHeader('course__category', True, 'Type'),
        8: SortableHeader('training_planner__organiser__user__first_name', True, 'Organiser'),
        9: SortableHeader('sem_start_date', True, 'Date'),
        10: SortableHeader('participants', 'True', 'Participants'),
        11: SortableHeader('Action', False)
    }

    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collectionSet, header, raw_get_data)
    ordering = get_field_index(raw_get_data)

    # find state id
    if 'training_planner__academic__state' in request.GET and request.GET['training_planner__academic__state']:
        state = State.objects.get(id=request.GET['training_planner__academic__state'])

    collection = TrainingRequestFilter(request.GET, queryset=collection, state=state)
    # find participants count
    participants = collection.qs.aggregate(Sum('participants'))
    # gender_counts = TrainingAttend.objects.filter(training__in=collection.qs).values('student__gender').annotate(gender_count=Count('student__gender'))
    # femalecount = 0
    # malecount = 0
    # for item in gender_counts:
    #     if item['student__gender'] == 'Female':
    #         femalecount = item['gender_count']
    #     if item['student__gender'] == 'Male':
    #         malecount = item['gender_count']
    
    chart_query_set = collection.qs.extra(select={'year': "EXTRACT(year FROM sem_start_date)"}).values('year').order_by(
        '-year').annotate(total_training=Count('sem_start_date'), total_participant=Sum('participants'))
    chart_data = ''
    for data in chart_query_set:
        chart_data += "['" + str(data['year']) + "', " + str(data['total_participant']) + "],"

    no_of_colleges=collection.qs.filter().values('training_planner__academic_id').distinct().count()   

    context = {}
    context['form'] = collection.form
    context['chart_data'] = chart_data
    page = request.GET.get('page')
    collection = get_page(collection.qs, page)
    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering
    context['participants'] = participants
    context['model'] = 'Workshop/Training'
    # context['femalecount'] = femalecount
    # context['malecount'] = malecount
    context['no_of_colleges'] = no_of_colleges
    return render(request, 'statistics/templates/pmmm_stats.html', context)

@rate_limited_view
def training_participant(request, rid):
    context = {}
    try:
        context['model_label'] = 'Workshop / Training'
        context['model'] = TrainingRequest.objects.get(id=rid)
        context['collection'] = TrainingAttend.objects.filter(training_id=rid).select_related('student', 'student__user')
    except Exception as e:
        print(e)
        raise PermissionDenied()
    return render(request, 'statistics/templates/training_participant.html', context)

@rate_limited_view
def studentmaster_ongoing(request, rid):
    
    context = {}
    try:
        context['model_label'] = 'Workshop / Training'
        context['model'] = TrainingRequest.objects.get(id=rid)
        current_batch = TrainingRequest.objects.filter(id=rid)
        for ab in current_batch:
            row_data = StudentMaster.objects.filter(batch_id=ab.batch_id)
        context['collection'] = row_data

    except Exception as e:
        print(e)
        raise ObjectDoesNotExist()
    return render(request, 'statistics/templates/training_participant.html', context)

@rate_limited_view
def online_test(request):
    """ Organiser index page """
    collectionSet = None
    participant_count = 0

    collectionSet = Test.objects.filter(status=4, participant_count__gt=0).order_by('-tdate')
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('academic__state__name', True, 'State'),
        3: SortableHeader('academic__city__name', True, 'City'),
        4: SortableHeader('academic__institution_name', True, 'Institution'),
        5: SortableHeader('foss__foss', True, 'FOSS'),
        6: SortableHeader('organiser__user__first_name', True, 'Organiser'),
        7: SortableHeader('invigilator__user__email', True, 'Invigilator'),
        8: SortableHeader('tdate', True, 'Date'),
        9: SortableHeader('participant_count', 'True', 'Participants'),
        10: SortableHeader('training__department__name', True, 'Department'),
        11: SortableHeader('Action', False)
        
    }

    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collectionSet, header, raw_get_data)
    ordering = get_field_index(raw_get_data)

    # find state id
    state = None
    if 'academic__state' in request.GET and request.GET['academic__state']:
        state = State.objects.get(id=request.GET['academic__state'])

    collection = TestFilter(request.GET, queryset=collection, state=state)
    # find participants count
    participant_count = collection.qs.aggregate(Sum('participant_count'))
    #
    chart_query_set = collection.qs.extra(select={'year': "EXTRACT(year FROM tdate)"}).values('year').order_by(
        '-year').annotate(total_training=Count('tdate'), total_participant=Sum('participant_count'))
    chart_data = ''
    for data in chart_query_set:
        chart_data += "['" + str(data['year']) + "', " + str(data['total_participant']) + "],"
    
    no_of_colleges=collection.qs.filter().values('academic_id').distinct().count()   
    print(" ********************** no of colleges: ", no_of_colleges)

    context = {}
    context['form'] = collection.form
    context['chart_data'] = chart_data
    page = request.GET.get('page')
    collection = get_page(collection.qs, page)
    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering
    context['participant_count'] = participant_count
    context['model'] = 'Online-Test'
    context['no_of_colleges'] = no_of_colleges
    return render(request, 'statistics/templates/online_test.html', context)

@rate_limited_view
def test_participant(request, rid):
    context = {}
    if not rid:
        raise PermissionDenied()
    try:
        context['model_label'] = 'Online-Test'
        context['model'] = Test.objects.get(id=rid)
        test_mdlusers = TestAttendance.objects.using('default').filter(
            test_id=rid, status__gte=2).values_list('mdluser_id')
        ids = []
        for wp in test_mdlusers:
            ids.append(wp[0])
        context['collection'] = MdlUser.objects.using('moodle').filter(id__in=ids)
    except Exception:
        raise PermissionDenied()
    return render(request, 'statistics/templates/participant.html', context)

@rate_limited_view
def academic_center(request, slug=None):
    context = {}
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('State', False),
        3: SortableHeader('institution_name', True, 'Institution Name'),
        4: SortableHeader('Training', False),
        5: SortableHeader('Participants', True),
        6: SortableHeader('Action', False)
    }

    collection = None
    start_date = request.GET.get('training__tdate_0', 0)
    end_date = request.GET.get('training__tdate_1', 0)
    lookup = None
    training_query = TrainingRequest.objects.filter(
        participants__gt=0,
        sem_start_date__lte=datetime.now()
    )
    if start_date or end_date:
        if start_date and end_date:
            lookup = [start_date, end_date]
        elif start_date:
            lookup = [start_date, now()]
        else:
            lookup = [datetime.strptime('1970-01-01', '%Y-%m-%d'), end_date]
    if slug:
        collection = AcademicCenter.objects.filter(
            id__in=training_query.values_list(
                'training_planner__academic_id'
            ).distinct(),
            state__slug=slug
        ).order_by('state__name', 'institution_name')
    else:
        if lookup:
            training_query = TrainingRequest.objects.filter(
                Q(sem_start_date__range=lookup) & Q(sem_start_date__lte=datetime.now()),
                participants__gt=0
            )
            collection = AcademicCenter.objects.filter(
                id__in=training_query.values_list(
                    'training_planner__academic_id'
                ).distinct()
            ).order_by('state__name', 'institution_name')
        else:
            collection = AcademicCenter.objects.filter(
                id__in=training_query.values_list(
                    'training_planner__academic_id'
                ).distinct()
            ).order_by('state__name', 'institution_name')

    raw_get_data = request.GET.get('o', None)
    collection = get_sorted_list(request, collection, header, raw_get_data)
    ordering = get_field_index(raw_get_data)

    collection = AcademicCenterFilter(request.GET, queryset=collection)
    context['form'] = collection.form
    context['total_training'] = training_query.count()
    participant_count = training_query.aggregate(Sum('participants'))
    print(participant_count)
    context['total_participant'] = participant_count['participants__sum']

    page = request.GET.get('page')
    collection = get_page(collection.qs, page)
    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering

    return render(request, 'statistics/templates/academic-center.html', context)

@rate_limited_view
def academic_center_view(request, academic_id=None, slug=None):
    collection = get_object_or_404(AcademicCenter, id=academic_id)
    slug_title = slugify(collection.institution_name)
    if slug != slug_title:
        return HttpResponseRedirect('/statistics/academic-center/' + str(collection.id) + '/' + slug_title)
    context = {
        'collection': collection
    }
    return render(request, 'statistics/templates/view-academic-center.html', context)

@rate_limited_view
def motion_chart(request):
    collection = TrainingRequest.objects.filter(
        participants__gt=0, sem_start_date__lte=datetime.now()
    ).values(
        'training_planner__academic__state__name', 'sem_start_date'
    ).annotate(tcount=Count('sem_start_date'), pcount=Sum('participants'))

    interactive_workshop_data = ""
    static_workshop_data = ""
    states = {}
    for row in collection:
        curr_state = str(row['training_planner__academic__state__name'])
        if curr_state in states:
            states[curr_state]['tcount'] += int(row['tcount'])
            states[curr_state]['pcount'] += int(row['pcount'])
        else:
            states[curr_state] = {}
            states[curr_state]['tcount'] = int(row['tcount'])
            states[curr_state]['pcount'] = int(row['pcount'])
        js_date = 'new Date(' + str(row['sem_start_date'].year) + ', ' + \
            str(int(row['sem_start_date'].month) - 1) + ', ' + str(row['sem_start_date'].day) + ')'
        interactive_workshop_data += "['" + curr_state + "', " + js_date + \
            ", " + str(row['tcount']) + ", " + str(row['pcount']) + "],"

    for key, value in list(states.items()):
        curr_year = str(datetime.now().year)
        static_workshop_data += "['" + key + "', " + curr_year + ", " + \
            str(value['tcount']) + ", " + str(value['pcount']) + "],"

    context = {
        'interactive_workshop_data': interactive_workshop_data,
        'static_workshop_data': static_workshop_data,
    }

    return render(request, 'statistics/templates/motion_charts.html', context)

@rate_limited_view
def learners(request):
    context = {}
    form = LearnerForm()
    if request.method == 'POST':
        form = LearnerForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request, "Thank you for submitting your details. You can choose your course and then continue..")
                return HttpResponseRedirect('/tutorial-search/?search_foss=&search_language=')
            except Exception as e:
                print(e)
                messages.success(request, "Sorry, something went wrong, Please try again!")
    context['form'] = form
    return render(request, 'statistics/templates/learners.html', context)

@rate_limited_view
def tutorial_content(request, template='statistics/templates/statistics_content.html'):
    header = {
        1: SortableHeader('# ', False),
        2: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial'),
        3: SortableHeader('tutorial_detail__foss__foss', True, 'FOSS Course'),
        4: SortableHeader('tutorial_detail__level', True, 'Level'),
        5: SortableHeader('language__name', True, 'Language'),
        6: SortableHeader('publish_at', True, 'Date Published')
    }

    published_tutorials_set = TutorialResource.objects.filter(Q(status=1) | Q(status=2))

    raw_get_data = request.GET.get('o', None)
    tutorials = get_sorted_list(request, published_tutorials_set, header, raw_get_data)
    ordering = get_field_index(raw_get_data)

    tutorials_filter = CreationStatisticsFilter(request.GET, queryset=tutorials)
    # whenever publish date filter is applied there is a table join, resulting a duplicate entry for tutorials 
    # because single tutorial might have multiple pushish objects
    qs = tutorials_filter.qs.distinct()
    no_of_foss = qs.filter().values('tutorial_detail__foss_id').distinct().count()

    context = {}

    context['form'] = tutorials_filter.form

    # display information table across multiple pages
    paginator = Paginator(qs, 100)
    page = request.GET.get('page')
    try:
        tutorials = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tutorials = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tutorials = paginator.page(paginator.num_pages)
    context['tutorials'] = tutorials
    context['tutorial_num'] = tutorials.paginator.count
    context['header'] = header
    context['ordering'] = ordering
    context['no_of_foss'] = no_of_foss

    return render(request, template, context)


@rate_limited_view
def ilw_stats(request):
    queryset =TrainingEvents.objects.filter(training_status=2).order_by('-event_start_date')
    context = {} 

    REG_COMPLETED = '1'
    CLOSED_TRAINING = '2'

    if request.method == 'GET':
        status = request.GET.get('status')
        if status not in [REG_COMPLETED, CLOSED_TRAINING]:
            status = CLOSED_TRAINING
    if status == REG_COMPLETED:
        queryset = TrainingEvents.objects.filter(training_status=1).order_by('-event_start_date')
    elif status == CLOSED_TRAINING:
        queryset = TrainingEvents.objects.filter(training_status=2).order_by('-event_start_date')


    header = {
        1: SortableHeader('#', False),
        2: SortableHeader(
          'state__name',
          True,
          'State'
        ),
        3: SortableHeader(
          'host_college__academic_code',
          True,
          'Code'
        ),
        4: SortableHeader(
          'host_college__institution_name',
          True,
          'Institution'
        ),
        5: SortableHeader('foss__foss', True, 'Foss Name'),
        6: SortableHeader(
          'event_coordinator_name',
          True,
          'Coordinator'
        ),
        7: SortableHeader(
          'registartion_end_date',
          True,
          'Registration Period'
        ),
        8: SortableHeader(
          'event_start_date',
          True,
          'Event Start Date'
        ),
        9: SortableHeader(
          'event_end_date',
          True,
          'Event End Date'
        ),
        10: SortableHeader('Participant Count', True),
        11: SortableHeader('Action', False)
        }

    raw_get_data = request.GET.get('o', None)


    queryset = get_sorted_list(
        request,
        queryset,
        header,
        raw_get_data
    )
    collection= EventStatsFilter(request.GET, queryset=queryset)
  
    femalecount =0
    malecount =0

    qs = collection.qs.select_related('state', 'foss', 'host_college')
    if status == REG_COMPLETED:
        participants = Participant.objects.filter(event_id__in=qs, reg_approval_status=1)
        pcount = participants.count()
        femalecount = participants.filter(gender__in=('f','F','female','Female','FEMALE')).count()
        malecount = participants.filter(gender__in=('m','M','male','Male','MALE')).count()
        
    
    elif status == CLOSED_TRAINING:
        participants = EventAttendance.objects.filter(event_id__in=qs)
        pcount=participants.count()
        femalecount = participants.filter(participant__gender__in=('f','F','female','Female','FEMALE')).count()
        malecount = participants.filter(participant__gender__in=('m','M','male','Male','MALE')).count()
    
    context['form'] = collection.form
    page = request.GET.get('page')
    collection = get_page(qs, page)

    # map of TrainingEvent id and participant count
    paginated_qs = collection.object_list
    ongoing_event_id = []
    completed_event_id = []
    
    for event in paginated_qs:
        if event.training_status <= 1:
            ongoing_event_id.append(event.id)
        elif event.training_status == 2:
            completed_event_id.append(event.id)
    
    participants = list(Participant.objects.filter(event_id__in=ongoing_event_id, reg_approval_status=1).values('event_id').annotate(count=Count('event_id')))
    ea = list(EventAttendance.objects.filter(event_id__in=completed_event_id).values('event_id').annotate(count=Count('event_id')))
    
    event_pcount_map = {}
    for d in participants + ea:
        event_pcount_map[d['event_id']] = d['count']
    
    # context values
    context['collection'] = collection
    context['header'] = header
    context['participants'] = pcount
    context['femalecount'] = femalecount
    context['malecount'] = malecount
    context['status'] = status
    context['event_pcount_map'] = event_pcount_map
    return render(request, 'statistics/templates/ilw_stats.html', context)
