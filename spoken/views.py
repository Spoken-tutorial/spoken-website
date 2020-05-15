import datetime as dt
import json
import os
from urllib.parse import quote, unquote_plus
from urllib.request import urlopen

# Third Party Stuff
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
#change here .. no csrf 

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.template.context_processors import csrf
from django.core.urlresolvers import reverse

# Spoken Tutorial Stuff
from cms.forms import *
from cms.models import Event, News, NewsType, Notification, SiteFeedback
from creation.models import Language, TutorialDetail, TutorialResource
from creation.subtitles import *
from creation.views import get_video_info
from events.views import get_page
from forums.models import Question

from .filters import NewsStateFilter, MediaTestimonialsFossFilter
from .forms import *
from .search import search_for_results


def is_resource_person(user):
    """Check if the user is having resource person  rights"""
    if user.groups.filter(name='Resource Person').count() == 1:
        return True


@csrf_exempt
def site_feedback(request):
    data = request.POST
    if data:
        try:
            SiteFeedback.objects.create(name=data['name'], email=data['email'], message=data['message'])
            data = True
        except Exception as e:
            print(e)
            data = False

    return HttpResponse(json.dumps(data), content_type='application/json')


def home(request):
    tr_rec = ''

    foss = list(TutorialResource.objects.filter(Q(status=1) | Q(status=2)).order_by(
        '?').values_list('tutorial_detail__foss_id').distinct()[:9])
    random_tutorials = []
    # eng_lang = Language.objects.get(name='English')
    for f in foss:
        tcount = TutorialResource.objects.filter(Q(status=1) | Q(
            status=2), tutorial_detail__foss_id=f, language__name='English').order_by('tutorial_detail__order').count()
        tutorial = TutorialResource.objects.filter(Q(status=1) | Q(
            status=2), tutorial_detail__foss_id=f, language__name='English').order_by('tutorial_detail__order')[:1].first()
        random_tutorials.append((tcount, tutorial))
    try:
        tr_rec = TutorialResource.objects.filter(Q(status=1) | Q(status=2)).order_by('?')[:1].first()
    except Exception as e:
        messages.error(request, str(e))
    context = {
        'tr_rec': tr_rec,
        'media_url': settings.MEDIA_URL,
        'random_tutorials': random_tutorials,
    }

    testimonials = Testimonials.objects.all().order_by('?')[:2]
    context['testimonials'] = testimonials

    notifications = Notification.objects.filter(Q(start_date__lte=dt.datetime.today()) & Q(
        expiry_date__gte=dt.datetime.today())).order_by('expiry_date')
    context['notifications'] = notifications

    events = Event.objects.filter(event_date__gte=dt.datetime.today()).order_by('event_date')[:2]
    context['events'] = events
    return render(request, 'spoken/templates/home.html',context= context)


def get_or_query(terms, search_fields):
    # terms = ['linux', ' operating system', ' computers', ' hardware platforms', ' oscad']
    # search_fields = ['keyword']
    query = None
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query | or_query
    print(query)
    return query


def keyword_search(request):
    context = {}
    keyword = ''
    collection = None
    correction = None
    form = AllTutorialSearchForm()
    if request.method == 'GET' and 'q' in request.GET and request.GET['q'] != '':
        form = KeywordSearchForm(request.GET)
        if form.is_valid():
            keyword = request.GET['q'].lower()
            collection, correction = search_for_results(keyword)

    if collection:
        page = request.GET.get('page')
        collection = get_page(collection, page)
    

    context = {}
    context['form'] = KeywordSearchForm()
    context['collection'] = collection
    context['correction'] = correction
    context['keywords'] = keyword
    context.update(csrf(request))
    return render(request, 'spoken/templates/keyword_search.html', context)


