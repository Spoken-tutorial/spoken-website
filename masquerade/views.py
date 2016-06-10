
# Third Party Stuff
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.core.validators import validate_email
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Spoken Tutorial Stuff
from masquerade.forms import *
from masquerade.signals import mask_off, mask_on

MASQUERADE_REDIRECT_URL = getattr(settings, 'MASQUERADE_REDIRECT_URL', '/')
MASQUERADE_REQUIRE_SUPERUSER = getattr(settings, 'MASQUERADE_REQUIRE_SUPERUSER', True)


def masquerade_home(request):
    rows = None
    if request.method == 'POST':
        form = MasqueradeHomeForm(request.POST)
        if form.is_valid():
            key = request.POST.get('username_email', None)
            if key:
                try:
                    validate_email(key)
                    if User.objects.filter(email=key).count():
                        rows = User.objects.filter(email=key)
                    else:
                        rows = User.objects.filter(Q(username__icontains=key)).order_by('username')
                except:
                    rows = User.objects.filter(Q(username__icontains=key)).order_by('username')
    else:
        form = MasqueradeHomeForm()

    context = {
        'form': form,
        'rows': rows
    }
    context.update(csrf(request))
    return render(request, 'masquerade/masquerade_home.html', context)


@login_required
def mask(request, uid):
    if not request.user.is_masked and not request.user.is_staff:
        return PermissionDenied()
    elif not request.user.is_superuser and MASQUERADE_REQUIRE_SUPERUSER:
        return PermissionDenied()

    try:
        user = User.objects.get(pk=uid)
        request.session['mask_user'] = user.username
        mask_on.send(sender=object(), mask_username=request.session['mask_user'])
    except Exception, e:
        messages.error(request, '1) ' + str(e))
    return HttpResponseRedirect(MASQUERADE_REDIRECT_URL)


@login_required
def unmask(request):
    try:
        mask_username = request.session['mask_user']
        del(request.session['mask_user'])
        mask_off.send(sender=object(), mask_username=mask_username)
    except:
        pass

    return HttpResponseRedirect(MASQUERADE_REDIRECT_URL)
