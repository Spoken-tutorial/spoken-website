
# Standard Library
from builtins import str
import json
import os
import zipfile
from datetime import datetime,date

# Third Party Stuff
from django.conf import settings
 
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.template.context_processors import csrf

# Spoken Tutorial Stuff
from cdcontent.forms import *
from creation.models import *
from forums.models import Answer, Question
from events.models import AcademicCenter, State, AcademicKey
from donate.forms import PayeeForm
from donate.models import Payee

# Create your views here.
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


def add_sheets(archive, foss, lang):
    instruction_file = 'videos/{}/{}-Instruction-Sheet-{}.pdf'.format(foss.id,
                                                                      foss.foss.replace(' ', '-'),
                                                                      lang.name)

    installation_file = 'videos/{}/{}-Installation-Sheet-{}.pdf'.format(foss.id,
                                                                        foss.foss.replace(' ', '-'),
                                                                        lang.name)
    instruction_file_path = '{}{}'.format(settings.MEDIA_ROOT, instruction_file)
    installation_file_path = '{}{}'.format(settings.MEDIA_ROOT, installation_file)

    if os.path.isfile(instruction_file_path):
        new_file_path = 'spoken/{}'.format(instruction_file)
        archive.write(instruction_file_path, new_file_path)

    if os.path.isfile(installation_file_path):
        new_file_path = 'spoken/{}'.format(installation_file)
        archive.write(installation_file_path, new_file_path)


def get_all_foss_details(selectedfoss):
    all_foss_details = {}

    for key, values in list(selectedfoss.items()):
        foss_rec = FossCategory.objects.get(pk=key)

        if not all_foss_details.get(foss_rec.id, None):
            all_foss_details[foss_rec.id] = {}

        all_foss_details[foss_rec.id]['foss'] = foss_rec.foss

        if not all_foss_details[foss_rec.id].get('langs', None):
            all_foss_details[foss_rec.id]['langs'] = {}

        for value in values[0]:
            language = Language.objects.get(pk=value)
            all_foss_details[foss_rec.id]['langs'][language.id] = language.name
    return all_foss_details


def add_side_by_side_tutorials(archive, languages):
    languages.add('English')
    available_langs = set()

    for language in languages:
        filepath = '{}videos/32/714/Side-by-Side-Method-{}.webm'.format(settings.MEDIA_ROOT, language)

        if os.path.isfile(filepath):
            available_langs.add(language)
            archive.write(filepath, 'spoken/videos/Side-by-Side-Method-{}.webm'.format(language))

    return available_langs

def add_forum_video(archive):
    filepath = '{}videos/32/1450/Spoken-Tutorial-Forums-English.webm'.format(settings.MEDIA_ROOT)
    if os.path.isfile(filepath):
        archive.write(filepath, 'spoken/videos/Spoken-Tutorial-Forums-English.webm')

def add_suplementary_video(archive):
    filepath = '{}videos/32/1537/Spoken-Tutorial-Supplementary-Material-English.webm'.format(settings.MEDIA_ROOT)
    if os.path.isfile(filepath):
        archive.write(filepath, 'spoken/videos/Spoken-Tutorial-Supplementary-Material-English.webm')


def get_static_files():
    return {
        '/static/spoken/css/bootstrap.min.css': 'spoken/includes/css/bootstrap.min.css',
        '/static/spoken/css/font-awesome.min.css': 'spoken/includes/css/font-awesome.min.css',
        '/static/spoken/css/main.css': 'spoken/includes/css/main.css',
        '/static/spoken/css/video-js.min.css': 'spoken/includes/css/video-js.min.css',
        '/static/spoken/images/favicon.ico': 'spoken/includes/images/favicon.ico',
        '/static/spoken/images/logo.png': 'spoken/includes/images/logo.png',
        '/static/spoken/js/jquery-1.11.0.min.js': 'spoken/includes/js/jquery-1.11.0.min.js',
        '/static/spoken/js/bootstrap.min.js': 'spoken/includes/js/bootstrap.min.js',
        '/static/spoken/js/video.js': 'spoken/includes/js/video.js',
        '/static/spoken/images/thumb-even.png': 'spoken/includes/images/thumb-even.png',
        '/static/spoken/images/Basic.png': 'spoken/includes/images/Basic.png',
        '/static/spoken/images/Intermediate.png': 'spoken/includes/images/Intermediate.png',
        '/static/spoken/images/Advanced.png': 'spoken/includes/images/Advanced.png',
        '/static/cdcontent/templates/readme.txt': 'spoken/README.txt',
        '/static/cdcontent/templates/index.html': 'spoken/index.html',
        '/static/forum_website/css/bootstrap.min.css': 'spoken/includes/css/bootstrap_forum.min.css',
        '/static/forum_website/css/main.css': 'spoken/includes/css/main_forum.css',
        '/static/forum_website/css/nice-bar.css': 'spoken/includes/css/nice-bar.css',
        '/static/forum_website/css/theme.blue.css': 'spoken/includes/css/theme.blue.css',
        '/static/forum_website/slick/slick.css': 'spoken/includes/css/slick.css',
        '/static/forum_website/images/cc-logo-88x31.png': 'spoken/includes/images/cc-logo-88x31.png'

    }