@csrf_exempt
def tutorial_search(request):
    context = {}
    collection = None
    form = TutorialSearchForm()
    foss_get = ''
    show_on_homepage = 1
    queryset = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage = show_on_homepage)

    if request.method == 'GET' and request.GET:
        form = TutorialSearchForm(request.GET)
        if form.is_valid():
            foss_get = request.GET.get('search_foss', '')
            language_get = request.GET.get('search_language', '')
            if foss_get and language_get:
                collection = queryset.filter(tutorial_detail__foss__foss=foss_get, language__name=language_get).order_by('tutorial_detail__level', 'tutorial_detail__order')

            elif foss_get:
                collection = queryset.filter(tutorial_detail__foss__foss=foss_get).order_by('tutorial_detail__level', 'tutorial_detail__order', 'language__name')
            elif language_get:
                collection = queryset.filter(language__name=language_get).order_by('tutorial_detail__foss__foss', 'tutorial_detail__level', 'tutorial_detail__order')
            else:
                collection = queryset.filter(tutorial_detail__foss__id__in=FossCategory.objects.values('id'), language__id__in=Language.objects.values('id')).order_by('tutorial_detail__foss__foss', 'language__name', 'tutorial_detail__level', 'tutorial_detail__order')
    else:
        foss = queryset.filter(language__name='English').values('tutorial_detail__foss__foss').annotate(Count('id')).values_list('tutorial_detail__foss__foss').distinct().order_by('?')[:1].first()
        collection = queryset.filter(tutorial_detail__foss__foss=foss[0], language__name='English')
        foss_get = foss[0]
    if collection:
        page = request.GET.get('page')
        collection = get_page(collection, page)
    context['form'] = form
    context['collection'] = collection
    context['SCRIPT_URL'] = settings.SCRIPT_URL
    context['current_foss'] = foss_get
    return render(request, 'spoken/templates/tutorial_search.html', context)

def list_videos(request):
    form = TutorialSearchForm()
    context = {}
    context['form'] = form
    return render(request, 'spoken/templates/list_videos_form.html', context)

def series_foss(request):
    '''
    Get all the media testimonials which are set to not 
    show on home page and display along the form to display the tutorials.
    '''
    form = SeriesTutorialSearchForm()
    collection = None
    # Get all the video / audio testimonials in series
    foss_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), language__name='English', tutorial_detail__foss__show_on_homepage = 0).values_list('tutorial_detail__foss__id').annotate().distinct()
    collection =  MediaTestimonials.objects.filter(foss__id__in=foss_list).values("foss__foss", "content", "created", "foss", "foss_id", "id", "path", "user", "workshop_details").order_by('-created')
    
    if collection:
        page = request.GET.get('page')
        collection = get_page(collection, page, limit=6)
    
    add_button_show= False
    if request.user.has_perm('events.add_testimonials'):
        add_button_show= True
    context = {}
    context['form'] = form
    context['collection'] = collection
    context['media_url'] = settings.MEDIA_URL
    context['add_button_show'] = add_button_show
    return render(request, 'spoken/templates/series_foss_list.html', context)

@csrf_exempt
def series_tutorial_search(request):
    context = {}
    collection = None
    form = SeriesTutorialSearchForm()
    foss_get = ''
    show_on_homepage = 0
    queryset = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage = show_on_homepage)
    
    if request.method == 'GET' and request.GET:
        form = SeriesTutorialSearchForm(request.GET)
        if form.is_valid():
            foss_get = request.GET.get('search_otherfoss', '')
            language_get = request.GET.get('search_otherlanguage', '')
            if foss_get and language_get:
                collection = queryset.filter(tutorial_detail__foss__foss=foss_get, language__name=language_get).order_by('tutorial_detail__level', 'tutorial_detail__order')

            elif foss_get:
                collection = queryset.filter(tutorial_detail__foss__foss=foss_get).order_by('tutorial_detail__level', 'tutorial_detail__order', 'language__name')
            elif language_get:
                collection = queryset.filter(language__name=language_get).order_by('tutorial_detail__foss__foss', 'tutorial_detail__level', 'tutorial_detail__order')
            else:
                collection = queryset.filter(tutorial_detail__foss__id__in=FossCategory.objects.values('id'), language__id__in=Language.objects.values('id')).order_by('tutorial_detail__foss__foss', 'language__name', 'tutorial_detail__level', 'tutorial_detail__order')
    else:
        foss = queryset.filter(language__name='English').values('tutorial_detail__foss__foss').annotate(Count('id')).values_list('tutorial_detail__foss__foss').distinct().order_by('?')[:1].first()
        collection = queryset.filter(tutorial_detail__foss__foss=foss[0], language__name='English')
        foss_get = foss[0]
    if collection:
        page = request.GET.get('page')
        collection = get_page(collection, page)
    context['form'] = form
    context['collection'] = collection
    context['SCRIPT_URL'] = settings.SCRIPT_URL
    context['current_foss'] = foss_get
    return render(request, 'spoken/templates/series_tutorial_search.html', context)

