# Standard Library
from builtins import str
import json

# Third Party Stuff
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Spoken Tutorial Stuff
from creation.models import Language, TutorialDetail, TutorialResource, FossCategory


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


@csrf_exempt
def get_uploadable_tutorials(request):
    """
    Get tutorials available for YouTube upload.
    Implements FK traversal: FOSSCategory → TutorialDetail → TutorialResource
    Filters by is_on_youtube=False
    
    GET params:
        foss_id: FOSSCategory ID
        language_id: Language ID
    
    Returns JSON with list of tutorials:
    {
        "tutorials": [
            {
                "id": tutorial_resource_id,
                "name": "Tutorial Name",
                "outline": "Tutorial outline text"
            },
            ...
        ]
    }
    """
    tutorials = []
    
    if request.method == 'GET':
        foss_id = request.GET.get('foss_id', '')
        language_id = request.GET.get('language_id', '')
        
        if foss_id and language_id:
            try:
                foss_id = int(foss_id)
                language_id = int(language_id)
                
                # Filter resources by FOSS, Language, and YouTube status
                tutorial_resources = TutorialResource.objects.filter(
                    tutorial_detail__foss_id=foss_id,
                    language_id=language_id,
                    is_on_youtube=False
                ).select_related('tutorial_detail').order_by('tutorial_detail__order')
                
                for tr in tutorial_resources:
                    tutorials.append({
                        'id': tr.id,
                        'name': tr.tutorial_detail.tutorial,
                        'outline': tr.outline
                    })
            except (ValueError, Language.DoesNotExist, FossCategory.DoesNotExist):
                pass
    
    return HttpResponse(json.dumps({'tutorials': tutorials}), content_type='application/json')
