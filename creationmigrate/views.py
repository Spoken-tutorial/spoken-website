from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.shortcuts import render
from django.conf import settings
from shutil import copyfile
import os

from cdeep.models import *
from creation.models import *

def is_administrator(user):
    """Check if the user is having administrator rights"""
    if user.groups.filter(name='Administrator').count():
        return True
    return False

def test(request):
    print "test"
    row = TutorialResources.objects.get(pk=1)
    return HttpResponse(row.tutorial_content.tutorial_slide)

def get_old_user(uid):
    user = None
    try:
        user = Users.objects.get(pk = uid)
    except Exception, e:
        pass
    return user

def get_user(uid):
    user = None
    try:
        user = User.objects.get(pk = uid)
    except Exception, e:
        pass
    return user

def get_current_user_from_old_email(mail, user):
    try:
        row = User.objects.get(email = mail)
        return int(row.id)
    except:
        pass
    return int(user.id)

def get_last_index(input_string, td_row, concat_str):
    if input_string == 'pending' or input_string == 'notrequired':
        return ''
    if len(input_string):
        tmp_string = input_string.split('/')
        tmp_index = len(tmp_string) - 1
        file_name, file_extension = os.path.splitext(tmp_string[tmp_index])
        filename = td_row.tutorial.replace(' ', '-') + '-' + concat_str + file_extension
        return filename
    return ''

def get_current_status(input_string, input_status):
    if input_status:
        if input_string == 'notrequired' or input_status == 6:
            return 6
        elif input_string != '' and input_string != 'pending':
            if input_status <= 6:
                return input_status
            elif input_status == 7:
                return 2
            elif input_status == 8:
                return 1
            return 2
        else:
            print input_status, "******************"
    return 0

def get_current_tutorial_detail(old_td):
    levels = {
        'C2': 1,
        'C3': 2,
        'C4': 3,
    }
    try:
        new_td = TutorialDetail.objects.get(foss__foss = old_td.foss_category.replace('-', ' '), tutorial = old_td.tutorial_name.replace('-', ' '), level_id = levels[old_td.tutorial_level])
        return new_td
    except:
        pass
    return None

def get_old_tutorial_detail(tdid):
    try:
        old_td = TutorialDetails.objects.get(pk = tdid)
        return old_td
    except:
        pass
    return None

def update_prerequisite(request):
    rows = TutorialCommonContents.objects.all()
    for row in rows:
        new_td = get_current_tutorial_detail(row.tutorial_detail)
        if new_td != None:
            if row.tutorial_prerequisit != 0:
                old_td = get_old_tutorial_detail(row.tutorial_prerequisit)
                if old_td:
                    new_prereq_td = get_current_tutorial_detail(old_td)
                try:
                    new_tcc = TutorialCommonContent.objects.get(tutorial_detail = new_td)
                    if new_tcc:
                        new_tcc.prerequisite = new_prereq_td
                        if new_prereq_td:
                            new_tcc.prerequisite_status = 4
                        new_tcc.save()
                except:
                    pass