def archived_foss(request):
    form = ArchivedTutorialSearchForm()
    collection = None    
    context = {}
    context['form'] = form
    return render(request, 'spoken/templates/archived_foss_list.html', context)

@csrf_exempt
def archived_tutorial_search(request):
    context = {}
    collection = None
    form = ArchivedTutorialSearchForm()
    foss_get = ''
    show_on_homepage = 2
    queryset = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage = show_on_homepage)
    
    if request.method == 'GET' and request.GET:
        form = ArchivedTutorialSearchForm(request.GET)
        if form.is_valid():
            foss_get = request.GET.get('search_archivedfoss', '')
            language_get = request.GET.get('search_archivedlanguage', '')
            if foss_get and language_get:
                collection = queryset.filter(tutorial_detail__foss__foss=foss_get, language__name=language_get).order_by('tutorial_detail__level', 'tutorial_detail__order')

            elif foss_get:
                collection = queryset.filter(tutorial_detail__foss__foss=foss_get).order_by('tutorial_detail__level', 'tutorial_detail__order', 'language__name')
            elif language_get:
                collection = queryset.filter(language__name=language_get).order_by('tutorial_detail__foss__foss', 'tutorial_detail__level', 'tutorial_detail__order')
            else:
                collection = queryset.filter(tutorial_detail__foss__id__in=FossCategory.objects.values('id'), language__id__in=Language.objects.values('id')).order_by('tutorial_detail__foss__foss', 'language__name', 'tutorial_detail__level', 'tutorial_detail__order')
    else:
        foss = queryset.filter(language__name='English').values('tutorial_detail__foss__foss').annotate(Count('id')).values_list('tutorial_detail__foss__foss').distinct().order_by('?')[:1].first()
        collection = queryset.filter(tutorial_detail__foss__foss=foss[0], language__name='English')
        foss_get = foss[0]
    if collection:
        page = request.GET.get('page')
        collection = get_page(collection, page)
    context['form'] = form
    context['collection'] = collection
    context['SCRIPT_URL'] = settings.SCRIPT_URL
    context['current_foss'] = foss_get
    return render(request, 'spoken/templates/archived_tutorial_search.html', context)


def watch_tutorial(request, foss, tutorial, lang):
    try:
        foss = unquote_plus(foss)
        tutorial = unquote_plus(tutorial)
        td_rec = TutorialDetail.objects.get(foss__foss=foss, tutorial=tutorial)
        tr_rec = TutorialResource.objects.select_related().get(tutorial_detail=td_rec, language=Language.objects.get(name=lang))
        tr_recs = TutorialResource.objects.select_related('tutorial_detail').filter(Q(status=1) | Q(status=2), tutorial_detail__foss=tr_rec.tutorial_detail.foss, language=tr_rec.language).order_by(
            'tutorial_detail__foss__foss', 'tutorial_detail__level', 'tutorial_detail__order', 'language__name')
        questions = Question.objects.filter(category=td_rec.foss.foss.replace(
            ' ', '-'), tutorial=td_rec.tutorial.replace(' ', '-')).order_by('-date_created')
    except Exception as e:
        messages.error(request, str(e))
        return HttpResponseRedirect('/')
    video_path = settings.MEDIA_ROOT + "videos/" + \
        str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.video
    video_info = get_video_info(video_path)
    context = {
        'tr_rec': tr_rec,
        'tr_recs': tr_recs,
        'questions': questions,
        'video_info': video_info,
        'media_url': settings.MEDIA_URL,
        'media_path': settings.MEDIA_ROOT,
        'tutorial_path': str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail_id) + '/',
        'script_base': settings.SCRIPT_URL
    }
    return render(request, 'spoken/templates/watch_tutorial.html', context)

