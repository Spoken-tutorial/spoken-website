from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.shortcuts import render
from cdeep.models import *
from creation.models import *
# Create your views here.

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
    for row in rows:
        foss_row = FossCategory.objects.get(foss = row.foss_category.replace("-", " "))
        try:
            td_row = TutorialDetail.objects.get(foss = foss_row, tutorial = row.tutorial_name.replace("-", " "), level_id = levels[row.tutorial_level])
        except Exception, e:
            TutorialDetail.objects.create(foss = foss_row, tutorial = row.tutorial_name.replace("-", " "), level_id = levels[row.tutorial_level], order = row.order_code, user = request.user)
    return HttpResponse('Success!')

@login_required
def tutorial_common_contents(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    levels = {
        'C2': 1,
        'C3': 2,
        'C4': 3,
    }
    rows = TutorialCommonContents.objects.select_related().all()
    for row in rows:
        td_row = TutorialDetail.objects.get(foss__foss = row.tutorial_detail.foss_category)
