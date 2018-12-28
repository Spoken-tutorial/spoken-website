# testcases for stats module
import os
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from cms.models import *
from events.models import *
from mdldjango.models import *
from datetime import datetime, date


def create_user(username, email):
    user = User.objects.create(username=username, email=email, first_name='test_fname', last_name='test_lname')
    user.set_password('demo1')
    user.save()
    profile = Profile.objects.create(user=user, confirmation_code='GarEQvZxVSx7YH8mpfm2PEGcnQLp4NXei')
    profile.save()
    return user

def create_mdluser(firstname, lastname, username, academic_id, user_email, gender):

    mdluser = MdlUser()
    mdluser.auth = 'manual'
    mdluser.id = 1
    mdluser.firstname = firstname
    mdluser.username = username
    mdluser.lastname = lastname
    mdluser.password = 'demo1'
     # mdluser.set_password('demo1')
    mdluser.institution = academic_id
    mdluser.email = user_email
    mdluser.confirmed = 1
    mdluser.mnethostid = 1
    mdluser.gender = gender
    mdluser.save()
    return mdluser



def create_state(name):
    state = State.objects.create(name=name, code=name[:3])
    return state

# def create_district(state, name):
#     return District.objects.create(state=state, name=name)

def create_academic(user, state, name, academic_code, institutetype, institutecategory, university, district, location, city):
    institutetype = InstituteType.objects.create(name=institutetype)
    institutecategory = InstituteCategory.objects.create(name=institutecategory)
    university = University.objects.create(state=state, name=university, user=user)
    institution_name = name
    district = District.objects.create(state=state, name=district)
    location = Location.objects.create(district=district, name=location, pincode=400075)
    city = City.objects.create(state=state, name=city)
    status = 1
    pincode = 400075
    resource_center = 'IIT Powai'
    rating = 1
    contact_person = 'ABC'
    remarks = 'Good'
    academic = AcademicCenter.objects.create(
        user=user, state=state, institution_type=institutetype,
        institute_category=institutecategory,
        university=university,
        institution_name=institution_name,
        academic_code=academic_code,
        district=district,
        location=location,
        city=city,
        status=0,
        pincode=pincode,
        resource_center=resource_center,
        contact_person=contact_person,
        rating=rating,
        remarks=remarks
        )
    return academic

# def create_group(group_name, app_label):                                        
#     try:                                                                        
#        group = Group.objects.get(name=group_name)                              
#     except Group.DoesNotExist:                                                  
#        group = Group(name=group_name)                                          
#        group.save()                                                            
#        # Get the models for the given app                                      
#        content_types = ContentType.objects.filter(app_label=app_label)         
#        # Get list of permissions for the models                                
#        permission_list = Permission.objects.filter(                            
#           content_type__in=content_types)                                     
#        group.permissions.add(*permission_list)                                 
#        group.save()                                                            
#     return group


def create_group(name):
    grp = Group.objects.create(name=name)
    return grp

def create_rp(user, state):
    rp = ResourcePerson.objects.create(user=user, state=state, assigned_by=1, status=1)
    grp = create_group('Resource Person')
    # # grp = create_group('Organiser', 'events')
    grp.user_set.add(user)
    grp.save()
    return rp

def create_organiser_status_zero(user, academic):
    org = Organiser.objects.create(user=user, academic=academic, status=0)
    grp = create_group('Organiser')
    # # grp = create_group('Organiser', 'events')
    grp.user_set.add(user)
    grp.save()
    return org


def create_organiser(user, academic, group_name):
    org = Organiser.objects.create(user=user, academic=academic, status=1)
    # grp = create_group('Organiser')
    # # grp = create_group('Organiser', 'events')
    grp = Group.objects.get(name=group_name)
    grp.user_set.add(user)
    grp.save()
    return org

def create_sem():
    sem = Semester.objects.create(name='Odd', even=0)
    sem2 = Semester.objects.create(name='Even', even=1)
    return sem, sem2

def create_tr_planner(sem, academic, organiser, year):
    tr_planner = TrainingPlanner.objects.create(semester=sem, academic=academic, organiser=organiser, year=year)
    return tr_planner

