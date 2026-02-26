from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from .models import ConsentVersion, UserConsent
from .utils import is_student_user

CONSENT_SESSION_KEY = 'consent_version_id'


class ConsentMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return self.get_response(request)

        if not is_student_user(user):
            return self.get_response(request)

        path = request.path
        consent_url = reverse('consent:consent')
        if (
            path.startswith('/admin/')
            or path.startswith(consent_url)
            or path.startswith(settings.STATIC_URL)
            or path.startswith(settings.MEDIA_URL)
        ):
            return self.get_response(request)

        active = ConsentVersion.objects.filter(is_active=True).first()
        if not active:
            return self.get_response(request)

        session_version = request.session.get(CONSENT_SESSION_KEY)
        if session_version == active.pk:
            return self.get_response(request)

        if UserConsent.objects.filter(user=user, consent=active).exists():
            request.session[CONSENT_SESSION_KEY] = active.pk
            return self.get_response(request)

        return redirect('%s?next=%s' % (consent_url, request.get_full_path()))
