# Standard Library
from urllib import quote_plus

# Third Party Stuff
from cdeep.models import *
from django.http import HttpResponseRedirect

# Spoken Tutorial Stuff
from creation.models import *


# Create your views here.
def list_videos(request):
    foss = request.GET.get('foss', '')
    foss = foss.replace('+', 'p').replace('-', ' ')
    language = request.GET.get('language', '')
    if foss or language:
        return HttpResponseRedirect('/tutorial-search/?foss=' + quote_plus(foss) + '&language=' + language)

    return HttpResponseRedirect('/tutorial-search/')


def show_video(request):
    old_tr = request.GET.get('tr', None)
    if old_tr:
        try:
            tr = TutorialResources.objects.get(pk=old_tr)
            foss = tr.tutorial_detail.foss_category.replace('+', 'p').replace('-', ' ')
            tutorial = tr.tutorial_detail.tutorial_name.replace('+', 'p').replace('-', ' ')
            return HttpResponseRedirect('/watch/' + quote_plus(foss) + '/' + quote_plus(tutorial) + '/' +
                                        tr.language + '/')
        except Exception as e:
            print(e)
            pass
    return HttpResponseRedirect('/tutorial-search/')


def search_node(request, keyword):
    return HttpResponseRedirect('/keyword-search/?q=' + str(keyword))
