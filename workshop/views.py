from django.shortcuts import render
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.template.defaultfilters import slugify
from workshop.models import WAcademicCenter, WWorkshopRequests, WWorkshopFeedback
from events.models import AcademicCenter, State, Training, TrainingFeedback
import base64
# Create your views here.

def view_college(request, collage_id=None):
    try:
        college = WAcademicCenter.objects.get(id = collage_id)
        academic = AcademicCenter.objects.get(academic_code = college.academic_code)
        redirect_url = "/software-training/academic-center/" + str(academic.id) + "/" + slugify(academic.institution_name)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception, e:
        return HttpResponseRedirect('/')

def training_list(request, state_code=None):
    try:
        state = State.objects.get(code = state_code)
        redirect_url = "/statistics/training-onlinetest/training/?academic__state={0}".format(state.id)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception, e:
        return HttpResponseRedirect('/')

def view_training(request, old_workshop_id=None):
    try:
        old_workshop = WWorkshopRequests.objects.get(id = old_workshop_id)
        training = Training.objects.get(training_code = old_workshop.workshop_code)
        redirect_url = "/statistics/training-onlinetest/training/{0}/participant/".format(training.id)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception, e:
        return HttpResponseRedirect('/')

def training_feedback(request, code=None):
    code = base64.b64decode(code)
    try:
        training = Training.objects.get(training_code = code)
        redirect_url = "/statistics/training-onlinetest/training/{0}/participant/".format(training.id)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception, e:
        return HttpResponseRedirect('/')

def view_training_feedback(request, code=None, feedback_id=None):
    code = base64.b64decode(code)
    feedback_id = base64.b64decode(feedback_id)
    try:
        training = Training.objects.get(training_code = code)
        old_feedback = WWorkshopFeedback.objects.get(user_id=feedback_id)
        feedback = TrainingFeedback.objects.get(training=training, mdluser_id=old_feedback.user_id)
        redirect_url = "/software-training/training/participant/feedback/{0}/{1}/".format(training.id, feedback.mdluser_id)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception, e:
        return HttpResponseRedirect('/')

def academic_details(request):
    try:
        redirect_url = "/statistics/academic-center/"
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception, e:
        return HttpResponseRedirect('/')

def academic_details_state(request, state=None):
    try:
        state = state.split('=')[1]
        state = State.objects.get(code=state)
        redirect_url = "/statistics/academic-center/?state={0}".format(state.id)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception, e:
        return HttpResponseRedirect('/')
