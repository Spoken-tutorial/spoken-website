import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError
from django.shortcuts import redirect, render

from .middleware import CONSENT_SESSION_KEY
from .models import ConsentVersion, UserConsent


@login_required
def consent_view(request):
    active = ConsentVersion.objects.filter(is_active=True).first()
    if not active:
        return HttpResponseServerError('Consent file is not configured.')

    file_path = os.path.join(settings.MEDIA_ROOT, 'consent', active.file_name)
    if not os.path.isfile(file_path):
        return HttpResponseServerError('Consent file is not configured.')

    if request.method == 'POST':
        UserConsent.objects.get_or_create(
            user=request.user,
            consent=active,
        )
        request.session[CONSENT_SESSION_KEY] = active.pk
        return redirect('/')

    with open(file_path, 'r', encoding='utf-8', errors='replace') as fh:
        consent_text = fh.read()

    return render(request, 'consent/consent.html', {
        'consent_text': consent_text,
    })
