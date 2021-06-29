from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from creation.models import TutorialResource,\
            TutorialDetail, FossSuperCategory, Language,\
             FossCategory, TutorialCommonContent, TutorialDuration
from api.serializers import VideoSerializer, CategorySerializer, FossSerializer, LanguageSerializer, RelianceJioSerializer,\
        RelianceJioVideoSerializer, RelianceJioCategorySerializer, RelianceJioLanguageSerializer, TutorialDetailSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Q
import json
from django.conf import settings
from creation.views import get_video_info
import math
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from spoken.config import FOSS_API_LIST
from django.core.cache import cache
from creation.templatetags.creationdata import instruction_sheet, installation_sheet, get_prerequisite
from rest_framework import status
from forums.models import Question
from rest_framework.decorators import api_view
from creation.models import ContributorRole, DomainReviewerRole, QualityReviewerRole
@csrf_exempt
def video_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = TutorialResource.objects.filter(status=1, id=1)
        serializer = VideoSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = VideoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def get_tutorial_list(request, fossid, langid):
    """
    Retrieve, update or delete a code snippet.
    """

    try:
        tuts = TutorialResource.objects.filter(Q(status=1)|Q(status=2), language_id=langid,
                tutorial_detail_id__foss=fossid)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = VideoSerializer(tuts, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'PUT':

        data = JSONParser().parse(request)
        serializer = VideoSerializer(tut, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':

        tut.delete()
        return HttpResponse(status=204)


def show_categories(request):
    """
    List all categories.
    """
    if request.method == 'GET':
        categories = FossSuperCategory.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return JsonResponse(serializer.data, safe=False)


def get_fosslist(request):
    """
    Retrieve, fosslist based on category.
    """
    fosslist=[]
    if request.method == 'GET':
        fosses = FossCategory.objects.filter(
            status=1, show_on_homepage=1, available_for_nasscom=1).order_by('foss')
        for foss in fosses:
            fossdict={}
            tot_hour = 0
            tot_mins = 0
            tot_secs = 0
            tutorials = TutorialDuration.objects.filter(tutorial__foss=foss)
            for tutorial in tutorials:
                #print("tutorial :",tutorial.tutorial.foss,tutorial.tutorial,tutorial.duration)
                if len(tutorial.duration)>6:
                    hr,minutes,secs = tutorial.duration.split(':')                    
                    tot_hour += int(hr)
                    tot_mins += int(minutes)
                    tot_secs += int(secs)                    
                    #print('hr :',tot_hour,' mins : ',tot_mins,' secs: ',tot_secs)
            tot_mins += math.ceil(tot_secs/60)
            tot_hour = math.floor(tot_mins/60)
            timetotal = str(tot_hour) +'hr'+str(tot_mins%60)+'mins' 
            #print("\n\n\n")    
            all_keywords=""
            keywords = TutorialCommonContent.objects.filter(tutorial_detail__foss_id=foss.id)
            
            key_list = []
            for keyword in keywords:
                keys = keyword.keyword.split (",")                
                for k in keys:
                    if k not in key_list:
                        key_list.append(k)
            for category in foss.category.all():
                key_list.append(str(category))

            image_name = foss.foss.replace(' ', '-') + '.jpg'

            foss_image = "http://static.spoken-tutorial.org/images/"+image_name
            fossdict = {
            "course_id": foss.id,
            "title": foss.foss,
            "duration": timetotal,
            "metadata": foss.description,
            "price":"Free",
            "currency":"",
            "content_type":"course",
            "deeplink_url":"https://spoken-tutorial.org/tutorial-search/?search_foss="+foss.foss+"&search_language=English",
            "image_url":foss_image,
            "description":foss.description,
            "keywords":key_list
            }          
            fosslist.append(fossdict)
        
        fosslist = json.dumps(fosslist)
        return HttpResponse(fosslist, content_type='application/json')


def get_schoolfosslist(request):
    """
    List all fosses for school website.
    """
    if request.method == 'GET':
        fosses = FossCategory.objects.filter(status=1, available_for_nasscom=1)
        serializer = FossSerializer(fosses, many=True)
        return JsonResponse(serializer.data, safe=False)


def get_fosslanguage(request, fossid):
    try:
        languages = Language.objects.filter(id__in=TutorialResource.objects.filter(tutorial_detail_id__foss=fossid, status__gte=1).values('language_id'))
    except ObjectDoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = LanguageSerializer(languages, many=True)
        return JsonResponse(serializer.data, safe=False)
        get_schooltutorials


def get_tutorialdetails(request, tutid):
    tutoriallist=[]
    if request.method == 'GET':
        tut = TutorialResource.objects.get(Q(status=1)|Q(status=2), id=tutid)
        print(tut.id)
        
        tutdict={}
        thumb_name = tut.tutorial_detail.tutorial.replace(' ', '-') + '-' + 'Big.png'
        thumbnail_path = "https://spoken-tutorial.org/media/videos/"+str(tut.tutorial_detail.foss_id)+"/"+str(tut.tutorial_detail_id)+"/"+thumb_name
        print(thumbnail_path)

        videopage_path = "https://spoken-tutorial.org/watch/"+tut.tutorial_detail.foss.foss+"/"+\
        tut.tutorial_detail.tutorial+"/"+tut.language.name
        print(videopage_path)

        tutdict={
            "tutid": tut.id,
            "tut_name" :tut.tutorial_detail.tutorial,
            "outline" :tut.outline,
            "order": tut.tutorial_detail.order,
            "thumbnail_path": thumbnail_path,
            "video_url" : videopage_path
        }
        
        tutdict = json.dumps(tutdict)
        return HttpResponse(tutdict, content_type='application/json')

class RelianceJioAPI(APIView):

    #@method_decorator(cache_page(60*60))
    def get(self, request, format='json'):
        jio_data = cache.get('jio_data')
        if jio_data:
            return Response(jio_data)
        else:
            foss = FOSS_API_LIST
            lists=[]
            category_list=[]
            lang_en='English'
            languages = Language.objects.all().exclude(name=lang_en)
            for f in foss:
                f = FossCategory.objects.get(pk=f)
                tr_en = TutorialResource.objects.filter(Q(status=1) | Q(status=2),tutorial_detail__foss=f, language__name=lang_en)
                lists.append(self.get_foss_serialized(request, tr_en, lang_en))
                for l in languages:
                    tr = TutorialResource.objects.filter(Q(status=1) | Q(status=2),tutorial_detail__foss=f, language=l)
                    if tr.count() == tr_en.count():
                        lists.append(self.get_foss_serialized(request, tr, l.name))
                    else:
                        continue
                category_serializer = RelianceJioCategorySerializer(tr_en, context={'category':f.foss, 'lists': lists})
                lists = []
                category_list.append(category_serializer.data)
            serializer = RelianceJioSerializer(tr_en, context={'spokentutorials' : category_list})
            cache.set('jio_data', serializer.data)
            return Response(serializer.data)
    
    def get_foss_serialized(self, request, tr, language):
        video_serializer = RelianceJioVideoSerializer(tr, context={'request':request}, many=True)
        language_serializer = RelianceJioLanguageSerializer(tr, context={'language':language, 'videos' : video_serializer.data})
        return language_serializer.data

class TutorialResourceAPI(APIView):

    def get(self, request, format='json'):
        context = {}
        foss = request.query_params.get('search_foss', None)
        tutorial = request.query_params.get('search_tutorial', None)
        language = request.query_params.get('search_language', None)

        if foss and tutorial and language:
            try:
                tr = TutorialResource.objects.get(
                    Q(status=1) | Q(status=2),
                    tutorial_detail__foss__foss=foss, 
                    tutorial_detail__tutorial=tutorial, 
                    language__name=language
                    )
                context['foss_id'] = tr.tutorial_detail.foss.pk
                context['tutorial_id'] = tr.tutorial_detail.pk
                context['language_id'] = tr.language.pk
                instruct_sheet = instruction_sheet(tr.tutorial_detail.foss, tr.language)
                context['instruction_sheet'] = "https://spoken-tutorial.org"+str(instruct_sheet) if instruct_sheet else None
                install_sheet = installation_sheet(tr.tutorial_detail.foss, tr.language)
                context['installation_sheet'] = "https://spoken-tutorial.org/"+str(install_sheet) if install_sheet else None
                prerequisite = get_prerequisite(tr, tr.tutorial_detail)
                context['prerequisite'] = "https://spoken-tutorial.org/watch/" + str(prerequisite) if prerequisite else None
                context['code_file'] = request.build_absolute_uri(settings.MEDIA_URL + "videos/" + str(tr.tutorial_detail.foss.pk) + "/" + str(tr.tutorial_detail.pk) + "/resources/" + tr.common_content.code) if tr.common_content.code_status == 4 else None
                context['assignment'] = request.build_absolute_uri(settings.MEDIA_URL + "videos/" + str(tr.tutorial_detail.foss.pk) + "/" + str(tr.tutorial_detail.pk) + "/resources/" + tr.common_content.assignment) if tr.common_content.assignment_status ==4 else None
                context['slide'] = request.build_absolute_uri(settings.MEDIA_URL + "videos/" + str(tr.tutorial_detail.foss.pk) + "/" + str(tr.tutorial_detail.pk) + "/resources/" + tr.common_content.slide) if tr.common_content.slide_status == 4 else None
                context['script'] = "https://script.spoken-tutorial.org/index.php/" + tr.script if tr.script_status == 4 else None
                context['timed_script'] = "https://script.spoken-tutorial.org/index.php/" + tr.timed_script if tr.timed_script else None
                context['srt_file'] = request.build_absolute_uri(settings.MEDIA_URL + "videos/" + str(tr.tutorial_detail.foss.pk) + "/" + str(tr.tutorial_detail.pk) + "/" + tr.tutorial_detail.tutorial.replace(' ', '-') + "-" + tr.language.name + ".srt")
                context['additional_resource'] = request.build_absolute_uri(settings.MEDIA_URL + "videos/" + str(tr.tutorial_detail.foss.pk) + "/" + str(tr.tutorial_detail.pk) + "/resources/" + tr.common_content.additional_material) if tr.common_content.additional_material_status == 4 else None
                questions = Question.objects.filter(category=tr.tutorial_detail.foss.foss.replace(' ', '-'), tutorial=tr.tutorial_detail.tutorial.replace(' ', '-')).order_by('-date_created')
                questions_filtered = []
                for q in questions:
                    user = q.user() if q.uid != "" else None
                    title = q.title
                    minute_range = q.minute_range +"M" if q.minute_range != 'None' else None
                    second_range = q.second_range +"S" if q.second_range != 'None' else None
                    date = q.date_modified
                    questions_filtered.append({'id': q.pk,'user': user, 'question': title, 'minute_range': minute_range, 'second_range': second_range, 'date':date})
                context['questions'] = questions_filtered
                return Response(context, status=status.HTTP_200_OK)
            except TutorialResource.DoesNotExist:
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        return Response(context, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_foss_langauges(request):
    foss = FossSerializer(FossCategory.objects.all(), many=True).data
    language = LanguageSerializer(Language.objects.all(), many=True).data
    context={'spokentutorials':{'foss':foss, 'language':language}}
    return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_all_tutorials(request, fid, lid):
    tutorials = TutorialDetailSerializer(
        TutorialDetail.objects.filter(foss = fid).order_by('order'), 
        context={"lang": lid},
        many=True
        ).data
    context={'spokentutorials':{'tutorials':tutorials}}
    return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_foss_roles(request, fid, lid, username):
    roles = []
    if ContributorRole.objects.filter(foss_category__id=fid, language__id=lid, user__username=username).exists():
        roles.append('Contributor')
    if DomainReviewerRole.objects.filter(foss_category__id=fid, language__id=lid, user__username=username).exists():
        roles.append('Domain-Reviewer')
    if QualityReviewerRole.objects.filter(foss_category__id=fid, language__id=lid, user__username=username).exists():
        roles.append('Quality-Reviewer')
    context={'spokentutorials':{'roles':roles}}
    return Response(context, status=status.HTTP_200_OK)

