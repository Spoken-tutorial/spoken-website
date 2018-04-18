# Standard Library
from datetime import datetime
import itertools
import collections

# Third Party Stuff
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import PermissionDenied,ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Min, Q, Sum, F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import slugify
from django.utils.timezone import now

# Spoken Tutorial Stuff
from cms.sortable import *
from events.filters import AcademicCenterFilter, TestFilter, TrainingRequestFilter
from events.models import *
from creation.models import TutorialResource, TutorialDetail
from creation.views import is_contributor, is_manager
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
    collectionSet = TrainingRequest.objects.filter(
            sem_start_date__lte=datetime.now()
        ).order_by('-sem_start_date')
    state = None
    TRAINING_COMPLETED = '1'
    TRAINING_PENDING = '0'

    if request.method == 'GET':
        status = request.GET.get('status')
        if status not in [TRAINING_COMPLETED, TRAINING_PENDING]:
            status = TRAINING_COMPLETED

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

    chart_query_set = collection.qs.extra(select={'year': "EXTRACT(year FROM sem_start_date)"}).values('year').order_by(
            '-year').annotate(total_training=Count('sem_start_date'), total_participant=Sum('participants'))
    chart_data = ''
    
    get_year = []
    pending_attendance_participant_count = 0

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
        for year,count in year_data_all.iteritems():
            chart_data += "['" + str(year) + "', " + str(count) + "],"
    
    context = {}
    context['form'] = collection.form
    context['chart_data'] = chart_data
    page = request.GET.get('page')
    collection = get_page(collection, page)
    context['collection'] = collection
    context['header'] = header
    context['ordering'] = ordering
    if status == TRAINING_PENDING:
        context['participants'] = pending_attendance_participant_count
    else:
        context['participants'] = participants
    context['model'] = 'Workshop/Training'
    context['status']=status

    
    return render(request, 'statistics/templates/training.html', context)

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
    return render(request, 'statistics/templates/pmmm_stats.html', context)


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

def studentmaster_ongoing(request, rid):
    
    context = {}
    try:
        context['model_label'] = 'Workshop / Training'
        context['model'] = TrainingRequest.objects.get(id=rid)
        current_batch = TrainingRequest.objects.filter(id=rid)
        for ab in current_batch:
            row_data = StudentMaster.objects.filter(batch_id=ab.batch_id)
        context['collection'] = row_data

    except Exception, e:
        print e
        raise ObjectDoesNotExist()
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
        2: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial'),
        3: SortableHeader('tutorial_detail__foss__foss', True, 'FOSS Course'),
        4: SortableHeader('tutorial_detail__level', True, 'Level'),
        5: SortableHeader('language__name', True, 'Language'),
        6: SortableHeader('publish_at', True, 'Date Published')
    }

    published_tutorials_set = TutorialResource.objects.filter(status__gte=1, status__lt = 3)

    raw_get_data = request.GET.get('o', None)
    tutorials = get_sorted_list(request, published_tutorials_set, header, raw_get_data)
    ordering = get_field_index(raw_get_data)

    tutorials_filter = CreationStatisticsFilter(request.GET, queryset=tutorials)
    # whenever publish date filter is applied there is a table join, resulting a duplicate entry for tutorials 
    # because single tutorial might have multiple pushish objects
    qs = tutorials_filter.qs.distinct()

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

    return render(request, template, context)

c_sel_lang = 0
global_req = ""
def check_stale_tuts(request,final_query):
    addy = final_query.exclude(tutorial_detail_id__tutorialresource__submissiondate__gt= datetime.date(datetime.now()-timedelta(days=10)))
    print "+++++++++++++++++\n\n\n\nFinal Submission Date : ", addy.values('tutorial_detail','submissiondate')
    
    print "fdhsb", addy.values('tutorial_detail','submissiondate')
    print "================\n\n\n\nUser's email : ", User.objects.filter(id=request.user.id).values('email')


    email = EmailMultiAlternatives(
        addy.values('tutorial_detail'), 'This tutorial has been sacked from your name ', 'workshops@spoken-tutorial.org',
        to = ('adhikarysaurabh@gmail.com',),
        headers = {
         "Content-type" : "text/html"
        }
    )
    print " Mail Connection : ", email.get_connection
    print " Mail TO : ", email.send