def calculate_directory_size(dir_path):
    folder_size = 0.0

    try:
        if os.path.isdir(dir_path):
            for (path, dirs, files) in os.walk(dir_path):
                for file_name in files:
                    filename = os.path.join(path, file_name)
                    folder_size += os.path.getsize(filename)
    except Exception as e:
        folder_size = 0.0
        print(e)

    return folder_size


def calculate_static_file_size():
    fsize = 0.0

    try:
        static_files = get_static_files()
        dir_path = '{}/static/spoken/fonts'.format(settings.BASE_DIR)

        for key, value in list(static_files.items()):
            filepath = '{}{}'.format(settings.BASE_DIR, key)

            if os.path.isfile(filepath):
                fsize += os.path.getsize(filepath)

        fsize += calculate_directory_size(dir_path)
    except Exception as e:
        fsize = 0.0
        print(e)

    return fsize


def add_static_files(archive):
    zipdir(settings.BASE_DIR + '/static/spoken/fonts', 'spoken/includes/fonts/', archive)
    static_files = get_static_files()

    for key, value in list(static_files.items()):
        filepath = '{}{}'.format(settings.BASE_DIR, key)

        if os.path.isfile(filepath):
            archive.write(filepath, value)


def convert_template_to_html_file(archive, filename, request, template, ctx):
    html = render(request, template, ctx).content
    html_string = html.decode('utf-8')
    html_string = html_string.replace('Content-Type: text/html; charset=utf-8', '').strip("\n")
    archive.writestr(filename, html_string)


def collect_common_files(tr_rec, common_files):
    common_files_path = 'videos/{}/{}/resources'.format(tr_rec.tutorial_detail.foss_id, tr_rec.tutorial_detail_id)

    # if tr_rec.common_content.slide_status > 0:
    #     common_files.add('{}/{}'.format(common_files_path, tr_rec.common_content.slide))

    if tr_rec.common_content.assignment_status > 0 and tr_rec.common_content.assignment_status != 6:
        common_files.add('{}/{}'.format(common_files_path, tr_rec.common_content.assignment))

    if tr_rec.common_content.code_status > 0 and tr_rec.common_content.code_status != 6:
        common_files.add('{}/{}'.format(common_files_path, tr_rec.common_content.code))

    if tr_rec.common_content.additional_material_status > 0 and tr_rec.common_content.additional_material_status != 6:
        common_files.add('{}/{}'.format(common_files_path, tr_rec.common_content.additional_material))



def add_common_files(archive, common_files):
    for filepath in common_files:
        if os.path.isfile(settings.MEDIA_ROOT + filepath):
            archive.write(settings.MEDIA_ROOT + filepath, 'spoken/' + filepath)


def add_srt_file(archive, tr_rec, filepath, eng_flag, srt_files):
    ptr = filepath.rfind(".")
    filepath = filepath[:ptr] + '.srt'

    if os.path.isfile(settings.MEDIA_ROOT + filepath):
        archive.write(settings.MEDIA_ROOT + filepath, 'spoken/' + filepath)

    if eng_flag:
        filepath = 'videos/{}/{}/{}-English.srt'.format(tr_rec.tutorial_detail.foss_id, tr_rec.tutorial_detail_id,
                                                        tr_rec.tutorial_detail.tutorial.replace(' ', '-'))

        if os.path.isfile(settings.MEDIA_ROOT + filepath) and filepath not in srt_files:
            srt_files.add(filepath)
            archive.write(settings.MEDIA_ROOT + filepath, 'spoken/' + filepath)


