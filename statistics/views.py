# Standard Library
from datetime import datetime
import itertools


# Third Party Stuff
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Min, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import slugify
from django.utils.timezone import now

# Spoken Tutorial Stuff
from cms.sortable import *
from events.filters import AcademicCenterFilter, TestFilter, TrainingRequestFilter
from events.models import *
from creation.models import TutorialResource, TutorialDetail
from creation.views import is_contributor
from creation.filters import CreationStatisticsFilter
from events.views import get_page
from .forms import LearnerForm
from statistics import services


# Create your views here.
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
        # workshop_details = Training.objects.filter(academic_id__in =
        # academic_list, status = 4).aggregate(Sum('participant_count'),
        # Count('id'), Min('tdate'))
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
    except Exception, e:
        print e
        return HttpResponse('<h4 style="margin: 30px;">Permission Denied!</h4>')


def training(request):
    """ Organiser index page """
    collectionSet = None
    state = None

    collectionSet = TrainingRequest.objects.filter(
        participants__gt=0,
        sem_start_date__lte=datetime.now()
    ).order_by('-sem_start_date')
    header = {
        1: SortableHeader('#', False),
        2: SortableHeader('training_planner__academic__state__name', True, 'State'),
        3: SortableHeader('training_planner__academic__city__name', True, 'City'),
        4: SortableHeader('training_planner__academic__institution_name', True, 'Institution'),
        5: SortableHeader('course__foss__foss', True, 'FOSS'),
        6: SortableHeader('course__category', True, 'Type'),
        7: SortableHeader('training_planner__organiser__user__first_name', True, 'Organiser'),
        8: SortableHeader('sem_start_date', True, 'Date'),
        9: SortableHeader('participants', 'True', 'Participants'),
        10: SortableHeader('Action', False)
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
    #
    chart_query_set = collection.qs.extra(select={'year': "EXTRACT(year FROM sem_start_date)"}).values('year').order_by(
        '-year').annotate(total_training=Count('sem_start_date'), total_participant=Sum('participants'))
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
    context['participants'] = participants
    context['model'] = 'Workshop/Training'
    return render(request, 'statistics/templates/training.html', context)


def training_participant(request, rid):
    context = {}
    try:
        context['model_label'] = 'Workshop / Training'
        context['model'] = TrainingRequest.objects.get(id=rid)
        context['collection'] = TrainingAttend.objects.filter(training_id=rid)
    except Exception, e:
        print e
        raise PermissionDenied()
    return render(request, 'statistics/templates/training_participant.html', context)


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
        7: SortableHeader('tdate', True, 'Date'),
        8: SortableHeader('participant_count', 'True', 'Participants'),
        9: SortableHeader('Action', False)
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
    context = {}
    context['form'] = collection.form
    context['chart_data'] = chart_data
    page = request.GET.get('page')
    collection = get_page(collection, page)
    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering
    context['participant_count'] = participant_count
    context['model'] = 'Online-Test'
    return render(request, 'statistics/templates/online_test.html', context)


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
    print participant_count
    context['total_participant'] = participant_count['participants__sum']

    page = request.GET.get('page')
    collection = get_page(collection, page)
    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering

    return render(request, 'statistics/templates/academic-center.html', context)


def academic_center_view(request, academic_id=None, slug=None):
    collection = get_object_or_404(AcademicCenter, id=academic_id)
    slug_title = slugify(collection.institution_name)
    if slug != slug_title:
        return HttpResponseRedirect('/statistics/academic-center/' + str(collection.id) + '/' + slug_title)
    context = {
        'collection': collection
    }
    return render(request, 'statistics/templates/view-academic-center.html', context)


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

    for key, value in states.iteritems():
        curr_year = str(datetime.now().year)
        static_workshop_data += "['" + key + "', " + curr_year + ", " + \
            str(value['tcount']) + ", " + str(value['pcount']) + "],"

    context = {
        'interactive_workshop_data': interactive_workshop_data,
        'static_workshop_data': static_workshop_data,
    }

    return render(request, 'statistics/templates/motion_charts.html', context)


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
            except Exception, e:
                print e
                messages.success(request, "Sorry, something went wrong, Please try again!")
    context['form'] = form
    return render(request, 'statistics/templates/learners.html', context)


def tutorial_content(request, template='statistics/templates/statistics_content.html'):
    header = {
        1: SortableHeader('# ', False),
        2: SortableHeader('Tutorial', False),
        3: SortableHeader('tutorial_detail__foss__foss', True, 'FOSS Course'),
        4: SortableHeader('Level', False),
        5: SortableHeader('language__name', False, 'Language'),
        6: SortableHeader('tutorial_detail__created', False, 'Date Published')
    }

    published_tutorials_set = TutorialResource.objects.filter(status__gte=1)

    raw_get_data = request.GET.get('o', None)
    tutorials = get_sorted_list(request, published_tutorials_set, header, raw_get_data)
    ordering = get_field_index(raw_get_data)

    tutorials = CreationStatisticsFilter(request.GET, queryset=tutorials)

    context = {}

    context['form'] = tutorials.form

    # display information table across multiple pages
    paginator = Paginator(tutorials, 100)
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

    return render(request, template, context)


def allocate_tutorial(request, status):
    context = {}

    user = request.user
    if not (user.is_authenticated() and (is_contributor(user))):
        raise PermissionDenied()

    active = status
    final_query = None
    fosses = []

    if status == 'completed':
        header = {
            1: SortableHeader('# ', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'FOSS Course'),
            3: SortableHeader('Tutorial', False),
            4: SortableHeader('language__name', False, 'Language'),
            5: SortableHeader('created', False, 'Date Created'),
            6: SortableHeader('script_user_id', False, 'User Details'),
        }

        status = 4
        final_query = TutorialResource.objects.filter(script_status=status)

    elif status == 'available':
        header = {
            1: SortableHeader('# ', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'FOSS Course'),
            3: SortableHeader('Tutorial', False),
            4: SortableHeader('language__name', False, 'Language'),
            5: SortableHeader('Bid', False),
        }

        all_tuts = TutorialDetail.objects.all()

        foss_to_allocate = {}
        for tutorial in all_tuts:
            if services.check_english_timed_script_available(tutorial):
                a_l = services.get_available_languages(tutorial)
                foss_name = str(tutorial.foss.foss)
                foss_to_allocate = [foss_name, tutorial, a_l]
                fosses.append(foss_to_allocate)
                

    elif status == 'ongoing':
        header = {
            1: SortableHeader('# ', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'FOSS Course'),
            3: SortableHeader('Tutorial', False),
            4: SortableHeader('language__name', False, 'Language'),
            5: SortableHeader('script_user_id', False, 'User ID'),
            6: SortableHeader('Bid Date', False),
            7: SortableHeader('Submission Date',False)
        }

        status = 4
        final_query = TutorialResource.objects.filter(script_status__lt=status).exclude(language_id=22)

    else:
        raise PermissionDenied()

    available_tutorials_count = 0
    for item in fosses:
        available_tutorials_count = available_tutorials_count + len(item[2])

    user = User.objects.get(pk=user.id)

    pub_tutorials_set = final_query
    raw_get_data = request.GET.get('o', None)
    tutorials = get_sorted_list(request, pub_tutorials_set, header, raw_get_data)
    ordering = get_field_index(raw_get_data)
    tutorials = CreationStatisticsFilter(request.GET, queryset=tutorials)

    context['form'] = tutorials.form
    for a in tutorials:
        a.updated = a.created + timedelta(days=10)

    # if active == 'completed' or active == 'ongoing':
    # display information table across multiple pages
    paginator = Paginator(tutorials, 100)
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
    context['status'] = active
    context['fosses'] = fosses
    context['available_tutorials_count'] = available_tutorials_count
    context['counter'] = itertools.count(1)
   # context['submission_date'] = submission_date
    return render(request, 'statistics/templates/allocate_tutorial.html', context)


def allocate(request, tdid, lid):
    user = request.user

    tut = TutorialDetail.objects.get(pk=tdid)
    if not ContributorRole.objects.filter(
            foss_category_id=tut.foss_id, user_id=user.id, language_id=lid):
        contributor_role = ContributorRole()
        contributor_role.foss_category_id = tut.foss_id
        contributor_role.user_id = user.id
        contributor_role.language_id = lid
        contributor_role.status = True
        contributor_role.save()

    common_content = TutorialCommonContent.objects.get(tutorial_detail_id=tdid)

    tutorial_resource = TutorialResource()
    tutorial_resource.tutorial_detail_id = tdid
    tutorial_resource.common_content_id = common_content.id
    tutorial_resource.language_id = lid
    tutorial_resource.outline_user = user
    tutorial_resource.script_user = user
    tutorial_resource.video_user = user
    tutorial_resource.script_status = 0
    # tutorial_resource.bid_date = datetime.now()
    tutorial_resource.save()

    return HttpResponseRedirect('/statistics/allocate_tutorial/ongoing/')
