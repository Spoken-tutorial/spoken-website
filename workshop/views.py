# Standard Library
import base64

# Third Party Stuff
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.template.defaultfilters import slugify

# Spoken Tutorial Stuff
from events.models import AcademicCenter, State, Training, TrainingFeedback
from workshop.models import WAcademicCenter, WWorkshopFeedback, WWorkshopRequests


def view_college(request, collage_id=None, college_name=None):
    if not collage_id:
        return HttpResponsePermanentRedirect('/statistics/academic-center/')
    try:
        college = WAcademicCenter.objects.get(id=collage_id)
        academic = AcademicCenter.objects.get(academic_code=college.academic_code)
        redirect_url = "/statistics/academic-center/" + str(academic.id) + "/" + slugify(academic.institution_name)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception:
        return HttpResponseRedirect('/')


def training_list(request, state_code=None):
    try:
        state = State.objects.get(code=state_code)
        redirect_url = "/statistics/training-onlinetest/training/?academic__state={0}".format(state.id)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception:
        return HttpResponseRedirect('/')


def view_training(request, old_workshop_id=None):
    try:
        old_workshop = WWorkshopRequests.objects.get(id=old_workshop_id)
        training = Training.objects.get(training_code=old_workshop.workshop_code)
        redirect_url = "/statistics/training-onlinetest/training/{0}/participant/".format(training.id)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception:
        return HttpResponseRedirect('/')


def training_feedback(request, code=None):
    code = base64.b64decode(code)
    try:
        training = Training.objects.get(training_code=code)
        redirect_url = "/statistics/training-onlinetest/training/{0}/participant/".format(training.id)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception:
        return HttpResponseRedirect('/')


def view_training_feedback(request, code=None, user_id=None):
    if '/' in code:
        tmp = code.split('/')
        code = tmp[0]
    code = base64.b64decode(code)
    user_id = base64.b64decode(user_id)
    try:
        training = Training.objects.get(training_code=code)
        old_feedback = None
        try:
            old_feedback = WWorkshopFeedback.objects.get(user_id=user_id)
        except MultipleObjectsReturned:
            old_feedback = WWorkshopFeedback.objects.filter(user_id=user_id).first()
        feedback = TrainingFeedback.objects.get(training=training, mdluser_id=old_feedback.user_id)
        redirect_url = "/software-training/training/participant/feedback/{0}/{1}/".format(
            training.id, feedback.mdluser_id)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception:
        return HttpResponseRedirect('/')


def academic_details(request):
    try:
        redirect_url = "/statistics/academic-center/"
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception:
        return HttpResponseRedirect('/')


def academic_details_state(request, state=None):
    try:
        if '=' in state:
            state = state.split('=')[1]
        state = State.objects.get(code=state)
        redirect_url = "/statistics/academic-center/?state={0}".format(state.id)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception:
        return HttpResponseRedirect('/')


def statistics_training(request):
    return HttpResponsePermanentRedirect('/statistics/training-onlinetest/training/')