# link to watch what is spoken tutorial video in english


def what_is_spoken_tutorial(request):
    try:
        foss = unquote_plus("Spoken+Tutorial+Technology")
        tutorial = unquote_plus('What+is+a+Spoken+Tutorial')
        td_rec = TutorialDetail.objects.get(foss__foss=foss, tutorial=tutorial)
        tr_rec = TutorialResource.objects.select_related().get(
            tutorial_detail=td_rec, language=Language.objects.get(name='English'))
        tr_recs = TutorialResource.objects.select_related('tutorial_detail').filter(Q(status=1) | Q(status=2), tutorial_detail__foss=tr_rec.tutorial_detail.foss, language=tr_rec.language).order_by(
            'tutorial_detail__foss__foss', 'tutorial_detail__level', 'tutorial_detail__order', 'language__name')
        questions = Question.objects.filter(category=td_rec.foss.foss.replace(
            ' ', '-'), tutorial=td_rec.tutorial.replace(' ', '-')).order_by('-date_created')
    except Exception as e:
        messages.error(request, str(e))
        return HttpResponseRedirect('/')
    video_path = settings.MEDIA_ROOT + "videos/" + \
        str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.video
    video_info = get_video_info(video_path)
    context = {
        'tr_rec': tr_rec,
        'tr_recs': tr_recs,
        'questions': questions,
        'video_info': video_info,
        'media_url': settings.MEDIA_URL,
        'media_path': settings.MEDIA_ROOT,
        'tutorial_path': str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail_id) + '/',
        'script_base': settings.SCRIPT_URL
    }
    return render(request, 'spoken/templates/watch_tutorial.html', context)


@csrf_exempt
def get_language(request, tutorial_type):
    output = ''
    show_on_homepage = 1
    if tutorial_type== "series":
        show_on_homepage = 0
    if tutorial_type== "archived":
        show_on_homepage = 2

    if request.method == "POST":
        foss = request.POST.get('foss')
        lang = request.POST.get('lang')
        if not lang and foss:
            lang_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage = show_on_homepage, tutorial_detail__foss__foss=foss).values(
                'language__name').annotate(Count('id')).order_by('language__name').values_list('language__name', 'id__count').distinct()
            tmp = '<option value = ""> -- All Languages -- </option>'
            for lang_row in lang_list:
                tmp += '<option value="' + str(lang_row[0]) + '">' + \
                    str(lang_row[0]) + ' (' + str(lang_row[1]) + ')</option>'
            output = ['foss', tmp]
        elif lang and not foss:
            foss_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage = show_on_homepage, language__name=lang).values('tutorial_detail__foss__foss').annotate(
                Count('id')).order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()
            tmp = '<option value = ""> -- All Courses -- </option>'
            for foss_row in foss_list:
                tmp += '<option value="' + str(foss_row[0]) + '">' + \
                    str(foss_row[0]) + ' (' + str(foss_row[1]) + ')</option>'
            output = ['lang', tmp]
        elif foss and lang:
            pass
        else:
            lang_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage = show_on_homepage).values('language__name').annotate(
                Count('id')).order_by('language__name').values_list('language__name', 'id__count').distinct()
            tmp1 = '<option value = ""> -- All Languages -- </option>'
            for lang_row in lang_list:
                tmp1 += '<option value="' + str(lang_row[0]) + '">' + \
                    str(lang_row[0]) + ' (' + str(lang_row[1]) + ')</option>'
            foss_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage = show_on_homepage,language__name='English').values('tutorial_detail__foss__foss').annotate(
                Count('id')).order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()
            tmp2 = '<option value = ""> -- All Courses -- </option>'
            for foss_row in foss_list:
                tmp2 += '<option value="' + str(foss_row[0]) + '">' + \
                    str(foss_row[0]) + ' (' + str(foss_row[1]) + ')</option>'
            output = ['reset', tmp1, tmp2]
    return HttpResponse(json.dumps(output), content_type='application/json')


