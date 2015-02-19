import os
import re
import json
import time
import subprocess
from decimal import Decimal
from urllib import urlopen, quote, unquote_plus
from django.conf import settings
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.views.decorators.http import require_POST

from django import forms
from django.template import RequestContext
from django.core.context_processors import csrf
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from creation.views import is_administrator
from django.db.models import Q
from creation.models import *
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
                print '{0},{1},{2},{3},{4},{5}'.format(code, tr_rec.id,tr_rec.tutorial_detail.foss, tr_rec.language, tr_rec.tutorial_detail.tutorial, script_path)
        except Exception, e:
            print e
        #break