def create_batch(organiser, academic, department, year, participant_count):
    sb = StudentBatch.objects.create(academic=academic,
            organiser=organiser, department=department, year=year, stcount=participant_count)
    return sb

def create_student(gender, verified_status, userid):
    student = Student.objects.create(gender=gender, verified=verified_status, user_id=userid)
    return student

def create_batch(organiser, academic, department, year, participant_count):
    sb = StudentBatch.objects.create(academic=academic,
            organiser=organiser, department=department, year=year, stcount=participant_count)
    return sb

def create_student_master(batchid, studentid):
    student_master = StudentMaster.objects.create(batch_id=batchid, student_id=studentid)
    return student_master

def create_training_request(sem, participants, batchid, courseid, departmentid, tr_planner):
    tr = TrainingRequest.objects.create(sem_start_date=sem, participants=participants, batch=batchid, course=courseid, department=departmentid, training_planner=tr_planner, status=1)
    return tr

def create_training_attendance(trainingid, studentid, languageid):
    tr_attendance = TrainingAttend.objects.create(training=trainingid, student=studentid, language=languageid)
    return tr_attendance

'''
############################# Test cases started ############################################
'''

class TestMaphome(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = create_user('kirtist', 'abc@gmail.com')#organiser
		self.user_stu = create_user('pooja', 'pooja@gmail.com')
		self.state = create_state('pune')
		self.academic = create_academic(self.user, self.state, 'IITB', 'institutetype1', 'MAH-001', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
		self.group = create_group('Organiser')
		self.organiser = create_organiser(self.user, self.academic, self.group.name)
		self.year = 2018
		self.sem_start_date = date(2018, 7, 1)


		self.participant_count = 10
		self.department = Department.objects.create(name='department 1')
		self.department2 = Department.objects.create(name='department 123')
		self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year, self.participant_count)
		        
		self.verified = 1

		self.student = create_student('Female', self.verified, self.user_stu.id)
		self.student_master = create_student_master(self.batch1.id, self.student.id)

		self.sem_odd, self.sem_even = create_sem()

		self.foss = FossCategory.objects.create(foss='foss1', description = 'testing', status=1, user=self.user)
		self.foss2 = FossCategory.objects.create(foss='foss2', description = 'testing', status=1, user=self.user)
		
		self.coursemap = CourseMap.objects.create(test=1, category=0, foss=self.foss)
		self.coursemap2 = CourseMap.objects.create(test=1, category=0, foss=self.foss2)

		self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')
		self.tr = create_training_request(self.sem_start_date, self.participant_count, self.batch1, self.coursemap, self.department, self.tr_planner)
		self.tr2 = create_training_request(self.sem_start_date, self.participant_count, self.batch1, self.coursemap2, self.department, self.tr_planner)

	def test_context(self):
		response = self.client.get(reverse('statistics:maphome'), follow=True)
		self.assertEqual(response.context["participant_count"], 20)
		self.assertEqual(response.context["training_count"], 2)

class TestGetStateInfo(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = create_user('kirtist', 'abc@gmail.com')#organiser
		self.user_stu = create_user('pooja', 'pooja@gmail.com')
		self.state = create_state('pune')
		self.academic = create_academic(self.user, self.state, 'IITB', 'institutetype1', 'MAH-001', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
		self.group = create_group('Organiser')
		self.organiser = create_organiser(self.user, self.academic, self.group.name)
		self.year = 2018
		self.sem_start_date = date(2018, 7, 1)


		self.participant_count = 10
		self.department = Department.objects.create(name='department 1')
		self.department2 = Department.objects.create(name='department 123')
		self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year, self.participant_count)
		        
		self.verified = 1

		self.student = create_student('Female', self.verified, self.user_stu.id)
		self.student_master = create_student_master(self.batch1.id, self.student.id)

		self.sem_odd, self.sem_even = create_sem()

		self.foss = FossCategory.objects.create(foss='foss1', description = 'testing', status=1, user=self.user)
		self.foss2 = FossCategory.objects.create(foss='foss2', description = 'testing', status=1, user=self.user)
		
		self.coursemap = CourseMap.objects.create(test=1, category=0, foss=self.foss)
		self.coursemap2 = CourseMap.objects.create(test=1, category=0, foss=self.foss2)

		self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')
		self.tr = create_training_request(self.sem_start_date, self.participant_count, self.batch1, self.coursemap, self.department, self.tr_planner)
		self.tr2 = create_training_request(self.sem_start_date, self.participant_count, self.batch1, self.coursemap2, self.department, self.tr_planner)

	def test_context(self):
		response = self.client.get(reverse('statistics:get_state_info', args=(self.state.code,)), follow=True)
		self.assertEqual(response.context["participants"], 20)
		self.assertEqual(response.context["workshops"], 2)

class TestFdpTraining(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = create_user('kirtist', 'abc@gmail.com')#organiser
		self.user_stu = create_user('pooja', 'pooja@gmail.com')
		self.state = create_state('pune')
		self.academic = create_academic(self.user, self.state, 'IITB', 'institutetype1', 'MAH-001', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
		self.group = create_group('Organiser')
		self.organiser = create_organiser(self.user, self.academic, self.group.name)
		self.year = 2018
		self.sem_start_date = date(2018, 7, 1)


		self.participant_count = 10
		self.department2 = Department.objects.create(name='Faculty Development Programs (FDPs)(PMMMNMTT)')
		self.department = Department.objects.create(name='department 123')

		self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year, self.participant_count)
		        
		self.verified = 1

		self.student = create_student('Female', self.verified, self.user_stu.id)
		self.student_master = create_student_master(self.batch1.id, self.student.id)

		self.sem_odd, self.sem_even = create_sem()

		self.foss = FossCategory.objects.create(foss='foss1', description = 'testing', status=1, user=self.user)
		self.foss2 = FossCategory.objects.create(foss='foss2', description = 'testing', status=1, user=self.user)
		
		self.coursemap = CourseMap.objects.create(test=1, category=0, foss=self.foss)
		self.coursemap2 = CourseMap.objects.create(test=1, category=0, foss=self.foss2)

		self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')
		self.tr = create_training_request(self.sem_start_date, self.participant_count, self.batch1, self.coursemap, self.department, self.tr_planner)
		self.tr2 = create_training_request(self.sem_start_date, self.participant_count, self.batch1, self.coursemap2, self.department, self.tr_planner)

	def test_context(self):
		response = self.client.get(reverse('statistics:fdp_training'), follow=True)
		self.assertEqual(response.context["participants"], {'participants__sum': 20})

class TestTraining(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = create_user('kirtist', 'abc@gmail.com')#organiser
		self.user_stu = create_user('pooja', 'pooja@gmail.com')
		self.state = create_state('pune')
		self.academic = create_academic(self.user, self.state, 'IITB', 'institutetype1', 'MAH-001', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
		self.group = create_group('Organiser')
		self.organiser = create_organiser(self.user, self.academic, self.group.name)
		self.year = 2018
		self.sem_start_date = date(2018, 7, 1)


		self.participant_count = 10
		self.department2 = Department.objects.create(name='Faculty Development Programs (FDPs)(PMMMNMTT)')
		self.department = Department.objects.create(name='department 123')

		self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year, self.participant_count)
		        
		self.verified = 1

		self.student = create_student('Female', self.verified, self.user_stu.id)
		self.student_master = create_student_master(self.batch1.id, self.student.id)

		self.sem_odd, self.sem_even = create_sem()

		self.foss = FossCategory.objects.create(foss='foss1', description = 'testing', status=1, user=self.user)
		self.foss2 = FossCategory.objects.create(foss='foss2', description = 'testing', status=1, user=self.user)
		
		self.coursemap = CourseMap.objects.create(test=1, category=0, foss=self.foss)
		self.coursemap2 = CourseMap.objects.create(test=1, category=0, foss=self.foss2)

		self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')
		self.tr = create_training_request(self.sem_start_date, self.participant_count, self.batch1, self.coursemap, self.department, self.tr_planner)
		self.tr2 = create_training_request(self.sem_start_date, self.participant_count, self.batch1, self.coursemap2, self.department, self.tr_planner)

	def test_context(self):
		response = self.client.get(reverse('statistics:fdp_training'), follow=True)
		self.assertEqual(response.context["participants"], {'participants__sum': 20})