def allocate_tutorial(request, status):
    context = {}
    global global_req
    global_req = request 
    print "status : ", status
    user = request.user
    if not (user.is_authenticated() and (is_contributor(user))):
        raise PermissionDenied()

    active = status
    final_query = None
    fosses = []
    lang_qs = None

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
            1: SortableHeader('Tutorial Level',False),
            2: SortableHeader('Order Id', False),
            3: SortableHeader('Tutorial', False),
            4: SortableHeader('language__name', True, 'Language'),
            5: SortableHeader('Bid', False),
        }

        lang_qs = Language.objects.filter(id__in= RoleRequest.objects.filter(user = request.user ,status=1, role_type = 0).values('language'))
        status = 4 
        final_query = TutorialsAvailable.objects.filter(language__in = lang_qs).order_by('tutorial_detail__foss__foss','tutorial_detail__level','language','tutorial_detail__order')
        unique_foss = TutorialsAvailable.objects.filter(language__in = lang_qs).values('tutorial_detail__foss__foss','language','tutorial_detail__level').distinct()

    elif status == 'ongoing':
        header = {
            1: SortableHeader('# ', False),
            2: SortableHeader('tutorial_detail__level',True,'Tutorial Level'),
            3: SortableHeader('tutorial_detail__foss__foss', True, 'FOSS Course'),
            4: SortableHeader('Tutorial', False),
            5: SortableHeader('language__name', False, 'Language'),
            6: SortableHeader('script_user_id', False, 'User ID'),
            7: SortableHeader('tutorial_detail_id__tutorialresource__updated', True,'Bid Date'),
            8: SortableHeader('Submission Date',False),
            9: SortableHeader('Extension',False)
        }
        
        status = 4
        final_query = TutorialResource.objects.filter(video_user = request.user.id , assignment_status =1).exclude(language_id=22)
        stale_tuts = check_stale_tuts(request,final_query)
    else:
        raise PermissionDenied()

    extension = []
    pub_tutorials_set = final_query
    context['datetoday'] = datetime.now()
    raw_get_data = request.GET.get('o', None)
    tutorials = get_sorted_list(request, pub_tutorials_set, header, raw_get_data)
    ordering = get_field_index(raw_get_data)
    tutorials = CreationStatisticsFilter(request.GET, queryset=tutorials)
    bid_count = TutorialResource.objects.filter(video_user=request.user,assignment_status=1).count()
    print "_________________________",bid_count
    context['bid_count'] = bid_count
    context['tutorials_count'] = final_query.count()
    context['perc'] = float(bid_count *100) / float(final_query.count())  
    print "Perc : ",float(bid_count *100) / float(final_query.count())
    form = tutorials.form
    #form.fields['tutorial_detail__foss'].queryset = final_query
    #print "Currect FOSSES : ", unique_foss.tutorial_detail_id
    if lang_qs: 
        form.fields['language'].queryset = lang_qs
    
    context['form'] = form
        
    # Pagination
    paginator = Paginator(tutorials, 50)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = int(request.GET.get('page'))

    try:
        posts = paginator.page(page)
        
    except(EmptyPage,PageNotAnInteger):
        posts = paginator.page(paginator.num_pages)
    
    global c_sel_lang
    c_sel_lang = request.GET.get('language')
    print "Language : ", request.GET.get('language')
    
    context['tutorial_num'] = posts
    context['header'] = header
    context['ordering'] = ordering
    context['status'] = active

    context['counter'] = itertools.count(1)
    return render(request, 'statistics/templates/allocate_tutorial.html', context)

submissiondate = datetime.date(datetime.now()+timedelta(days=10))

