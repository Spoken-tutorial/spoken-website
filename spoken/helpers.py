from random import sample, randint
import datetime as dt

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Q

from creation.models import TutorialSummaryCache, TutorialResource
from events.models import Testimonials
from cms.models import Notification, Event
from .config import CACHE_RANDOM_TUTORIALS, CACHE_TR_REC, CACHE_TESTIMONIALS, CACHE_NOTIFICATIONS, CACHE_EVENTS
from cms.cache_registry import register_cache_key


# ---- 1. Random tutorials from TutorialSummaryCache ----
def get_home_random_tutorials():
    cache_key = "home_random_tutorials"
    tutorials = cache.get(cache_key)
    print("tuto",tutorials)
    if tutorials is not None:
        print("tuturial exit",list(tutorials))
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
        # register_cache_key(cache_key)
    except Exception:
        tutorials = []
        print("exceptionnnnn",tutorials)
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
        register_cache_key(cache_key)
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
    register_cache_key(cache_key)
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
    register_cache_key(cache_key)
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
    register_cache_key(cache_key)
    return events