@login_required
def users(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    rows = Users.objects.all()
    for row in rows:
        name = row.name
        if len(name) > 30:
            name = row.mail
            if len(name) > 30:
                tmp_name = name.split("@")
                name = tmp_name[0]
        try:
            User.objects.get(email = row.mail)
        except:
            try:
                user = User.objects.get(username = name)
                name = name + '_' + str(user.id)
            except:
                pass
            User.objects.create(password = row.pass_field,username = name, email = row.mail, is_active = row.status)
    return HttpResponse('Success!')

@login_required
def foss_categories(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    rows = FossCategories.objects.all()
    for row in rows:
        foss_name = row.name
        foss_name = foss_name.replace("-", " ")
        try:
            foss_row = FossCategory.objects.get(foss = foss_name)
        except Exception, e:
            FossCategory.objects.create(foss = foss_name, description = row.foss_desc, status = 1, user = request.user)
    return HttpResponse('Success!')

@login_required
def languages(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    rows = TutorialLanguages.objects.all()
    for row in rows:
        try:
            lang_row = Language.objects.get(name = row.name)
        except Exception, e:
            Language.objects.create(name = row.name, user = request.user)
    return HttpResponse('Success!')

@login_required
def tutorial_details(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    levels = {
        'C2': 1,
        'C3': 2,
        'C4': 3,
    }
    rows = TutorialDetails.objects.all()
    lang_rec = Language.objects.get(name = 'English')
    for row in rows:
        foss_row = FossCategory.objects.get(foss = row.foss_category.replace("-", " "))
        try:
            td_row = TutorialDetail.objects.get(foss = foss_row, tutorial = row.tutorial_name.replace("-", " "), level_id = levels[row.tutorial_level])
        except Exception, e:
            td_row = TutorialDetail.objects.create(foss = foss_row, tutorial = row.tutorial_name.replace("-", " "), level_id = levels[row.tutorial_level], order = row.order_code, user = request.user)
        try:
            foss_dir = settings.MEDIA_ROOT + '/videos/' + str(foss_row.id) + '/' + str(td_row.id) + '/resources'
            os.makedirs(foss_dir)
        except:
            #print "Tutorial directories already exists..."
            pass
        try:
            old_tcc = TutorialCommonContents.objects.get(tutorial_detail = row)
        except Exception, e:
            print e
            continue
        try:
            new_tcc = TutorialCommonContent.objects.get(tutorial_detail = td_row)
        except:
            try:
                slide_user_id = get_current_user_from_old_email(old_tcc.tutorial_slide_uid.mail, request.user)
            except:
                slide_user_id = request.user.id
            try:
                code_user_id = get_current_user_from_old_email(old_tcc.tutorial_code_uid.mail, request.user)
            except:
                code_user_id = request.user.id
            try:
                assignment_user_id = get_current_user_from_old_email(old_tcc.tutorial_assignment_uid.mail, request.user)
            except:
                assignment_user_id = request.user.id
            try:
                prerequisite_user_id = get_current_user_from_old_email(old_tcc.tutorial_prerequisit_uid.mail, request.user)
            except:
                prerequisite_user_id = request.user.id
            if old_tcc.tutorial_keywords.strip():
                keyword_status = 4
            else:
                keyword_status = 0
            try:
                new_tcc = TutorialCommonContent.objects.create(
                    tutorial_detail_id = td_row.id,
                    slide = get_last_index(old_tcc.tutorial_slide, td_row, 'Slides'),
                    slide_user_id = slide_user_id,
                    slide_status = get_current_status(old_tcc.tutorial_slide, old_tcc.tutorial_slide_status),
                    code = get_last_index(old_tcc.tutorial_code, td_row, 'Codefiles'),
                    code_user_id = code_user_id,
                    code_status = get_current_status(old_tcc.tutorial_code, old_tcc.tutorial_code_status),
                    assignment = get_last_index(old_tcc.tutorial_assignment, td_row, 'Assignment'),
                    assignment_user_id = assignment_user_id,
                    assignment_status = get_current_status(old_tcc.tutorial_assignment, old_tcc.tutorial_assignment_status),
                    prerequisite = None,
                    prerequisite_user_id = prerequisite_user_id,
                    prerequisite_status = 0,
                    keyword = old_tcc.tutorial_keywords,
                    keyword_user_id = request.user.id,
                    keyword_status = keyword_status,
                )
            except Exception, e:
                pass
        if new_tcc and old_tcc:
            new_tutorial_path = settings.MEDIA_ROOT + 'videos/' + str(new_tcc.tutorial_detail.foss_id) + '/' + str(new_tcc.tutorial_detail.id) + '/resources/'
            if new_tcc.slide:
                try:
                    copyfile(settings.STVIDEOS_DIR + old_tcc.tutorial_slide, new_tutorial_path + new_tcc.slide)
                except Exception, e:
                    print e
            if new_tcc.code:
                try:
                    copyfile(settings.STVIDEOS_DIR + old_tcc.tutorial_code, new_tutorial_path + new_tcc.code)
                except Exception, e:
                    print e
            if new_tcc.assignment:
                try:
                    copyfile(settings.STVIDEOS_DIR + old_tcc.tutorial_assignment, new_tutorial_path + new_tcc.assignment)
                except Exception, e:
                    print e
        if new_tcc:
            if new_tcc.slide_user_id != request.user.id:
                try:
                    role_rec = RoleRequest.objects.get(user = new_tcc.slide_user, role_type = 0)
                except Exception, e:
                    print 1, e
                    role_rec = RoleRequest.objects.create(user = new_tcc.slide_user, role_type = 0, status = 1, approved_user = request.user)
                if role_rec:
                    try:
                        role_rec.user.groups.add(Group.objects.get(name = 'Contributor'))
                    except Exception, e:
                        print 2, e
                    try:
                        ContributorRole.objects.create(foss_category = new_tcc.tutorial_detail.foss, language = lang_rec, user = role_rec.user, status = 1)
                    except:
                        pass
            if new_tcc.code_user_id != request.user.id and new_tcc.code_user_id != new_tcc.slide_user_id:
                try:
                    role_rec = RoleRequest.objects.get(user = new_tcc.code_user, role_type = 0)
                except Exception, e:
                    print 3, e
                    role_rec = RoleRequest.objects.create(user = new_tcc.code_user, role_type = 0, status = 1, approved_user = request.user)
                if role_rec:
                    try:
                        role_rec.user.groups.add(Group.objects.get(name = 'Contributor'))
                    except Exception, e:
                        print 4, e
                    try:
                        ContributorRole.objects.create(foss_category = new_tcc.tutorial_detail.foss, language = lang_rec, user = role_rec.user, status = 1)
                    except:
                        pass
            if new_tcc.assignment_user_id != request.user.id and new_tcc.assignment_user_id != new_tcc.slide_user_id and new_tcc.assignment_user_id != new_tcc.code_user_id:
                try:
                    role_rec = RoleRequest.objects.get(user = new_tcc.assignment_user, role_type = 0)
                except:
                    role_rec = RoleRequest.objects.create(user = new_tcc.assignment_user, role_type = 0, status = 1, approved_user = request.user)
                if role_rec:
                    try:
                        role_rec.user.groups.add(Group.objects.get(name = 'Contributor'))
                    except:
                        pass
                    try:
                        ContributorRole.objects.create(foss_category = new_tcc.tutorial_detail.foss, language = lang_rec, user = role_rec.user, status = 1)
                    except:
                        pass
            if new_tcc.prerequisite_user_id != request.user.id and new_tcc.prerequisite_user_id != new_tcc.slide_user_id and new_tcc.prerequisite_user_id != new_tcc.code_user_id and new_tcc.prerequisite_user_id != new_tcc.assignment_user_id:
                try:
                    role_rec = RoleRequest.objects.get(user = new_tcc.prerequisite_user, role_type = 0)
                except:
                    role_rec = RoleRequest.objects.create(user = new_tcc.prerequisite_user, role_type = 0, status = 1, approved_user = request.user)
                if role_rec:
                    try:
                        role_rec.user.groups.add(Group.objects.get(name = 'Contributor'))
                    except:
                        pass
                    try:
                        ContributorRole.objects.create(foss_category = new_tcc.tutorial_detail.foss, language = lang_rec, user = role_rec.user, status = 1)
                    except:
                        pass

    update_prerequisite(request)
    return HttpResponse('Success!')

def get_current_tutorial_status(input_status):
    if input_status == 'accepted':
        return 1
    elif input_status == 'public_review':
        return 2
    return 0

@login_required
def tutorial_resources(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    rows = TutorialResources.objects.all()
    new_tr = None
    for row in rows:
        #break
        new_td = get_current_tutorial_detail(row.tutorial_detail)
        print new_td
        if new_td:
            try:
                new_tcc = TutorialCommonContent.objects.get(tutorial_detail = new_td)
                new_lang = Language.objects.get(name = row.language)
                try:
                    new_tr = TutorialResource.objects.get(tutorial_detail = new_td, common_content = new_tcc, language = new_lang)
                except Exception, e:
                    #print 1, e
                    try:
                        outline_user_id = get_current_user_from_old_email(row.tutorial_outline_uid.mail, request.user)
                    except:
                        outline_user_id = request.user.id
                    try:
                        script_user_id = get_current_user_from_old_email(row.tutorial_script_uid.mail, request.user)
                    except:
                        script_user_id = request.user.id
                    try:
                        video_user_id = get_current_user_from_old_email(row.tutorial_video_uid.mail, request.user)
                    except:
                        video_user_id = request.user.id
                    try:
                        new_tr = TutorialResource.objects.create(
                            tutorial_detail = new_td,
                            common_content = new_tcc,
                            language = new_lang,
                            outline = row.tutorial_outline,
                            outline_user_id = outline_user_id,
                            outline_status = get_current_status(row.tutorial_outline, row.tutorial_outline_status),
                            script = row.tutorial_script,
                            script_user_id = script_user_id,
                            script_status = get_current_status(row.tutorial_script, row.tutorial_script_status),
                            timed_script = row.tutorial_script_timed,
                            video = get_last_index(row.tutorial_video, new_td, new_lang.name),
                            video_user_id = video_user_id,
                            video_status = get_current_status(row.tutorial_video, row.tutorial_video_status),
                            status = get_current_tutorial_status(row.tutorial_status),
                            version = row.cvideo_version,
                            hit_count = row.hit_count,
                        )
                    except Exception, e:
                        print 2, e
                        #break
            except Exception, e:
                print 3, e
                #break
        if new_tr:
            if new_tr.outline_user_id != request.user.id:
                try:
                    role_rec = RoleRequest.objects.get(user = new_tr.outline_user, role_type = 0)
                except Exception, e:
                    print 1, e
                    role_rec = RoleRequest.objects.create(user = new_tr.outline_user, role_type = 0, status = 1, approved_user = request.user)
                if role_rec:
                    try:
                        role_rec.user.groups.add(Group.objects.get(name = 'Contributor'))
                    except Exception, e:
                        print 2, e
                    try:
                        ContributorRole.objects.create(foss_category = new_tr.tutorial_detail.foss, language = new_tr.language, user = role_rec.user, status = 1)
                    except:
                        pass
            if new_tr.script_user_id != request.user.id:
                try:
                    role_rec = RoleRequest.objects.get(user = new_tr.script_user, role_type = 0)
                except Exception, e:
                    print 1, e
                    role_rec = RoleRequest.objects.create(user = new_tr.script_user, role_type = 0, status = 1, approved_user = request.user)
                if role_rec:
                    try:
                        role_rec.user.groups.add(Group.objects.get(name = 'Contributor'))
                    except Exception, e:
                        print 2, e
                    try:
                        ContributorRole.objects.create(foss_category = new_tr.tutorial_detail.foss, language = new_tr.language, user = role_rec.user, status = 1)
                    except:
                        pass
            if new_tr.video_user_id != request.user.id:
                try:
                    role_rec = RoleRequest.objects.get(user = new_tr.video_user, role_type = 0)
                except Exception, e:
                    print 1, e
                    role_rec = RoleRequest.objects.create(user = new_tr.video_user, role_type = 0, status = 1, approved_user = request.user)
                if role_rec:
                    try:
                        role_rec.user.groups.add(Group.objects.get(name = 'Contributor'))
                    except Exception, e:
                        print 2, e
                    try:
                        ContributorRole.objects.create(foss_category = new_tr.tutorial_detail.foss, language = new_tr.language, user = role_rec.user, status = 1)
                    except:
                        pass
        if new_tr and new_tr.video:
            new_tutorial_path = settings.MEDIA_ROOT + 'videos/' + str(new_tr.tutorial_detail.foss_id) + '/' + str(new_tr.tutorial_detail.id) + '/'
            try:
                copyfile(settings.STVIDEOS_DIR + row.tutorial_video, new_tutorial_path + new_tr.video)
            except Exception, e:
                print 4, e

    return HttpResponse('Success!')