def testimonials(request, testimonial_type="text"):
    '''
    Responds with `/testimonial` page to display all the 
    text / video / audio template.
    '''
    collection = None
    if testimonial_type == "text":
        collectionSet = Testimonials.objects.all().order_by('-created')
    else:
        collectionSet = MediaTestimonials.objects.all().order_by('-created')
    collection = MediaTestimonialsFossFilter(request.GET, queryset=collectionSet)
    
    if collection:
        page = request.GET.get('page')
        testimonials = get_page(collection.qs, page, limit=6)
        form = collection.form

    context = {}
    context['form'] = form
    context['collection'] = testimonials
    context['media_url'] = settings.MEDIA_URL
    context['testimonial_type'] = testimonial_type
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/testimonials.html', context)

def foss_testimonials(request, foss):
    '''
    Responds with `/testimonial` page to display all the 
    text / video / audio template.
    '''
    collection = None
    collection = MediaTestimonials.objects.filter(foss__foss=foss).values("foss__foss", "content", "created", "foss", "foss_id", "id", "path", "user").order_by('-created')
    if foss == "General":
        #excludng biogas, koha and health series from the list
        exclude_foss_list = [82,100,70]
        collection = MediaTestimonials.objects.all().exclude(foss__id__in=exclude_foss_list).values("foss__foss", "content", "created", "foss", "foss_id", "id", "path", "user").order_by('-created')
    
    if collection:
        page = request.GET.get('page')
        collection = get_page(collection, page, limit=6)

    context = {}
    context['collection'] = collection
    context['media_url'] = settings.MEDIA_URL
    context['foss'] = foss
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/mediatestimonials.html', context)


def testimonials_new_media(request, testimonial_type):
    '''
    Responds with form for video/audio testimonials 
    to be uploaded and POST request checks and stores 
    the response in file system and database.
    '''
    user = request.user
    if not user.has_perm('events.add_testimonials'):
        raise PermissionDenied()
    
    context = {}
    if testimonial_type == 'series':
        form = MediaTestimonialForm(on_home_page=0)
    else:
        form = MediaTestimonialForm(on_home_page=1)

    if request.method == 'POST':
        if testimonial_type == 'series':
            form = MediaTestimonialForm(request.POST, request.FILES, on_home_page=0)
        else:
            form = MediaTestimonialForm(request.POST, request.FILES, on_home_page=1)
        if form.is_valid():
            foss = FossCategory.objects.get(foss=request.POST.get('foss'))
            if not request.FILES:
                messages.error(request, 'Nothing uploaded. Choose a file for paste a link')
            else:
                file_container = request.FILES['media']
                # Put the uploaded file in the desired location.
                file_name = str(user) + '-' + dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + file_container.name[-4:]
                file_path = settings.MEDIA_ROOT + 'testimonials/' + str(foss.id) + '/' 
                from_media_path =  'testimonials/' + str(foss.id) + '/' + file_name
                os.system("mkdir -p %s" % file_path)
                full_path = file_path + file_name
                fout = open(full_path, 'wb+')
                # Iterate through the chunks.
                for chunk in file_container.chunks():
                    fout.write(chunk)
                fout.close()
                # Save in database
                data = MediaTestimonials(foss=foss, path=from_media_path, user=request.POST.get('name'),workshop_details=request.POST.get('workshop_details'), content= request.POST.get('content'))
                print(data)
                messages.success(request, 'Testimonial has posted successfully!')
                data.save()
            return HttpResponseRedirect('/')
    context['form'] = form
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/mediaform.html', context)


