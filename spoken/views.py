# Standard Library
import datetime as dt
import json
import os
from urllib import quote, unquote_plus, urlopen

# Third Party Stuff
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from forms import *

# Spoken Tutorial Stuff
from cms.forms import *
from cms.models import Event, News, NewsType, Notification, SiteFeedback
from creation.models import Language, TutorialDetail, TutorialResource
from creation.subtitles import *
from creation.views import get_video_info
from events.views import get_page
from forums.models import Question
from spoken.filters import NewsStateFilter
from spoken.search import search_for_results


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
        except Exception:
            data = False

    return HttpResponse(json.dumps(data), content_type='application/json')


def home(request):
    t_resource_qs = TutorialResource.objects.filter(Q(status=1) | Q(status=2))
    foss = t_resource_qs.order_by('?').values_list('tutorial_detail__foss_id', flat=True).distinct()[:9]

    random_tutorials = []
    # eng_lang = Language.objects.get(name='English')
    for f in foss:
        qs = t_resource_qs.filter(tutorial_detail__foss_id=f, language__name='English')
        tcount = qs.count()
        tutorial = qs.first()
        random_tutorials.append((tcount, tutorial))

    tr_rec = t_resource_qs.order_by('?').first()

    ctx = {
        'tr_rec': tr_rec,
        'media_url': settings.MEDIA_URL,
        'random_tutorials': random_tutorials,
    }

    ctx['testimonials'] = Testimonials.objects.all().order_by('?')[:2]

    today = dt.datetime.today()
    ctx['notifications'] = Notification.objects.filter(Q(start_date__lte=today) & Q(expiry_date__gte=today)
                                                       ).order_by('expiry_date')

    ctx['events'] = Event.objects.filter(event_date__gte=dt.datetime.today()).order_by('event_date')[:2]
    return render(request, 'spoken/templates/home.html', ctx)


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
    return query


def keyword_search(request):
    context = {}
    keyword = ''
    collection = None
    correction = None
    # conjunction_words = ['a', 'i']
    form = TutorialSearchForm()
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
    t_resource_qs = TutorialResource.objects.filter(Q(status=1) | Q(status=2))
    if request.method == 'GET' and request.GET:
        form = TutorialSearchForm(request.GET)
        if form.is_valid():
            foss_get = request.GET.get('search_foss', '')
            language_get = request.GET.get('search_language', '')
            if foss_get and language_get:
                collection = t_resource_qs.filter(tutorial_detail__foss__foss=foss_get,
                                                  language__name=language_get).order_by(
                    'tutorial_detail__level', 'tutorial_detail__order')
            elif foss_get:
                collection = t_resource_qs.filter(tutorial_detail__foss__foss=foss_get).order_by(
                    'tutorial_detail__level', 'tutorial_detail__order', 'language__name')
            elif language_get:
                collection = t_resource_qs.filter(language__name=language_get).order_by(
                    'tutorial_detail__foss__foss', 'tutorial_detail__level', 'tutorial_detail__order')
            else:
                collection = t_resource_qs.filter(tutorial_detail__foss__id__in=FossCategory.objects.values(
                    'id'), language__id__in=Language.objects.values('id')).order_by(
                    'tutorial_detail__foss__foss', 'language__name', 'tutorial_detail__level', 'tutorial_detail__order')
    else:
        foss = t_resource_qs.filter(language__name='English').values('tutorial_detail__foss__foss').annotate(
            Count('id')).values_list('tutorial_detail__foss__foss').distinct().order_by('?')[:1].first()
        collection = t_resource_qs.filter(tutorial_detail__foss__foss=foss[0], language__name='English')
        foss_get = foss[0]
    if collection:
        page = request.GET.get('page')
        collection = get_page(collection, page)
    context['form'] = form
    context['collection'] = collection
    context['SCRIPT_URL'] = settings.SCRIPT_URL
    context['current_foss'] = foss_get
    return render(request, 'spoken/templates/tutorial_search.html', context)