def allocate(request, tdid, lid):
    user = request.user
    print "TDID : ",tdid
    tut = TutorialDetail.objects.get(id=tdid)
    print "Tutorial : ", tut
    if not ContributorRole.objects.filter(
            foss_category_id=tut.foss_id, user_id=user.id, language_id=lid):
        contributor_role = ContributorRole()
        contributor_role.foss_category_id = tut.foss_id
        contributor_role.user_id = user.id
        contributor_role.language_id = lid
        contributor_role.status = True
        contributor_role.save()

    level_name ={
    1:'Basic',
    2:'Intermediate',
    3:'Advanced' 
    }
    
    final_query = TutorialsAvailable.objects.get(tutorial_detail_id = tdid ,language = lid)
    print "final_query objects : ",final_query.tutorial_detail.foss_id, final_query.tutorial_detail.level_id
    print "YES NO :",final_query.tutorial_detail.level_id -1
    if TutorialDetail.objects.filter(foss_id = final_query.tutorial_detail.foss_id,level_id = (final_query.tutorial_detail.level_id -1)).exists():
        sa =level_name[int(final_query.tutorial_detail.level_id) - 1]
        messages.error(request,str(sa)+" level of "+str(tut.foss)+" is available. Please complete it first.")
        print "global_req : ",global_req.META['QUERY_STRING']
        return HttpResponseRedirect("/statistics/allocate_tutorial/available/?"+global_req.META['QUERY_STRING'])
    else:        
        common_content = TutorialCommonContent.objects.get(tutorial_detail_id=tdid)
        tutorial_resource = TutorialResource()
        tutorial_resource.tutorial_detail_id = tdid
        tutorial_resource.language_id = lid
        tutorial_resource.common_content_id = common_content.id
        tutorial_resource.outline_user = user
        tutorial_resource.script_user = user
        tutorial_resource.video_user = user
        # assignment_status - 
        # 0 : Not Assigned , 1 : Work in Progress , 2 : Completed
        tutorial_resource.assignment_status = 1
        print "submissiondate : ", submissiondate
        tutorial_resource.submissiondate = submissiondate
        try :
            #tutorial_resource.save()
            #TutorialsAvailable.objects.filter(tutorial_detail = tdid,language = lid).delete()
            abc = 1
        except:
            print "Already saved"
        return HttpResponseRedirect('/statistics/allocate_tutorial/ongoing/')


def extend_submission_date(request,tutorial):
    print "Tutorial : ",tutorial
    tutorial_resource = TutorialResource.objects.get(id = tutorial)
    if tutorial_resource.extension_status>1:
        messages.error(request,"You have exceeded the no of extensions")
    else:    
        tutorial_resource.submissiondate = datetime.now() + timedelta(days = 10 )
        tutorial_resource.extension_status +=1
        tutorial_resource.save()
    return HttpResponseRedirect('/statistics/allocate_tutorial/ongoing/')

def allocate_foss(request,fid):
    print "FOSS ID : ",fid
    print "Language : ",c_sel_lang
    total_days = datetime.now()
    
    if c_sel_lang:
        print "Saurabh Adhikary : ",c_sel_lang,"I am good"
        tdids = TutorialDetail.objects.filter(foss_id=fid).values('id')
        
        for a_tdid in tdids:
            tdid_available = TutorialsAvailable.objects.filter(tutorial_detail_id = a_tdid['id'], language_id = c_sel_lang)
            for available in  tdid_available:
                print "TDID : ", available
                print "a_tdid : ",a_tdid
                total_days += timedelta(days=3)
        
            global submissiondate
            submissiondate = datetime.date(total_days)
            
        for a_tdid in tdids:
            tdid_available = TutorialsAvailable.objects.filter(tutorial_detail_id = a_tdid['id'], language_id = c_sel_lang)    
            for available in  tdid_available:
                allocate(request,a_tdid['id'],c_sel_lang)    

        messages.success(request,"Submission Date is : "+str(submissiondate))
    else:
        print "I was in else "
        messages.error(request,"Please select a language")
    
    return HttpResponseRedirect('/statistics/allocate_tutorial/available/')



