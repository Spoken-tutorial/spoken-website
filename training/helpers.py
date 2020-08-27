from events.models import AcademicKey, StudentBatch
from datetime import datetime,date
from certificate.views import _clean_certificate_certificate
from django.http import HttpResponse
import os
from string import Template
import subprocess

EVENT_TYPE_CHOICES =(
	('', '-----'), ('FDP', 'Paid FDP'), ('Workshop', 'Blended Mode Workshop'),('sdp', 'Student Training Programme')
	)

EVENT_AMOUNT = {
     'FDP': '500', 'Workshop': '1000'
    }

# REGISTRATION_TYPE_CHOICES =(
#     ('', '-----'),  (1, 'Subscribed College'),(2, 'Manual Registration')
#     )

def is_user_paid(user_obj):
    try:
        idcase = AcademicKey.objects.get(academic_id=user_obj.organiser.academic_id)
        user_paid = [True, user_obj.organiser.academic] if (idcase.expiry_date >= date.today()) else [False]
        return user_paid
    except:
        user_paid = [False]
    try:
        idcase = AcademicKey.objects.get(academic_id=user_obj.invigilator.academic_id)
        user_paid = [True, user_obj.invigilator.academic] if (idcase.expiry_date >= date.today()) else [False]
        return user_paid
    except:
        user_paid = [False]
    return user_paid

def user_college(user_obj):
    college = ''
    try:
        college = user_obj.organiser.academic
    except Exception as e1:
        try:
             college = user_obj.invigilator.academic
        except Exception as e2:
             #try:
             #      studentbatch_id = user_obj.student.studentmaster_set.values('batch_id')
             #      batch = StudentBatch.objects.get(id=studentbatch_id)
             #      college = batch.academic
             #except:
             #      #user is not associated with any college
             pass
    return college

def handle_uploaded_file(request):
    return "successfull"


def is_college_paid(college_id):
    try:
        idcase = AcademicKey.objects.get(academic_id=college_id)
        college_paid = True if (idcase.expiry_date >= date.today()) else False
        return college_paid
    except:
        college_paid = False
    
    return college_paid

def create_certificate(eventid,pname):
    response = HttpResponse(content_type='application/pdf')
    event = TrainingEvents.objects.get(id=eventid)
    try:        
        file_name = pname
        template = 'training_certificate_template'
        download_file_name = "ST_"+event.event_name+'.pdf'
        certificate_path = os.path.dirname(os.path.realpath(__file__))+"/certificate/"
        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(
            name = pname,
            event_name = event.event_name,
            college = event.host_college.institution_name,
            host_college = event.host_college.institution_name,
            foss = event.foss.foss,
            event_start_date = event.event_start_date
            )
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        out = certificate_path
        
        subprocess.run(['pdflatex','--output-directory',certificate_path,certificate_path+file_name+'.tex'])
        pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'rb')
        response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
        response.write(pdf.read())
        _clean_certificate_certificate(certificate_path, file_name)
        return response
    except Exception as e:
        print("error is ",e)
