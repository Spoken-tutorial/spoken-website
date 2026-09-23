from django.conf import settings
from spoken.config import EDUPYRAMIDS_CERTIFICATE_DATE,WGF_INSTITUTIONS
import re
import os
from reportlab.lib.utils import ImageReader

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

WGF = {
   'stp': 'Blank-Certificate_edupyramids_wgf.pdf',
}

def is_wgf_institution(academic_code):
   return academic_code in WGF_INSTITUTIONS


def get_participation_certificate_title(academic_code,normal_title_y,wgf_title_y):
   """
   Returns participation certificate title and title position.
   """
   if academic_code in WGF_INSTITUTIONS:
      certificate_title = "Certificate of Participation"
      title_y = wgf_title_y
   else:
      certificate_title = "Participation Certificate"
      title_y = normal_title_y

   return certificate_title, title_y


def get_completion_certificate_title(academic_code,normal_title_y,wgf_title_y,foss_name):
   """
   Returns completion certificate title and title position.
   """
   if academic_code in WGF_INSTITUTIONS:
      certificate_title = "Course Completion Certificate"
      title_y = wgf_title_y
   else:
      certificate_title = ("Certificate for the Completion of <br/>"+ foss_name+ " Training")
      title_y = normal_title_y

   return certificate_title, title_y

def get_cert_template(event_date, cert_type, academic_code=None):
   if academic_code in WGF_INSTITUTIONS:
      return os.path.join(settings.MEDIA_ROOT, WGF['stp'])
   if event_date < EDUPYRAMIDS_CERTIFICATE_DATE:
      return os.path.join(settings.MEDIA_ROOT, SPK[cert_type])
   return os.path.join(settings.MEDIA_ROOT, EDUPYRAMIDS[cert_type])


def get_training_certificate(ta):
   """
      return training certificate template path
      ta : TrainingAttend obj
   """
   academic_code = ta.training.training_planner.academic.academic_code
   if ta.training.department.id == FDP:
      cert_type = 'fdp'
   elif ta.training.training_planner.academic.institution_type_id == CSC:
      cert_type = 'csc'
   else:
      cert_type = 'stp'
   return get_cert_template(ta.training.training_start_date, cert_type, academic_code)


def get_test_certificate(ta):
   """
      return test certificate template path
      ta : TestAttendance obj
   """

   academic_code = ta.test.academic.academic_code
   if ta.test.training.department.id == FDP:
      cert_type = 'fdp_test'
   elif ta.test.academic.institution_type_id == CSC:
      cert_type = 'csc'
   else:
      cert_type = 'stp'
   return get_cert_template(ta.test.tdate, cert_type, academic_code)


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

   academic = ta.training.training_planner.academic
   academic_code = academic.academic_code
   
   institution_name = ta.training.training_planner.academic.institution_name
   organization = get_organization(ta.training.training_start_date)
   org_course_material = "EduPyramids, SINE, IIT Bombay"
   org_training = "This training is offered through SWAYAM Plus by EduPyramids, SINE, IIT Bombay"

   if is_wgf_institution(academic_code):
      text = (
         f"This is to certify that <b>{name}</b> has participated in the "
         f"<b>{foss}</b> training, offered by "
         f"<b>EduPyramids, SINE, IIT Bombay</b>."
         f"<br /><br />"
         f"A comprehensive set of topics pertaining to "
         f"<b>{foss}</b> was covered in the training."
      )
      return text
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
   test_date = test.tdate.strftime("%d-%m-%Y")
   academic = test.academic
   academic_code = academic.academic_code
   institution = test.academic.institution_name
   organization = get_organization(test.training.training_start_date)
   organizer = f"{test.organiser.user.first_name} {test.organiser.user.last_name}"
   invigilator = f"{test.invigilator.user.first_name} {test.invigilator.user.last_name}"
   org_training = "This training is offered through SWAYAM Plus by EduPyramids, SINE, IIT Bombay"
   text_end = f"{org_training}"

   # WGF completion certificate text
   if is_wgf_institution(academic_code):
      text = (
         f"This is to certify that <b>{name}</b> has successfully "
         f"completed the course <b>{foss}</b>, offered by "
         f"<b>EduPyramids, SINE, IIT Bombay</b>."
         f"<br /><br />"
         f"Passing an online exam conducted remotely by EduPyramids "
         f"is a prerequisite to complete this course. "
         f"<b>WHEELS Global Foundation</b> organised the invigilation "
         f"of this exam."
         f"<br /><br />"
         f"{credits}"
      )
      return text

   
   #paragraphe
   if test.training.department.id == FDP:
      text = f"This is to certify that <b>{name}</b> has successfully completed <b>{foss}</b> test on <b>{test_date}</b> organized at <b>{institution}</b> by <b>{organizer}</b> with course material provided by {organization}. Passing an online exam, conducted remotely from IIT Bombay, is a pre-requisite for completing this Faculty Development Programme.<br/><br/><b>{invigilator}</b> at <b>{institution}</b> invigilated this examination. {text_end}.</p><br /><br />{credits}"
   elif test.academic.institution_type_id == CSC: # CHECK #TODO
      text = f"This is to certify that <b>{name}</b> has successfully completed <b>{foss}</b> test organized at {institution} by <u>{organizer}</u> with course material provided by {organization}. Passing an online exam, conducted remotely from IIT Bombay, is a pre-requisite for completing this training. <u>{invigilator}</u> at {institution} invigilated this examination.<br/>This training is offered by the Spoken Tutorial Project, IIT Bombay, funded by National Mission on Education through ICT, Ministry of Education, Govt., of India."
   else:
      text = f"This is to certify that <b>{name}</b> has successfully completed <b>{foss}</b> test organized at <b>{institution}</b> by <b>{organizer}</b>  with course material provided by {organization}. Passing an online exam, conducted remotely from IIT Bombay, is a pre-requisite for completing this training. <br /><p><b>{invigilator}</b> from <b>{institution}</b> invigilated this examination. {text_end}.</p><br /><br />{credits}"
   return text


def get_aspect_height(imgPath, width):
    """
    Returns the height of the image based on a fixed width of 160 pixels, maintaining aspect ratio.
    """
    img = ImageReader(imgPath)
    original_width, original_height = img.getSize()
    height = width * original_height / original_width
    return height
