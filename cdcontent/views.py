# Standard Library
import json
import os
import tempfile
import zipfile

# Third Party Stuff
from django.conf import settings
from django.core.context_processors import csrf
from django.core.servers.basehttp import FileWrapper
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Spoken Tutorial Stuff
from cdcontent.forms import *
from creation.models import *


def zipdir(src_path, dst_path, archive):
    for root, dirs, dir_files in os.walk(src_path):
        for dir_file in dir_files:
            archive.write(os.path.join(root, dir_file), os.path.join(dst_path, dir_file))


def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.
        i += 1
    f = ('%.1f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def get_sheet_path(foss, lang, sheet):
    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-' + \
        sheet.title() + '-Sheet-' + lang.name + '.pdf'
    if lang.name != 'English':
        if os.path.isfile(file_path):
            new_file_path = 'spoken/videos/' + \
                str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-' + sheet.title() + '-Sheet-' + lang.name + '.pdf'
            return file_path, new_file_path

    file_path = settings.MEDIA_ROOT + 'videos/' + \
        str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-' + sheet.title() + '-Sheet-English.pdf'
    if os.path.isfile(file_path):
        new_file_path = 'spoken/videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + \
                        '-' + sheet.title() + '-Sheet-English.pdf'
        return file_path, new_file_path
    return False, False


def get_all_foss_details(selectedfoss):
    all_foss_details = {}
    languages = set()
    for key, values in selectedfoss.iteritems():
        foss_rec = FossCategory.objects.get(pk=key)
        try:
            all_foss_details[foss_rec.id]
        except:
            all_foss_details[foss_rec.id] = {}
        all_foss_details[foss_rec.id]['foss'] = foss_rec.foss
        try:
            all_foss_details[foss_rec.id]['langs']
        except:
            all_foss_details[foss_rec.id]['langs'] = {}
        for value in values[0]:
            language = Language.objects.get(pk=value)
            all_foss_details[foss_rec.id]['langs'][language.id] = language.name
            languages.add(language.name)
    return all_foss_details, languages


def home(request):
    if request.method == 'POST':
        form = CDContentForm(request.POST)
        if form.is_valid():
            temp = tempfile.TemporaryFile()
            archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
            selectedfoss = json.loads(request.POST.get('selected_foss', {}))
            all_foss_details, languages = get_all_foss_details(selectedfoss)
            eng_rec = Language.objects.get(name="English")
            for key, values in selectedfoss.iteritems():
                foss_rec = FossCategory.objects.get(pk=key)
                level = int(values[1])
                eng_flag = True
                if str(eng_rec.id) in values[0]:
                    eng_flag = False
                for value in values[0]:
                    language = Language.objects.get(pk=value)
                    src_path, dst_path = get_sheet_path(foss_rec, language, 'instruction')
                    if dst_path:
                        archive.write(src_path, dst_path)
                    src_path, dst_path = get_sheet_path(foss_rec, language, 'installation')
                    if dst_path:
                        archive.write(src_path, dst_path)
                    t_resource_qs = TutorialResource.objects.filter(Q(status=1) | Q(status=2),
                                                                    tutorial_detail__foss_id=key)
                    if level:
                        tr_recs = t_resource_qs.filter(tutorial_detail__level_id=level, language_id=value).order_by(
                            'tutorial_detail__level', 'tutorial_detail__order', 'language__name')
                    else:
                        tr_recs = t_resource_qs.filter(language_id=value).order_by(
                            'tutorial_detail__level', 'tutorial_detail__order', 'language__name')
                    rec = None
                    for rec in tr_recs:
                        if eng_flag:
                            filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + \
                                '/' + rec.tutorial_detail.tutorial.replace(' ', '-') + "-English.srt"
                            if os.path.isfile(settings.MEDIA_ROOT + filepath):
                                archive.write(settings.MEDIA_ROOT + filepath, 'spoken/' + filepath)
                        filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + '/' + rec.video

            # Check if the side by side video for the selected language is present or
            # not, if not, fetch default language as English
                        side_by_side_language = settings.BASE_DIR + \
                            '/media/videos/32/714/Side-by-Side-Method-%s.ogv' % (language.name)
                        if os.path.exists(side_by_side_language):
                            archive.write(settings.BASE_DIR + '/media/videos/32/714/Side-by-Side-Method-%s.ogv' %
                                          (language.name), 'spoken/Side_by_Side-Method-%s.ogv' % (language.name))
                        else:
                            archive.write(settings.BASE_DIR + '/media/side-by-side-method.ogv',
                                          'spoken/side-by-side-method.ogv')

                        if os.path.isfile(settings.MEDIA_ROOT + filepath):
                            archive.write(settings.MEDIA_ROOT + filepath, 'spoken/' + filepath)
                        ptr = filepath.rfind(".")
                        filepath = filepath[:ptr] + '.srt'
                        if os.path.isfile(settings.MEDIA_ROOT + filepath):
                            archive.write(settings.MEDIA_ROOT + filepath, 'spoken/' + filepath)
                        if rec.common_content.slide_status > 0:
                            filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + \
                                '/resources/' + rec.common_content.slide
                            if os.path.isfile(settings.MEDIA_ROOT + filepath):
                                archive.write(settings.MEDIA_ROOT + filepath, 'spoken/' + filepath)
                        if rec.common_content.assignment_status > 0 and rec.common_content.assignment_status != 6:
                            filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + \
                                '/resources/' + rec.common_content.assignment
                            if os.path.isfile(settings.MEDIA_ROOT + filepath):
                                archive.write(settings.MEDIA_ROOT + filepath, 'spoken/' + filepath)
                        if rec.common_content.code_status > 0 and rec.common_content.code_status != 6:
                            filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + \
                                '/resources/' + rec.common_content.code
                            if os.path.isfile(settings.MEDIA_ROOT + filepath):
                                archive.write(settings.MEDIA_ROOT + filepath, 'spoken/' + filepath)
                        tutorial_path = str(rec.tutorial_detail.foss_id) + '/' + str(rec.tutorial_detail_id) + '/'
                        ctx = {
                            'tr_rec': rec,
                            'tr_recs': tr_recs,
                            'media_path': settings.MEDIA_ROOT,
                            'tutorial_path': tutorial_path,
                        }
                        watch_page = str(render(request, "cdcontent/templates/watch_tutorial.html", ctx))
                        watch_page = watch_page.replace('Content-Type: text/html; charset=utf-8', '')
                        watch_page = watch_page.strip("\n")
                        archive.writestr('spoken/videos/' + tutorial_path + 'show-video-' +
                                         rec.language.name + '.html', watch_page)
                    list_page = str(render(request, "cdcontent/templates/tutorial_search.html",
                                           {'collection': tr_recs,
                                            'foss_details': all_foss_details,
                                            'foss': foss_rec.id,
                                            'lang': language.id}))
                    list_page = list_page.replace('Content-Type: text/html; charset=utf-8', '')
                    list_page = list_page.strip("\n")
                    archive.writestr('spoken/videos/' + str(foss_rec.id) +
                                     '/list-videos-' + language.name + '.html', list_page)
            home_page = str(render(request, "cdcontent/templates/home.html",
                                   {'foss_details': all_foss_details,
                                    'foss': foss_rec.id,
                                    'lang': language.id,
                                    'languages': languages}))
            home_page = home_page.replace('Content-Type: text/html; charset=utf-8', '')
            home_page = home_page.strip("\n")
            archive.writestr('spoken/videos/home.html', home_page)
            archive.write(settings.BASE_DIR + '/static/spoken/css/bootstrap.min.css',
                          'spoken/includes/css/bootstrap.min.css')
            archive.write(settings.BASE_DIR + '/static/spoken/css/font-awesome.min.css',
                          'spoken/includes/css/font-awesome.min.css')
            archive.write(settings.BASE_DIR + '/static/spoken/css/main.css', 'spoken/includes/css/main.css')
            archive.write(settings.BASE_DIR + '/static/spoken/css/video-js.min.css',
                          'spoken/includes/css/video-js.min.css')
            archive.write(settings.BASE_DIR + '/static/spoken/images/favicon.ico', 'spoken/includes/images/favicon.ico')
            archive.write(settings.BASE_DIR + '/static/spoken/images/logo.png', 'spoken/includes/images/logo.png')
            archive.write(settings.BASE_DIR + '/static/spoken/js/jquery-1.11.0.min.js',
                          'spoken/includes/js/jquery-1.11.0.min.js')
            archive.write(settings.BASE_DIR + '/static/spoken/js/bootstrap.min.js',
                          'spoken/includes/js/bootstrap.min.js')
            archive.write(settings.BASE_DIR + '/static/spoken/js/video.js', 'spoken/includes/js/video.js')
            archive.write(settings.BASE_DIR + '/static/spoken/images/thumb-even.png',
                          'spoken/includes/images/thumb-even.png')
            archive.write(settings.BASE_DIR + '/static/spoken/images/Basic.png', 'spoken/includes/images/Basic.png')
            archive.write(settings.BASE_DIR + '/static/spoken/images/Intermediate.png',
                          'spoken/includes/images/Intermediate.png')
            archive.write(settings.BASE_DIR + '/static/spoken/images/Advanced.png',
                          'spoken/includes/images/Advanced.png')
            # archive.write(settings.BASE_DIR + '/media/side-by-side-method.ogv', 'spoken/side-by-side-method.ogv')
            zipdir(settings.BASE_DIR + '/static/spoken/fonts', 'spoken/includes/fonts/', archive)
            archive.write(settings.BASE_DIR + '/static/cdcontent/templates/readme.txt', 'spoken/README.txt')
            archive.write(settings.BASE_DIR + '/static/cdcontent/templates/index.html', 'spoken/index.html')
            archive.close()
            temp.seek(0)
            wrapper = FileWrapper(temp)
            response = HttpResponse(wrapper, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=spoken-tutorial-cdcontent.zip'
            response['Content-Length'] = temp.tell()
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
        t_resource_qs = TutorialResource.objects.filter(Q(status=1) | Q(status=2), tutorial_detail__foss_id=fossid)
        if levelid:
            lang_recs = t_resource_qs.filter(tutorial_detail__level_id=levelid).values_list(
                'language_id', 'language__name').order_by('language__name').distinct()
        else:
            lang_recs = t_resource_qs.values_list('language_id', 'language__name').order_by('language__name').distinct()
        for row in lang_recs:
            data = data + '<option value="' + str(row[0]) + '">' + row[1] + '</option>'

    return HttpResponse(json.dumps(data), content_type='application/json')


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

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def ajax_show_added_foss(request):
    try:
        tmp = json.loads(request.POST.get('selectedfoss', {}))
    except:
        tmp = {}
    data = ''
    fsize_total = 0.0
    for key, values in tmp.iteritems():
        foss, level = FossCategory.objects.get(pk=key), int(values[1])
        langs = ', '.join(list(Language.objects.filter(id__in=list(
            values[0])).order_by('name').values_list('name', flat=True)))
        if level:
            tr_recs = TutorialResource.objects.filter(Q(status=1) | Q(
                status=2), tutorial_detail__foss=foss, tutorial_detail__level_id=level, language_id__in=list(values[0]))
        else:
            tr_recs = TutorialResource.objects.filter(Q(status=1) | Q(
                status=2), tutorial_detail__foss=foss, language_id__in=list(values[0]))
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
                    filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + \
                        '/resources/' + rec.common_content.slide
                    if os.path.isfile(settings.MEDIA_ROOT + filepath):
                        fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
                if rec.common_content.assignment_status > 0 and rec.common_content.assignment_status != 6:
                    filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + \
                        '/resources/' + rec.common_content.assignment
                    if os.path.isfile(settings.MEDIA_ROOT + filepath):
                        fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
                if rec.common_content.code_status > 0 and rec.common_content.code_status != 6:
                    filepath = 'videos/' + str(key) + '/' + str(rec.tutorial_detail_id) + \
                        '/resources/' + rec.common_content.code
                    if os.path.isfile(settings.MEDIA_ROOT + filepath):
                        fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)
            except Exception:
                continue
        fsize_total += fsize
        data += '<tr><td>' + foss.foss + '</td><td>' + langs + '</td><td>' + humansize(fsize) + '</td></tr>'

    output = {0: data, 1: humansize(fsize_total)}
    return HttpResponse(json.dumps(output), content_type='application/json')
