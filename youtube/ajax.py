# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Standard Library
import json

# Third Party Stuff
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Spoken Tutorial Stuff
from creation.models import *


@csrf_exempt
def ajax_foss_based_language_tutorial(request):
    data = ''
    if request.method == 'POST':
        foss = request.POST.get('foss', '')
        lang = request.POST.get('lang', '')
        if foss and lang:
            lang_rec = Language.objects.get(pk=int(lang))
            td_list = TutorialDetail.objects.filter(foss_id=foss).values_list('id')
            tutorials = TutorialDetail.objects.filter(
                id__in=TutorialResource.objects.filter(
                    tutorial_detail_id__in=td_list,
                    language_id=lang_rec.id,
                    status__gte=1,
                    video_id__isnull=False,
                ).values_list('tutorial_detail_id')
            ).order_by('level', 'order')
            for tutorial in tutorials:
                data += '<option value="' + str(tutorial.id) + '">' + tutorial.tutorial + '</option>'
            if data:
                data = '<option value="">Select Tutorial</option>' + data
        elif foss:
            languages = Language.objects.filter(
                id__in=TutorialResource.objects.filter(
                    Q(status=1) | Q(status=2),
                    tutorial_detail__foss_id=foss,
                    video_id__isnull=False,
                ).values_list('language_id').distinct()
            ).order_by('name')
            for language in languages:
                data += '<option value="' + str(language.id) + '">' + language.name + '</option>'
            if data:
                data = '<option value="">Select Language</option>' + data

    return HttpResponse(json.dumps(data), content_type='application/json')