def admin_testimonials_media_edit(request, rid):
    user = request.user
    context = {}
    testimonial = get_object_or_404(MediaTestimonials, pk=rid)
    if request.method == 'POST':
        form = MediaTestimonialEditForm(request.POST, instance=testimonial)
        if form.is_valid():
            form.save()
            context['form'] = form
            messages.success(request, 'Testimonial updated successfully!')
            return HttpResponseRedirect('/admin/testimonials/')
        else:
            context['form'] = form
            context['instance'] = testimonial
            context.update(csrf(request))
            return render(request, 'spoken/templates/testimonial/mediaform.html', context)
        
    form = MediaTestimonialEditForm(instance=testimonial)
    context['form'] = form
    context['instance'] = testimonial
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/mediaform.html', context)


def testimonials_new(request):
    ''' 
    Responds with form for text testimonials 
    to be uploaded and POST request checks and stores 
    the response in the database.
    '''
    user = request.user
    context = {}
    if not user.has_perm('events.add_testimonials'):
        raise PermissionDenied()
    
    form = TestimonialsForm()
    if request.method == 'POST':
        form = TestimonialsForm(request.POST, request.FILES)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user_id = user.id
            form_data.save()
            rid = form_data.id
            file_type = ['application/pdf']
            if 'scan_copy' in request.FILES:
                if request.FILES['scan_copy'].content_type in file_type:
                    file_path = settings.MEDIA_ROOT + 'testimonial/'
                    try:
                        os.mkdir(file_path)
                    except Exception as e:
                        print(e)
                    file_path = settings.MEDIA_ROOT + 'testimonial/' + str(rid) + '/'
                    try:
                        os.mkdir(file_path)
                    except Exception as e:
                        print(e)
                    full_path = file_path + str(rid) + ".pdf"
                    fout = open(full_path, 'wb+')
                    f = request.FILES['scan_copy']
                    # Iterate through the chunks.
                    for chunk in f.chunks():
                        fout.write(chunk)
                    fout.close()

            messages.success(request, 'Testimonial has posted successfully!')
            return HttpResponseRedirect('/')
    context['form'] = form
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/form.html', context)


def admin_testimonials_edit(request, rid):
    user = request.user
    context = {}
    form = TestimonialsForm()
    instance = ''
    if not user.has_perm('events.change_testimonials'):
        raise PermissionDenied()
    try:
        instance = Testimonials.objects.get(pk=rid)
    except Exception as e:
        raise Http404('Page not found')
        print(e)

    if request.method == 'POST':
        form = TestimonialsForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user_id = user.id
            form_data.save()
            file_type = ['application/pdf','image/jpeg','image/png']
            if 'scan_copy' in request.FILES:
                if request.FILES['scan_copy'].content_type in file_type:
                    file_path = settings.MEDIA_ROOT + 'testimonial/'
                    try:
                        os.mkdir(file_path)
                    except Exception as e:
                        print(e)
                    file_path = settings.MEDIA_ROOT + 'testimonial/' + str(rid) + '/'
                    try:
                        os.mkdir(file_path)
                    except Exception as e:
                        print(e)
                    f = request.FILES['scan_copy']
                    filename = str(f)
                    ext = os.path.splitext(filename)[1].lower()
                    full_path = file_path + str(rid) + ext
                    fout = open(full_path, 'wb+')

                    # Iterate through the chunks.
                    for chunk in f.chunks():
                        fout.write(chunk)
                    fout.close()

            messages.success(request, 'Testimonial updated successfully!')
            return HttpResponseRedirect('/')

    form = TestimonialsForm(instance=instance)
    context['form'] = form
    context['instance'] = instance
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/form.html', context)


