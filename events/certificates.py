from django.conf import settings
from spoken.config import EDUPYRAMIDS_CERTIFICATE_DATE
import re
import os

SCHOOL = 24
FDP = 169
CSC = 18

SPK = {
   'stp': 'Blank-Certificate.pdf',
   'fdp': 'fdptr-certificate.pdf',
   'csc': 'Certificate_CSC_blank.pdf',
   'fdp_test': 'fdp-test-certificate.pdf',
}
EDUPYRAMIDS = {
   'stp': 'Blank-Certificate_edupyramids.pdf',
   'fdp': 'fdptr-certificate_edupyramids.pdf',
   'csc': 'Certificate_CSC_blank_edupyramids.pdf',
   'fdp_test': 'fdp-test-certificate_edupyramids.pdf',
}

def get_cert_template(event_date, cert_type):
   if event_date < EDUPYRAMIDS_CERTIFICATE_DATE:
      return os.path.join(settings.MEDIA_ROOT, SPK[cert_type])
   return os.path.join(settings.MEDIA_ROOT, EDUPYRAMIDS[cert_type])


def get_training_certificate(ta):
   """
      return training certificate template path
      ta : TrainingAttend obj
   """
   
   if ta.training.department.id == FDP:
      cert_type = 'fdp'
   elif ta.training.training_planner.academic.institution_type_id == CSC:
      cert_type = 'csc'
   else:
      cert_type = 'stp'
   return get_cert_template(ta.training.training_start_date, cert_type)


def get_test_certificate(ta):
   """
      return test certificate template path
      ta : TestAttendance obj
   """
   if ta.test.training.department.id == FDP:
      cert_type = 'fdp_test'
   elif ta.test.academic.institution_type_id == CSC:
      cert_type = 'csc'
   else:
      cert_type = 'stp'
   return get_cert_template(ta.test.tdate, cert_type)


def get_signature(event_date):
   if event_date < EDUPYRAMIDS_CERTIFICATE_DATE:
      return settings.MEDIA_ROOT +"sign.jpg"
   return settings.MEDIA_ROOT +"sign_edupyramids.jpg"

def get_organization(event_date):
   if event_date < EDUPYRAMIDS_CERTIFICATE_DATE:
      return "the Spoken Tutorial Project, IIT Bombay"
   return "EduPyramids, SINE, IIT Bombay"

def get_training_cert_text(ta):
   """
      ta : TrainingAttend obj
   """
   name = f"{ta.student.user.first_name} {ta.student.user.last_name}"
   foss = ta.training.course.foss.foss
   institution_name = ta.training.training_planner.academic.institution_name
   organization = get_organization(ta.training.training_start_date)
   
   semsplit = re.split('-|, ',ta.training.training_planner.get_semester())
   sem_start = semsplit[0]+semsplit[2]

   text_end = f"A comprehensive set of topics pertaining to <b>{foss}</b> were covered in the training. This training is offered by {organization}"
   
   #paragraph
   text = f"This is to certify that <b>{name}</b> participated in the <b>{foss}</b> training organized at <b>{institution_name}</b> in <b>{sem_start}</b> semester, with course material provided by {organization}.<br /><br />{text_end}."
   if ta.training.department.id == SCHOOL:
      organiser_name = f"{ta.training.training_planner.organiser.user.first_name} {ta.training.training_planner.organiser.user.last_name}"
      text = f"This is to certify that <b>{name}</b> participated in the <b>{foss}</b> training organized at <b>{institution_name}</b> by <b>{organiser_name}</b>, with course material provided by {organization}.<br /><br />{text_end}."
   elif ta.training.department.id == FDP:
      formatted_start_date = ta.training.training_start_date.strftime("%d-%m-%Y")
      formatted_end_date = ta.training.training_end_date.strftime("%d-%m-%Y")
      text = f"This is to certify that <b>{name}</b> has participated in <b>Faculty Development Programme</b> from <b>{formatted_start_date}</b> to <b>{formatted_end_date}</b> on <b>{foss}</b> organized by <b>{institution_name}</b> with course material provided by {organization}.<br />{text_end}."
   elif ta.training.training_planner.academic.institution_type_id == CSC:
      sem = ta.training.training_planner.get_semester()
      text = f"This is to certify that <u>{name}</u> participated in the <b>{foss}</b> training organized at {institution_name} in {sem} semester, with course material provided by {institution_name}.<br />{text_end}."
   return text


def get_test_cert_text(test, mdluser, credits=''):
   """
      mdluser : MdlUser obj
      test : Test obj
   """
   name = f"{mdluser.firstname} {mdluser.lastname}"
   foss = test.foss.foss
   test_date = test.tdate
   
   institution = test.academic.institution_name
   organization = get_organization(test.training.training_start_date)
   organizer = f"{test.organiser.user.first_name} {test.organiser.user.last_name}"
   invigilator = f"{test.invigilator.user.first_name} {test.invigilator.user.last_name}"
   text_end = f"This training is offered by {organization}"
   
   #paragraphe
   if test.training.department.id == FDP:
      text = f"This is to certify that <b>{name}</b> has successfully completed <b>{foss}</b> test on <b>{test_date}</b> organized at <b>{institution}</b> by <b>{organizer}</b> with course material provided by {organization}. Passing an online exam, conducted remotely from IIT Bombay, is a pre-requisite for completing this Faculty Development Programme.<br/><br/><b>{invigilator}</b> at <b>{institution}</b> invigilated this examination. {text_end}.</p><br /><br />{credits}"
   elif test.academic.institution_type_id == CSC: # CHECK #TODO
      text = f"This is to certify that <b>{name}</b> has successfully completed <b>{foss}</b> test organized at {institution} by <u>{organizer}</u> with course material provided by {organization}. Passing an online exam, conducted remotely from IIT Bombay, is a pre-requisite for completing this training. <u>{invigilator}</u> at {institution} invigilated this examination.<br/>This training is offered by the Spoken Tutorial Project, IIT Bombay, funded by National Mission on Education through ICT, Ministry of Education, Govt., of India."
   else:
      text = f"This is to certify that <b>{name}</b> has successfully completed <b>{foss}</b> test organized at <b>{institution}</b> by <b>{organizer}</b>  with course material provided by {organization}. Passing an online exam, conducted remotely from IIT Bombay, is a pre-requisite for completing this training. <br /><p><b>{invigilator}</b> from <b>{institution}</b> invigilated this examination. {text_end}.</p><br /><br />{credits}"
   return text