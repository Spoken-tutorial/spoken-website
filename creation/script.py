# Standard Library
from urllib import urlopen

# Third Party Stuff
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q

# Spoken Tutorial Stuff
from creation.models import *
from creation.views import is_administrator


@login_required
def list_missing_script(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    trs = TutorialResource.objects.filter(Q(status=1) | Q(status=2))
    for tr_rec in trs:
        storage_path = tr_rec.script
        script_path = settings.SCRIPT_URL + storage_path
        try:
            code = 0
            try:
                code = urlopen(script_path).code
            except Exception, e:
                code = e.code
            if not (int(code) == 200):
                print '{0},{1},{2},{3},{4},{5}'.format(code, tr_rec.id,
                                                       tr_rec.tutorial_detail.foss,
                                                       tr_rec.language,
                                                       tr_rec.tutorial_detail.tutorial,
                                                       script_path)
        except Exception as e:
            print(e)