def admin_testimonials_delete(request, rid):
    user = request.user
    context = {}
    instance = ''
    if not user.has_perm('events.delete_testimonials'):
        raise PermissionDenied()
    try:
        instance = Testimonials.objects.get(pk=rid)
    except Exception as e:
        raise Http404('Page not found')
        print(e)
    if request.method == 'POST':
        instance = Testimonials.objects.get(pk=rid)
        instance.delete()
        messages.success(request, 'Testimonial deleted successfully')
        return HttpResponseRedirect(reverse('admin_testimonials'))
    context['instance'] = instance
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/form.html', context)


def admin_testimonials_media_delete(request, rid):
    user = request.user
    context = {}
    instance = ''
    if not user.has_perm('events.delete_testimonials'):
        raise PermissionDenied()
    try:
        instance = MediaTestimonials.objects.get(pk=rid)
    except Exception as error:
        print(error)
        raise Http404('Page not found')
    if request.method == 'POST':
        instance = MediaTestimonials.objects.get(pk=rid)
        instance.delete()
        messages.success(request, 'Testimonial deleted successfully')
        return HttpResponseRedirect(reverse('admin_testimonials'))
    context['instance'] = instance
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/mediaform.html', context)


def admin_testimonials(request):
    ''' 
    admin testimonials:
        Page for administrators to view / add / edit / delete testimonials.
    '''
    user = request.user
    context = {}
    if not user.has_perm('events.add_testimonials') and not user.has_perm('events.change_testimonials'):
        raise PermissionDenied()
    collection = Testimonials.objects.all()
    mediacollection = MediaTestimonials.objects.all()
    context['collection'] = collection
    context['mediacollection'] = mediacollection
    context['media_url'] = settings.MEDIA_URL
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/index.html', context)


def news(request, cslug):
#    try:
        newstype = NewsType.objects.get(slug=cslug)
        collection = None
        latest = None
        sortAllowedCategory = ['articles-on-university-tie-ups-workshops',
                               'articles-on-spoken-tutorial-project', 'events-from-iitb', 'events-across-india']
        if request.GET and 'latest' in request.GET and int(request.GET.get('latest')) == 1 and (cslug in sortAllowedCategory):
            collection = newstype.news_set.order_by('weight', '-created')
        else:
            collection = newstype.news_set.order_by('-created')
            latest = True
        collection = NewsStateFilter(request.GET, queryset=collection, news_type_slug=cslug)
        #print ("\n collection :",collection.qs.count())
        form = collection.form
        if collection:
            page = request.GET.get('page')

            print ("\n collection :",collection.qs.count())
            collection = get_page(collection.qs, page)
        context = {
            'form': form,
            'collection': collection,
            'category': cslug,
            'newstype': newstype,
            'latest': latest,
            'sortAllowedCategory': sortAllowedCategory
        }
        context.update(csrf(request))
        return render(request, 'spoken/templates/news/index.html', context)

    # except Exception as e:
    #     print(e)
    #     raise Http404('You are not allowed to view this page')

def news_view(request, cslug, slug):
    try:
        # 301 redirection. Enable this after categories all to new
        """
        if cslug == 'media-articles':
            news = News.objects.get(slug = slug)
            redirect_url = "/news/"+news.news_type.slug+"/"+news.slug
            return HttpResponsePermanentRedirect(redirect_url)
        """

        # newstype = NewsType.objects.get(slug=cslug)
        news = News.objects.get(slug=slug)
        image_or_doc = None
        if news.picture:
            supported_formats = ['.gif', '.png', '.bmp', '.jpg', '.jpeg']
            file_name, file_extension = os.path.splitext(settings.MEDIA_ROOT + str(news.picture))
            image_or_doc = 1
            if not (file_extension.lower() in supported_formats):
                image_or_doc = 2
        context = {
            'news': news,
            'image_or_doc': image_or_doc,
        }
        context.update(csrf(request))
        return render(request, 'spoken/templates/news/view-news.html', context)

    except Exception as e:
        print(e)
        raise Http404('You are not allowed to view this page')


