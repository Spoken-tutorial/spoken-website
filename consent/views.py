import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError
from django.shortcuts import redirect, render

from .middleware import CONSENT_SESSION_KEY
from .models import Consent, UserConsent


@login_required
def consent_view(request):
    active = Consent.objects.filter(is_active=True).first()
    if not active:
        return HttpResponseServerError('Consent file is not configured.')

    if not active.file or not os.path.isfile(active.file.path):
        return HttpResponseServerError('Consent file is not configured.')

    if request.method == 'POST':
        UserConsent.objects.get_or_create(
            user=request.user,
            consent=active,
        )
        request.session[CONSENT_SESSION_KEY] = active.pk
        return redirect('/')

    with open(active.file.path, 'r', encoding='utf-8', errors='replace') as fh:
        consent_text = fh.read()

    return render(request, 'consent/consent.html', {
        'consent_text': consent_text,
    })
