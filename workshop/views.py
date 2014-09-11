from django.shortcuts import render
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.template.defaultfilters import slugify
from workshop.models import WAcademicCenter
from events.models import AcademicCenter
# Create your views here.

def view_college(request, collage_id=None):
    try:
        college = WAcademicCenter.objects.get(id = collage_id)
        academic = AcademicCenter.objects.get(academic_code = college.academic_code)
        redirect_url = "/software-training/academic-center/" + str(academic.id) + "/" + slugify(academic.institution_name)
        return HttpResponsePermanentRedirect(redirect_url)
    except Exception, e:
        return HttpResponseRedirect('/')