def internal_computation(request, user_type):
    zipfile_name = '{}.zip'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))
    file_obj = open('{}cdimage/{}'.format(settings.MEDIA_ROOT, zipfile_name), 'wb')
    archive = zipfile.ZipFile(file_obj, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
    try:
        selectedfoss = json.loads(request.POST.get('selected_foss', {}))
    except:
        selectedfoss = request.POST.get('selected_foss', {})
    all_foss_details = get_all_foss_details(selectedfoss)
    eng_rec = Language.objects.get(name="English")
    languages = set()

    for key, values in list(selectedfoss.items()):
        foss_rec = FossCategory.objects.get(pk=key)
        level = int(values[1])
        eng_flag = True
        srt_files = set()
        common_files = set()

        if str(eng_rec.id) in values[0]:
            eng_flag = False

        t_resource_qs = TutorialResource.objects.filter(Q(status=1) | Q(status=2),
                                                        tutorial_detail__foss_id=key)

        if level:
            t_resource_qs = t_resource_qs.filter(tutorial_detail__level_id=level)
        for value in values[0]:
            language = Language.objects.get(pk=value)
            add_sheets(archive, foss_rec, language)

            tr_recs = t_resource_qs.filter(language_id=value).order_by(
                'tutorial_detail__level', 'tutorial_detail__order', 'language__name')

            languages.add(language.name)

            for rec in tr_recs:
                filepath = 'videos/{}/{}/{}'.format(key, rec.tutorial_detail_id, rec.video)
                 # get list of questions of a particular tutorial
                # Temporarily disable questions
                # question_s = Question.objects.filter(category=foss_rec.foss.replace(' ','-'),tutorial=rec.tutorial_detail.tutorial.replace(' ','-')).order_by('-date_created')
                question_s = Question.objects.none()

                if os.path.isfile(settings.MEDIA_ROOT + filepath):
                    archive.write(settings.MEDIA_ROOT + filepath, 'spoken/' + filepath)

                # add srt file to archive
                add_srt_file(archive, rec, filepath, eng_flag, srt_files)

                # collect common files
                collect_common_files(rec, common_files)

                tutorial_path = '{}/{}/'.format(rec.tutorial_detail.foss_id, rec.tutorial_detail_id)
                filepath = 'spoken/videos/{}show-video-{}.html'.format(tutorial_path, rec.language.name)
                ctx = {'tr_rec': rec, 'tr_recs': tr_recs,
                       'media_path': settings.MEDIA_ROOT, 'tutorial_path': tutorial_path,'question_s': question_s}
                convert_template_to_html_file(archive, filepath, request,
                                              "cdcontent/templates/watch_tutorial.html", ctx)
                # for each question find the answers
                for question in question_s:
                    answer=Answer.objects.filter(question=question)
                    ctx = {'question': question, 'answer': answer}
                    filepath = 'spoken/videos/' + str(foss_rec.id) + '/' + str(rec.tutorial_detail_id) + '/answer-to-question-' + str(question.id) + '.html'
                    convert_template_to_html_file(archive, filepath, request, "cdcontent/templates/answer_to_question.html", ctx)




            filepath = 'spoken/videos/' + str(foss_rec.id) + '/list-videos-' + language.name + '.html'
            ctx = {'collection': tr_recs, 'foss_details': all_foss_details,
                   'foss': foss_rec.id, 'lang': language.id}
            convert_template_to_html_file(archive, filepath, request,
                                          "cdcontent/templates/tutorial_search.html", ctx)

        # add common files for current foss
        add_common_files(archive, common_files)

    # add side-by-side tutorials for selected languages
    languages = add_side_by_side_tutorials(archive, languages)
    add_forum_video(archive)
    add_suplementary_video(archive)

    ctx = {'foss_details': all_foss_details, 'foss':'' ,
           'lang': '', 'languages': languages}
    convert_template_to_html_file(archive, 'spoken/videos/home.html', request,
                                  "cdcontent/templates/home.html", ctx)

    # add all required static files to archive
    add_static_files(archive)
    archive.close()

    file_obj.close()
    file_path= os.path.dirname(os.path.realpath(__file__))+'/../media/cdimage/{}'.format(zipfile_name)
    response = HttpResponse(open(file_path, 'rb'), content_type='application/zip')
    if user_type == 'paid':
        return zipfile_name
    elif user_type == 'general':
        return response

@csrf_exempt
def home(request):
    if request.method == 'POST':
        form = CDContentForm(request.POST)

        if form.is_valid():
            try:
                zipfile_name = internal_computation(request, 'paid')
                # wrapper = FileWrapper(temp)
                # response = HttpResponse(wrapper, content_type='application/zip')
                # response['Content-Disposition'] = 'attachment; filename=spoken-tutorial-cdcontent.zip'
                # response['Content-Length'] = temp.tell()
                # return response
                context = {'path': '/media/cdimage/{}'.format(zipfile_name), 'status': True}
            except Exception as e:
                print(e)
                context = {'path': '', 'status': False}
        return HttpResponse(json.dumps(context), content_type='application/json')
    else:
        form = CDContentForm()
    states = State.objects.order_by('name')

    context = {
        'form': form,
        'states': states,
        'payment_form': PayeeForm(user=request.user),
    }
    if request.user.is_authenticated():
        payee_list = Payee.objects.prefetch_related(
            'cdfosslanguages_set__foss','cdfosslanguages_set__lang',
            'payment_transaction').filter(user=request.user)
        context['payee_list'] = payee_list
    context.update(csrf(request))
    context['organizer_paid'] = is_organizer_paid(request)
    return render(request, "cdcontent/templates/cdcontent_home.html", context)

@csrf_exempt
def ajax_fill_languages(request):
    data = ''
    fossid = request.POST.get('foss', '')
    levelid = int(request.POST.get('level', 0))
    if fossid:
        if levelid:
            lang_recs = TutorialResource.objects.filter(
                Q(status=1) | Q(status=2), tutorial_detail__foss_id=fossid,
                tutorial_detail__level_id=levelid).values_list(
                    'language_id', 'language__name').order_by('language__name').distinct()
        else:
            lang_recs = TutorialResource.objects.filter(
                Q(status=1) | Q(status=2), tutorial_detail__foss_id=fossid).values_list(
                    'language_id', 'language__name').order_by('language__name').distinct()
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
    languages = set()
    eng_rec = Language.objects.get(name="English")

    for key, values in list(tmp.items()):
        langs_list = list(values[0])
        
        

        foss, level = FossCategory.objects.get(pk=key), int(values[1])
        
        langs = ', '.join(list(
            Language.objects.filter(id__in=list(values[0])).order_by('name').values_list('name', flat=True)))
        
        if level:
            tr_recs = TutorialResource.objects.filter(Q(status=1) | Q(
                status=2), tutorial_detail__foss=foss, tutorial_detail__level_id=level, language_id__in=langs_list)
            level_txt = Level.objects.get(pk=level)
        else:
            tr_recs = TutorialResource.objects.filter(Q(status=1) | Q(
                status=2), tutorial_detail__foss=foss, language_id__in=langs_list)
            level_txt = 'All'

        fsize = 0.0
        eng_flag = True
        srt_files = set()
        common_files = set()

        if str(eng_rec.id) in langs_list:
            eng_flag = False

        for rec in tr_recs:
            try:
                languages.add(rec.language.name)

                # calculate video size
                filepath = 'videos/{}/{}/{}'.format(foss.id, rec.tutorial_detail_id, rec.video)

                if os.path.isfile(settings.MEDIA_ROOT + filepath):
                    fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)

                # calculate str file size
                ptr = filepath.rfind(".")
                filepath = filepath[:ptr] + '.srt'
                if os.path.isfile(settings.MEDIA_ROOT + filepath):
                    fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)

                if eng_flag:
                    filepath = 'videos/{}/{}/{}-English.srt'.format(
                        key, rec.tutorial_detail_id, rec.tutorial_detail.tutorial.replace(' ', '-'))

                    if os.path.isfile(settings.MEDIA_ROOT + filepath) and filepath not in srt_files:
                        fsize += os.path.getsize(settings.MEDIA_ROOT + filepath)

                # append common files path to list
                common_files_path = '{}videos/{}/{}/resources'.format(settings.MEDIA_ROOT, key,
                                                                      rec.tutorial_detail_id)

                # if rec.common_content.slide_status > 0:
                #     common_files.add('{}/{}'.format(common_files_path, rec.common_content.slide))

                if rec.common_content.assignment_status > 0 and rec.common_content.assignment_status != 6:
                    common_files.add('{}/{}'.format(common_files_path, rec.common_content.assignment))

                if rec.common_content.code_status > 0 and rec.common_content.code_status != 6:
                    common_files.add('{}/{}'.format(common_files_path, rec.common_content.code))

                if rec.common_content.additional_material_status > 0 and rec.common_content.additional_material_status != 6:
                    common_files.add('{}/{}'.format(common_files_path, rec.common_content.additional_material))
            except Exception:
                continue

        # calculate common files size
        for filepath in common_files:
            if os.path.isfile(filepath):
                fsize += os.path.getsize(filepath)
        fsize_total += fsize
        
        
        data += '<tr><td name="foss[]">{}</td><td name="level[]">{}</td><td name="langs[]">{}</td><td name="size">{}</td><td id="{}"></td></tr>'.format(foss.foss,level_txt, langs, humansize(fsize),foss.id)

    fsize = 0.0
    languages.add(eng_rec.name)

    # calculate size for side-by-side tutorials
    for language in languages:
        filepath = '{}videos/32/714/Side-by-Side-Method-{}.webm'.format(settings.MEDIA_ROOT, language)

        if os.path.isfile(filepath):
            fsize += os.path.getsize(filepath)

    # calculate size for forum video
    filepath = '{}videos/32/1450/Spoken-Tutorial-Forums-English.webm'.format(settings.MEDIA_ROOT)
    if os.path.isfile(filepath):
            fsize += os.path.getsize(filepath)

    # calculate size for suplementary video
    filepath = '{}videos/32/1537/Spoken-Tutorial-Supplementary-Material-English.webm'.format(settings.MEDIA_ROOT)
    if os.path.isfile(filepath):
            fsize += os.path.getsize(filepath)
            
    # calculate static file size
    fsize += calculate_static_file_size()

    fsize_total += fsize
    data += '<tr><td colspan="3">Extra files</td><td>{}</td></tr>'.format(humansize(fsize))
    
    #check if user is registered
    user_details = check_user_details(request,fsize_total )
    output = {0: data, 1: humansize(fsize_total), 2:user_details}
    return HttpResponse(json.dumps(output), content_type='application/json')


