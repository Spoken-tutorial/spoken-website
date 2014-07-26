from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.servers.basehttp import FileWrapper
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.shortcuts import render
from django.conf import settings
from django.db.models import Q
from creation.models import *
from cdcontent.forms import *
import os, tempfile, zipfile
import json

# Create your views here.
def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.1f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

def home(request):
    if request.method == 'POST':
        form = CDContentForm(request.POST)
        if form.is_valid():
            temp = tempfile.TemporaryFile()
            archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
            selectedfoss = json.loads(request.POST.get('selected_foss', {}))
            for key, values in selectedfoss.iteritems():
                foss_rec = FossCategory.objects.get(pk = key)
                print values
                level = int(values[1])
                if level:
                    tr_recs = TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss_id = key, tutorial_detail__level_id = level, language_id__in = list(values[0])).order_by('tutorial_detail__level', 'tutorial_detail__order', 'language__name')
                else:
                    tr_recs = TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss_id = key, language_id__in = list(values[0])).order_by('tutorial_detail__level', 'tutorial_detail__order', 'language__name')
                for rec in tr_recs:
                    filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + '/' + rec.video
                    if os.path.isfile(settings.MEDIA_ROOT + filepath):
                        archive.write(settings.MEDIA_ROOT + filepath, filepath)
                    ptr = filepath.rfind(".")
                    filepath = filepath[:ptr] + '.srt'
                    if os.path.isfile(settings.MEDIA_ROOT + filepath):
                        archive.write(settings.MEDIA_ROOT + filepath, filepath)
                    if rec.common_content.slide_status > 0:
                        filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + '/resources/' + rec.common_content.slide
                        if os.path.isfile(settings.MEDIA_ROOT + filepath):
                            archive.write(settings.MEDIA_ROOT + filepath, filepath)
                    if rec.common_content.assignment_status > 0 and rec.common_content.assignment_status != 6:
                        filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + '/resources/' + rec.common_content.assignment
                        if os.path.isfile(settings.MEDIA_ROOT + filepath):
                            archive.write(settings.MEDIA_ROOT + filepath, filepath)
                    if rec.common_content.code_status > 0 and rec.common_content.code_status != 6:
                        filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + '/resources/' + rec.common_content.code
                        if os.path.isfile(settings.MEDIA_ROOT + filepath):
                            archive.write(settings.MEDIA_ROOT + filepath, filepath)
            list_page = render(request, "cdcontent/templates/tutorial_search.html", {})
            archive.close()
            wrapper = FileWrapper(temp)
            response = HttpResponse(wrapper, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=spoken-tutorial-cdcontent.zip'
            response['Content-Length'] = temp.tell()
            temp.seek(0)
            return response
    else:
        form = CDContentForm()
    context = {
        'form': form
    }
    context.update(csrf(request))

    return render(request, "cdcontent/templates/cdcontent_home.html", context)

@csrf_exempt
def ajax_fill_languages(request):
    data = ''
    fossid = request.POST.get('foss', '')
    levelid = int(request.POST.get('level', 0))
    if fossid:
        if levelid:
            lang_recs = TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss_id = fossid, tutorial_detail__level_id = levelid).values_list('language_id', 'language__name').order_by('language__name').distinct()
        else:
            lang_recs = TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss_id = fossid).values_list('language_id', 'language__name').order_by('language__name').distinct()
        for row in lang_recs:
            data = data + '<option value="' + str(row[0]) + '">' + row[1] + '</option>'

    return HttpResponse(json.dumps(data), mimetype='application/json')

@csrf_exempt
def ajax_add_foss(request):
    foss = request.POST.get('foss', '')
    level = int(request.POST.get('level', 0))
    selectedfoss = {}
    try:
        langs = json.loads(request.POST.get('langs', []))
    except:
        langs = []
    try:
        selectedfoss = json.loads(request.POST.get('selectedfoss', ''))
    except:
        pass
    if foss and langs:
        selectedfoss[foss] = [langs, level]
    data = json.dumps(selectedfoss)

    return HttpResponse(json.dumps(data), mimetype='application/json')

@csrf_exempt
def ajax_show_added_foss(request):
    try:
        tmp = json.loads(request.POST.get('selectedfoss', {}))
    except:
        tmp = {}
    data = ''
    fsize_total = 0.0
    print '--------------'
    for key, values in tmp.iteritems():
        foss = FossCategory.objects.get(pk = key)
        level = int(values[1])
        print foss, level
        langs = ', '.join(list(Language.objects.filter(id__in = list(values[0])).order_by('name').values_list('name', flat=True)))
        if level:
            tr_recs = TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss = foss, tutorial_detail__level_id = level, language_id__in = list(values[0]))
        else:
            tr_recs = TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss = foss, language_id__in = list(values[0]))
        fsize = 0.0
        for rec in tr_recs:
            try:
                filepath = 'videos/' + str(foss.id) + '/' + str(rec.tutorial_detail_id) + '/' + rec.video
                if os.path.isfile(settings.MEDIA_ROOT + filepath):
                    fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
                ptr = filepath.rfind(".")
                filepath = filepath[:ptr] + '.srt'
                if os.path.isfile(settings.MEDIA_ROOT + filepath):
                    fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
                if rec.common_content.slide_status > 0:
                    filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + '/resources/' + rec.common_content.slide
                    if os.path.isfile(settings.MEDIA_ROOT + filepath):
                        fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
                if rec.common_content.assignment_status > 0 and rec.common_content.assignment_status != 6:
                    filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + '/resources/' + rec.common_content.assignment
                    if os.path.isfile(settings.MEDIA_ROOT + filepath):
                        fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
                if rec.common_content.code_status > 0 and rec.common_content.code_status != 6:
                    filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + '/resources/' + rec.common_content.code
                    if os.path.isfile(settings.MEDIA_ROOT + filepath):
                        fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
            except Exception, e:
                print e
                continue
        fsize_total += fsize
        data += '<tr><td>' + foss.foss + '</td><td>' + langs + '</td><td>' + humansize(fsize) + '</td></tr>'
    if data:
        data += '<tr><td colspan="2" class="col-right">~ Total Size</td><td>' + humansize(fsize_total) + '</td></tr>'
    return HttpResponse(json.dumps(data), mimetype='application/json')
