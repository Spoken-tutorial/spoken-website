from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.shortcuts import render
from django.db.models import Q
from creation.models import *
from cdcontent.forms import *
import json

# Create your views here.
def home(request):
    if request.method == 'POST':
        form = CDContentForm(request.POST)
        if form.is_valid():
            print form.cleaned_data.get('language')
            form = CDContentForm()
    else:
        form = CDContentForm()
    context = {
        'form': form
    }

    return render(request, "cdcontent/templates/cdcontent_home.html", context)
@csrf_exempt
def ajax_fill_languages(request):
    data = ''
    fossid = request.POST.get('foss', '')
    if fossid:
        lang_recs = TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss_id = fossid).values_list('language_id', 'language__name').order_by('language__name').distinct()
        for row in lang_recs:
            data = data + '<option value="' + str(row[0]) + '">' + row[1] + '</option>'

    return HttpResponse(json.dumps(data), mimetype='application/json')
