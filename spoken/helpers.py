from random import sample, randint
import datetime as dt

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Q, Count

from creation.models import TutorialSummaryCache, TutorialResource
from events.models import Testimonials
from cms.models import Notification, Event
from .config import CACHE_RANDOM_TUTORIALS, CACHE_TR_REC, CACHE_TESTIMONIALS, CACHE_NOTIFICATIONS, CACHE_EVENTS, CACHE_TUTORIALS

# ---- 1. Random tutorials from TutorialSummaryCache ----
def get_home_random_tutorials():
    cache_key = "home_random_tutorials"
    tutorials = cache.get(cache_key)
    if tutorials is not None:
        return tutorials
    try:
        ids = list(
            TutorialSummaryCache.objects.all().values_list("id", flat=True)
        )
        if len(ids) >= 9:
            sample_ids = sample(ids, 9)
        else:
            sample_ids = ids
        tutorials = (
            TutorialSummaryCache.objects.filter(
                id__in=sample_ids).select_related(
                    "foss", "first_tutorial", "first_tutorial__tutorial_detail", "first_tutorial__language")
        )
        cache.set(cache_key, tutorials, timeout=CACHE_RANDOM_TUTORIALS) # in sec
    except Exception:
        tutorials = []
    return tutorials


# ---- 2. Random TutorialResource record ----
def get_home_tr_rec(request=None):
    cache_key = "home_tr_rec"
    tr_rec = cache.get(cache_key)
    if tr_rec is not None:
        return tr_rec
    try:
        queryset = TutorialResource.objects.filter(Q(status=1) | Q(status=2))
        count = queryset.count()
        if count > 0:
            random_index = randint(0, count-1)
            tr_rec = queryset[random_index]
        else:
            tr_rec = None
        cache.set(cache_key, tr_rec, timeout=CACHE_TR_REC) #seconds
    except Exception as e:
        tr_rec = None
        if request is not None:
            messages.error(request, str(e))
    return tr_rec


# ---- 3. Testimonials (longer cache) ----
def get_home_testimonials():
    cache_key = "home_testimonials"
    testimonials = cache.get(cache_key)
    if testimonials is not None:
        return testimonials
    testimonials = Testimonials.objects.all().order_by("?")[:2]
    cache.set(cache_key, testimonials, timeout=CACHE_TESTIMONIALS) # seconds
    return testimonials

# ---- 4. Notifications (shorter cache) ----
def get_home_notifications():
    cache_key = "home_notifications"
    notifications = cache.get(cache_key)
    if notifications is not None:
        return notifications
    today = dt.datetime.today()
    notifications = Notification.objects.filter(Q(start_date__lte=today) & Q(expiry_date__gte=today)).order_by("expiry_date")
    cache.set(cache_key, notifications, timeout=CACHE_NOTIFICATIONS)
    return notifications

# ---- 5. Upcoming events ----
def get_home_events():
    cache_key = "home_events"
    events = cache.get(cache_key)
    if events is not None:
        return events
    today = dt.datetime.today()
    events = Event.objects.filter(event_date__gte=today).order_by("event_date")[:2]
    cache.set(cache_key, events, timeout=CACHE_EVENTS)
    return events

# ----  Tutorials List ----
def get_tutorials_list(foss, lang):
    foss_key = f"tutorials:{foss.lower().strip().replace(' ','_')}"
    lang_key = lang.lower().strip()
    cache_key = f"{foss_key}_{lang_key}"
    tutorials = cache.get(cache_key)
    
    if tutorials is not None:
        return tutorials
    queryset = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage = 1).select_related('tutorial_detail__level', 'tutorial_detail__foss', 'language')
    if foss and lang:
        collection = queryset.filter(tutorial_detail__foss__foss=foss, language__name=lang).order_by('tutorial_detail__level', 'tutorial_detail__order')
    elif foss:
        collection = queryset.filter(tutorial_detail__foss__foss=foss).order_by('tutorial_detail__level', 'tutorial_detail__order', 'language__name')
    elif lang:
        collection = queryset.filter(language__name=lang).order_by('tutorial_detail__foss__foss', 'tutorial_detail__level', 'tutorial_detail__order')
    else:
        collection = queryset.order_by('tutorial_detail__foss__foss', 'language__name', 'tutorial_detail__level', 'tutorial_detail__order')
    cache.set(cache_key, collection, timeout=CACHE_TUTORIALS)
    return collection

# ----  Foss Choice For Search Bar ----
def get_foss_choice():
    cache_key = "tutorial_search:foss_choices"
    foss_list_choices = cache.get(cache_key)
    if foss_list_choices is not None:
        return foss_list_choices
    
    foss_list_choices = [('', '-- All Courses --'), ]
    foss_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), language__name='English', tutorial_detail__foss__show_on_homepage=1).values('tutorial_detail__foss__foss').annotate(
            Count('id')).order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()
    
    for foss_row in foss_list:
            foss_list_choices.append((str(foss_row[0]), str(foss_row[0]) + ' (' + str(foss_row[1]) + ')'))

    cache.set(cache_key, foss_list_choices, timeout=CACHE_TUTORIALS)
    return foss_list_choices



# ----  Language Choice For Search Bar ----
def get_lang_choice():
    cache_key = "tutorial_search:lang_choices"
    lang_list_choices = cache.get(cache_key)
    if lang_list_choices is not None:
        return lang_list_choices
    
    lang_list_choices = [('', '-- All Languages --'), ]
    lang_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss__show_on_homepage=1).values('language__name').annotate(
            Count('id')).order_by('language__name').values_list('language__name', 'id__count').distinct()
    for lang_row in lang_list:
        lang_list_choices.append((str(lang_row[0]), str(lang_row[0]) + ' (' + str(lang_row[1]) + ')'))

    cache.set(cache_key, lang_list_choices, timeout=CACHE_TUTORIALS)
    return lang_list_choices