def get_user_type(request):
    user_type = 0
    classification ={
    'unregistered' : 'UR',
    'registered_not_paid' : 'RNP',
    'registered_paid' : 'RP'
    }
    # 'UR':'UnRegistered User',
    # 'RNP':'Registered but not Paid User',
    # 'RP':'Registered and Paid User'
    if request.user.is_authenticated():
        try:
            AcademicKey.objects.get(academic_id=request.user.organiser.academic_id, expiry_date__gte=date.today())
            return classification['registered_paid']
        except AcademicKey.DoesNotExist:
            user_type = classification['registered_not_paid']
        except AcademicKey.MultipleObjectsReturned:
            return classification['registered_paid']
        except:
            user_type = classification['registered_not_paid']



        try:
            AcademicKey.objects.get(academic_id=request.user.invigilator.academic_id, expiry_date__gte=date.today())
            return classification['registered_paid']
        except AcademicKey.DoesNotExist:
            user_type = classification['registered_not_paid']
        except AcademicKey.MultipleObjectsReturned:
            return classification['registered_paid']
        except:
            user_type = classification['registered_not_paid']
        

        try:
            AcademicKey.objects.get(academic_id=request.user.student.academic_id, expiry_date__gte=date.today())
            return classification['registered_paid']
        except AcademicKey.DoesNotExist:
            user_type = classification['registered_not_paid']
        except AcademicKey.MultipleObjectsReturned:
            return classification['registered_paid']
        except:
            user_type = classification['registered_not_paid']
        return user_type
    else:
        return classification['unregistered']

def get_payable_amount(filesize):
    lt_100 = 99
    gt_100 = 250
    gst = 0.18
    if filesize < 100.0: 
        return (lt_100 + (lt_100 * gst))
    else:
        return (gt_100 + (gt_100 * gst))

def check_user_details(request, filesize):
    file_size = round(filesize/ pow(2,20),1)
    user_type = get_user_type(request)
    amount = get_payable_amount(file_size)
    if user_type == 'RP':
        return ['RP','No Limit']
    else:
        return [user_type, amount]

# return '1' if organizer belongs to paid college with valid expiry date, else '0'
def is_organizer_paid(request):
    try:
        idcase = AcademicKey.objects.filter(academic_id=request.user.organiser.academic_id, expiry_date__gte=date.today()).order_by('-expiry_date').first()
        organizer_paid = '1' if (idcase.expiry_date >= date.today()) else '0'
    except:
        organizer_paid = '0'
    return organizer_paid