def create_subtitle_files(request, overwrite=True):
    rows = TutorialResource.objects.filter(Q(status=1) | Q(status=2))
    for row in rows:
        code = 0
        if row.language.name == 'English':
            if row.timed_script and row.timed_script != 'pending':
                script_path = settings.SCRIPT_URL.strip('/') + '?title=' + quote(row.timed_script) + '&printable=yes'
            elif row.script and row.script != 'pending':
                script_path = settings.SCRIPT_URL.strip('/') + '?title=' + \
                    quote(row.script + '-timed') + '&printable=yes'
            else:
                continue
        else:
            if row.script and row.script != 'pending':
                script_path = settings.SCRIPT_URL.strip('/') + '?title=' + quote(row.script) + '&printable=yes'
            else:
                continue
        srt_file_path = settings.MEDIA_ROOT + 'videos/' + \
            str(row.tutorial_detail.foss_id) + '/' + str(row.tutorial_detail_id) + '/'
        srt_file_name = row.tutorial_detail.tutorial.replace(' ', '-') + '-' + row.language.name + '.srt'
        # print srt_file_name
        if not overwrite and os.path.isfile(srt_file_path + srt_file_name):
            continue
        try:
            code = urlopen(script_path).code
        except Exception as e:
            code = e.code
        if(int(code) == 200):
            if generate_subtitle(script_path, srt_file_path + srt_file_name):
                print(('Success: ', row.tutorial_detail.foss.foss + ',', srt_file_name))
            else:
                print(('Failed: ', row.tutorial_detail.foss.foss + ',', srt_file_name))
    return HttpResponse('Success!')


def sitemap(request):
    return render(request, 'sitemap.html', {})


def add_user(request):
    username = None
    password = None
    email = None
    count = 1
    f = open('/websites_dir/django_spoken/spoken/spoken/users', 'r')
    ulist = f.read().splitlines()
    f.close()
    for data in ulist:
        username = data
        password = data
        email = data
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            profile = Profile(user=user, confirmation_code='12345')
            profile.save()
            count += 1
        except Exception as e:
            print(e)
    return HttpResponse("success")


def ViewBrochures(request):
    template_name = 'spoken/templates/brochures.html'
    return render(request, template_name)


def learndrupal(request):
    return render(request, 'spoken/templates/learndrupal.html')

def induction_2017(request):
    EOI_count = InductionInterest.objects.all().count()
    context = {'EOI_count': EOI_count}
    context.update(csrf(request))
    return render(request, 'spoken/templates/induction_2017.html', context)


def induction_2017_new(request):
    return render(request, 'spoken/templates/induction_2017_new.html')

def expression_of_intrest(request):
    return render(request, 'spoken/templates/expression_of_intrest.html')


def expression_of_intrest_new(request):
    form = ExpressionForm()
    if request.method == 'POST':
        form = ExpressionForm(request.POST)
        if form.is_valid():
            try:
                form_data = form.save(commit=False)
                form_data.save()
                messages.success(request, "Your response has been recorded. Thanks for giving your inputs. In case there are more than 120 eligible applicants, we will get back to you about a selection criterion.")
                return HttpResponseRedirect('/induction')
            except Exception as e:
                print(e)
                messages.error(request, "Sorry, something went wrong, Please try again!")
                # return HttpResponseRedirect('/induction')
    context = {
        'form' : form,
    }
    context = {}
    context['form'] = form
    return render(request, 'spoken/templates/expression_of_intrest_old.html', context)

# def nmeict_intro(request):
#     return render(request, 'spoken/templates/nmeict_intro.html')