def watch_tutorial(request, foss, tutorial, lang):
    try:
        foss = unquote_plus(foss)
        tutorial = unquote_plus(tutorial)
        td_rec = TutorialDetail.objects.get(foss__foss=foss, tutorial=tutorial)
        tr_rec = TutorialResource.objects.select_related().get(tutorial_detail=td_rec,
                                                               language=Language.objects.get(name=lang))
        tr_recs = TutorialResource.objects.select_related('tutorial_detail').filter(
            Q(status=1) | Q(status=2),
            tutorial_detail__foss=tr_rec.tutorial_detail.foss,
            language=tr_rec.language).order_by(
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
        tr_rec = TutorialResource.objects.select_related().get(tutorial_detail=td_rec,
                                                               language=Language.objects.get(name='English'))
        tr_recs = TutorialResource.objects.select_related('tutorial_detail').filter(
            Q(status=1) | Q(status=2),
            tutorial_detail__foss=tr_rec.tutorial_detail.foss,
            language=tr_rec.language).order_by(
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
def get_language(request):
    output = ''
    t_resource_qs = TutorialResource.objects.filter(Q(status=1) | Q(status=2))
    if request.method == "POST":
        foss = request.POST.get('foss')
        lang = request.POST.get('lang')
        if not lang and foss:
            lang_list = t_resource_qs.filter(tutorial_detail__foss__foss=foss).values('language__name').annotate(
                Count('id')).order_by('language__name').values_list('language__name', 'id__count').distinct()
            tmp = '<option value = ""> -- All Languages -- </option>'
            for lang_row in lang_list:
                tmp += '<option value="' + str(lang_row[0]) + '">' + \
                    str(lang_row[0]) + ' (' + str(lang_row[1]) + ')</option>'
            output = ['foss', tmp]
        elif lang and not foss:
            foss_list = t_resource_qs.filter(language__name=lang).values('tutorial_detail__foss__foss').annotate(
                Count('id')).order_by('tutorial_detail__foss__foss').values_list(
                'tutorial_detail__foss__foss', 'id__count').distinct()
            tmp = '<option value = ""> -- All Courses -- </option>'
            for foss_row in foss_list:
                tmp += '<option value="' + str(foss_row[0]) + '">' + \
                    str(foss_row[0]) + ' (' + str(foss_row[1]) + ')</option>'
            output = ['lang', tmp]
        elif foss and lang:
            pass
        else:
            lang_list = t_resource_qs.values('language__name').annotate(Count('id')).order_by(
                'language__name').values_list('language__name', 'id__count').distinct()
            tmp1 = '<option value = ""> -- All Languages -- </option>'
            for lang_row in lang_list:
                tmp1 += '<option value="' + str(lang_row[0]) + '">' + \
                    str(lang_row[0]) + ' (' + str(lang_row[1]) + ')</option>'
            foss_list = t_resource_qs.filter(language__name='English').values('tutorial_detail__foss__foss').annotate(
                Count('id')).order_by('tutorial_detail__foss__foss').values_list(
                'tutorial_detail__foss__foss', 'id__count').distinct()
            tmp2 = '<option value = ""> -- All Courses -- </option>'
            for foss_row in foss_list:
                tmp2 += '<option value="' + str(foss_row[0]) + '">' + \
                    str(foss_row[0]) + ' (' + str(foss_row[1]) + ')</option>'
            output = ['reset', tmp1, tmp2]
    return HttpResponse(json.dumps(output), content_type='application/json')


def testimonials(request):
    testimonials = Testimonials.objects.all()
    context = {'testimonials': testimonials}
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/testimonials.html', context)


def testimonials_new(request):
    ''' new testimonials '''
    user = request.user
    context = {}
    form = TestimonialsForm()
    if (not user.is_authenticated()) or ((not user.has_perm('events.add_testimonials'))):
        raise PermissionDenied()

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
                    except Exception, e:
                        print e
                    file_path = settings.MEDIA_ROOT + 'testimonial/' + str(rid) + '/'
                    try:
                        os.mkdir(file_path)
                    except Exception, e:
                        print e
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
    if (not user.is_authenticated()) or ((not user.has_perm('events.change_testimonials'))):
        raise PermissionDenied()
    try:
        instance = Testimonials.objects.get(pk=rid)
    except Exception, e:
        raise Http404('Page not found')
        print e

    if request.method == 'POST':
        form = TestimonialsForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()

    form = TestimonialsForm(instance=instance)
    context['form'] = form
    context['instance'] = instance
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/form.html', context)


def admin_testimonials_delete(request, rid):
    user = request.user
    context = {}
    instance = ''
    if (not user.is_authenticated()) or ((not user.has_perm('events.delete_testimonials'))):
        raise PermissionDenied()
    try:
        instance = Testimonials.objects.get(pk=rid)
    except Exception, e:
        raise Http404('Page not found')
        print e
    if request.method == 'POST':
        instance = Testimonials.objects.get(pk=rid)
        instance.delete()
        messages.success(request, 'Testimonial deleted successfully')
        return HttpResponseRedirect('/admin/testimonials')
    context['instance'] = instance
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/form.html', context)


def admin_testimonials(request):
    ''' admin testimonials '''
    user = request.user
    context = {}
    if (not user.is_authenticated()) or (not user.has_perm('events.add_testimonials') and
                                         (not user.has_perm('events.change_testimonials'))):
        raise PermissionDenied()
    collection = Testimonials.objects.all()
    context['collection'] = collection
    context.update(csrf(request))
    return render(request, 'spoken/templates/testimonial/index.html', context)


def news(request, cslug):
    try:
        newstype = NewsType.objects.get(slug=cslug)
        collection = None
        latest = None
        sortAllowedCategory = ['articles-on-university-tie-ups-workshops',
                               'articles-on-spoken-tutorial-project', 'events-from-iitb', 'events-across-india']
        if (request.GET and 'latest' in request.GET and int(request.GET.get('latest')) == 1 and
                (cslug in sortAllowedCategory)):
            collection = newstype.news_set.order_by('weight')
        else:
            collection = newstype.news_set.order_by('-created')
            latest = True
        collection = NewsStateFilter(request.GET, queryset=collection, news_type_slug=cslug)
        form = collection.form
        if collection:
            page = request.GET.get('page')
            collection = get_page(collection, page)
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

    except Exception, e:
        print e
        raise Http404('You are not allowed to view this page')


def news_view(request, cslug, slug):
    try:
        # 301 redirection. Enable this after categories all to new
        """
        if cslug == 'media-articles':
            news = News.objects.get(slug = slug)
            redirect_url = "/news/"+news.news_type.slug+"/"+news.slug
            return HttpResponsePermanentRedirect(redirect_url)
        """
        NewsType.objects.get(slug=cslug)
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

    except Exception, e:
        print e
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
                print 'Success: ', row.tutorial_detail.foss.foss + ',', srt_file_name
            else:
                print 'Failed: ', row.tutorial_detail.foss.foss + ',', srt_file_name
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
        except Exception, e:
            print e
    return HttpResponse("success")
