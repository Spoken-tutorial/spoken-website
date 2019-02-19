import os
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from cms.models import *
from events.models import *
from mdldjango.models import *
from events.formsv2 import StudentBatchForm
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
    state = State.objects.create(name=name)
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


class TestEventDdashboard(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
                                                        
        self.academic = create_academic(self.user, self.state, 'IITB', 'MAH-001', 'institutetype1', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')

    def test_dashboard_denies_without_login(self):
        response = self.client.get(reverse('events:events_dashboard'), follow=True)
        redirect_url = 'accounts/login/?next=/software-training/'
        self.assertRedirects(response, redirect_url)

    def test_dashboard_with_login(self):
        a = self.client.login(
            username=self.user.username,
            password=self.user_pass
        )
        response = self.client.get(reverse('events:events_dashboard'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/templates/events_dashboard.html')

    def test_user_roles_empty(self):
        a = self.client.login(
            username=self.user.username,
            password=self.user_pass
        )
        response = self.client.get(reverse('events:events_dashboard'), follow=True)
        self.assertEqual(response.context['roles'], [])

    def test_user_roles_entry(self):
        a = self.client.login(
            username=self.user.username,
            password=self.user_pass
        )
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)
        response = self.client.get(reverse('events:events_dashboard'), follow=True)
        self.assertEqual(response.context['roles'], ['Organiser'])

##################

class TestOrganiserRequest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user, self.state, 'IITB', 'MAH-001', 'institutetype1', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')

        self.grp = create_group('Organiser')
        

    def test_denies_anonymous(self):   
        response = self.client.get(reverse('events:organiser_request', kwargs={'username': self.user.username}), follow=True)
        redirect_url = 'accounts/login/?next=/software-training/organiser/request/'+self.user.username+'/'
        self.assertRedirects(response, redirect_url)

    def test_request_with_login(self):
        a = self.client.login(
            username=self.user.username,
            password=self.user_pass
        )
        response = self.client.get(reverse('events:organiser_request', kwargs={'username': self.user.username}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/templates/organiser/form.html')

    def test_org_request_post(self):
        """
        POST request to add organiser entry in Organiser table with status 0
        """
        a = self.client.login(
            username=self.user.username,
            password=self.user_pass
        )
        response = self.client.post(
                reverse('events:organiser_request', kwargs={'username': self.user.username}),
                data = {
                    'state': self.state.id,
                    'college': self.academic.id
                }
            )
        organiser = Organiser.objects.get(user=self.user)
        self.assertEqual(organiser.academic, self.academic)
        self.assertEqual(organiser.status, 0)
        # redirect_url = 'software-training/organiser/view/'+self.user.username+'/'
        # self.assertRedirects(response, redirect_url)
        # self.assertContains(response, "Thank you. Your request has been sent for Training Manager's approval.")

class TestRpOrganiser(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_org = create_user('kirtist', 'abc@gmail.com')
        self.user_rp = create_user('rp', 'abcrp@gmail.com')
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user_rp, self.state, 'IITB', 'MAH-001', 'institutetype1', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')

        self.organiser = create_organiser_status_zero(self.user_org, self.academic)


    def test_denies_activate_if_not_rp(self):
        a = self.client.login(
            username=self.user_rp.username,
            password=self.user_pass
        )

        response = self.client.get(reverse('events:rp_organiser', 
            kwargs={'status': 'active',
                    'code': 'GarEQvZxVSx7YH8mpfm2PEGcnQLp4NXei',
                    'userid': self.user_org.id
            }),
         follow=True)
        self.assertEquals(response.status_code, 403)

    def test_organiser_status_change(self):
        a = self.client.login(
            username=self.user_rp.username,
            password=self.user_pass
        )
        self.rp = create_rp(self.user_rp, self.state)
        response = self.client.get(reverse('events:rp_organiser', 
            kwargs={'status': 'active',
                    'code': 'GarEQvZxVSx7YH8mpfm2PEGcnQLp4NXei',
                    'userid': self.user_org.id
            }),
         follow=True)
        self.org = Organiser.objects.get(user=self.user_org)
        self.assertEquals(self.org.status, 1)
        response_for_block = self.client.get(reverse('events:rp_organiser', 
            kwargs={'status': 'block',
                    'code': 'GarEQvZxVSx7YH8mpfm2PEGcnQLp4NXei',
                    'userid': self.user_org.id
            }),
         follow=True)
        self.org = Organiser.objects.get(user=self.user_org)
        self.assertEquals(self.org.status, 2)


class TestTrainingPlannerListView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user, self.state, 'IITB', 'MAH-001', 'institutetype1', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')

    def test_denies_anonymous(self):
        response = self.client.get(reverse('events:training_planner'), follow=True)
        redirect_url = 'accounts/login/?next=/software-training/training-planner/'
        self.assertRedirects(response, redirect_url)

    # def test_user_not_organiser(self):
    #     a = self.client.login(
    #         username=self.user.username,
    #         password=self.user_pass
    #     )
    #     self.sem_odd, self.sem_even = create_sem()
    #     response = self.client.get(reverse('events:training_planner'))
    #     self.assertEqual(response.status_code, 302)

    def test_show_page_to_organiser(self):
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)
        self.sem_odd, self.sem_even = create_sem()
        self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')
        a = self.client.login(
            username=self.user.username,
            password=self.user_pass
        )
        response = self.client.get(reverse('events:training_planner'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'training_planner.html')
        
    def test_next_planner_ready(self):
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)
        self.sem_odd, self.sem_even = create_sem()
        self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')

        a = self.client.login(
            username=self.user.username,
            password=self.user_pass
        )
        response = self.client.get(reverse('events:training_planner'))
        self.assertEqual(response.context['current_planner'], self.tr_planner)

        self.tr_next_planner = TrainingPlanner.objects.get(semester=self.sem_even)
        self.assertEqual(response.context['next_planner'], self.tr_next_planner)


class TestStudentBatchListView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user, self.state, 'IITB', 'MAH-001', 'institutetype1', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)

        self.year = 2018
        self.department = Department.objects.create(name='department 1')

    def test_denies_anonymous(self):
        response = self.client.get(reverse('events:batch_list'), follow=True)
        redirect_url = 'accounts/login/?next=/software-training/student-batch/'
        self.assertRedirects(response, redirect_url)

    # def test_check_existing_batchlist(self):
    #     response = self.client.get(reverse('events:batch_list'), follow=True)
    #     print response.context
    #     self.assertFalse('object_list' in response.context)

    #     sb = StudentBatch.objects.create(academic=self.academic,
    #         organiser=self.organiser, department=self.department, year=self.year)

    #     self.assertTrue('object_list' in response.context)


# class TestStudentBatchCreateView(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = create_user('kirtist', 'abc@gmail.com')
#         self.user_pass = 'demo1'

#         self.state = create_state('maharashtra')
#         self.academic = create_academic(self.user, self.state, 'IITB', 'MAH-001', 'institutetype1', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
#         self.group = create_group('Organiser')
#         self.organiser = create_organiser(self.user, self.academic, self.group.name)

#         self.year = 2018
#         self.department = Department.objects.create(name='department 1')

#     def test_denies_anonymous(self):
#         response = self.client.get(reverse('events:add_batch'), follow=True)
#         redirect_url = 'accounts/login/?next=/software-training/student-batch/new/'
#         self.assertRedirects(response, redirect_url)




class TestStudentBatchCreateView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')#organiser
        self.user_stu = create_user('student1', 'abcstu@gmail.com')#student
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user, self.state, 'IITB', 'institutetype1', 'MAH-001', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)

        self.year = 2018
        self.participant_count = 1
        self.department = Department.objects.create(name='department 1')
        self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year,
                                   self.participant_count)

    def test_create_new_batch_get(self):
        self.client.login(username=self.user.username, password=self.user_pass)
        response = self.client.get(reverse('events:add_batch'))
        self.assertEqual(response.status_code, 200)


    def test_create_new_batch_post(self):
        # Given
        data = {}
        # When
        self.client.login(username=self.user.username, password=self.user_pass)
        response = self.client.post(reverse('events:add_batch'), data)
        # Then
        print response.content
        self.assertEqual(response.status_code, 200)
        # self.assertFormError(response, StudentBatchForm, 'department', "This field is required.")



class TestStudentListView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')#organiser
        self.user_stu = create_user('student1', 'abcstu@gmail.com')#student
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user, self.state, 'IITB', 'institutetype1', 'MAH-001', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)

        self.year = 2018
        self.participant_count = 1
        self.department = Department.objects.create(name='department 1')
        self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year, self.participant_count)
        
        self.verified = 1

        self.student1 = create_student('Female', self.verified, self.user_stu.id)
        self.student_master = create_student_master(self.batch1.id, self.student1.id)

    def test_denies_anonymous(self):
        response = self.client.get(reverse('events:list_student', kwargs={'bid': self.batch1.id,}), follow=True)
        redirect_url = 'accounts/login/?next=/software-training/student-batch/'+str(self.batch1.id)+'/view/'
        self.assertRedirects(response, redirect_url)

    def test_batch(self):
        a = self.client.login(
            username=self.user.username,
            password=self.user_pass
        )
        response = self.client.get(reverse('events:list_student', kwargs={'bid': self.batch1.id,}), follow=True)
        self.assertEqual(response.context["batch"], self.batch1)

    #check student in queryset

class TestUpdateStudentName(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')#organiser
        self.user_stu = create_user('student1', 'abcstu@gmail.com')#student
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user, self.state, 'IITB', 'institutetype1', 'MAH-001', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)

        self.year = 2018
        self.participant_count = 1
        self.department = Department.objects.create(name='department 1')
        self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year, self.participant_count)
        
        self.verified = 1

        self.student1 = create_student('Female', self.verified, self.user_stu.id)
        self.mdluser = create_mdluser(self.user_stu.first_name, self.user_stu.last_name, self.user_stu.username, self.academic.id, self.user_stu.email, 'Female')

    # def test_denies_anonymous(self):
    #     response = self.client.get(reverse('events:update_student', 
    #         kwargs={'bid': self.batch1.id, 'pk': self.user_stu.id}), follow=True)
    #     redirect_url = 'accounts/login/?next=/software-training/student-batch/'+str(self.batch1.id)+'/view/'
    #     self.assertRedirects(response, redirect_url)

    def test_edit_post_status(self):
        self.client.login(username=self.user.username, password=self.user_pass)
        response = self.client.post(reverse('events:update_student', 
            kwargs = {'bid': self.batch1.id, 'pk': self.user_stu.id}), 
            data = {'gender': self.student1.gender, 'first_name': self.user_stu.first_name,
                'last_name': self.user_stu.last_name, 'email': self.user_stu.email}, 
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_edit_post_data(self):
        new_firstname = 'student1_new'
        old_email = self.user_stu.email

        self.client.login(username=self.user.username, password=self.user_pass)
        response = self.client.post(reverse('events:update_student', 
            kwargs = {'bid': self.batch1.id, 'pk': self.user_stu.id}), 
            data = {'gender': self.student1.gender, 'first_name': 'student1_new',
                'last_name': self.user_stu.last_name, 'email': self.user_stu.email}, 
            follow=True)

        user_stu_new = User.objects.get(id=self.user_stu.id)
        self.assertEquals(user_stu_new.first_name, new_firstname)
        
        mdl_user_stu_new = MdlUser.objects.get(email=old_email)
        self.assertEquals(mdl_user_stu_new.firstname, new_firstname)

    def test_edit_email_post(self):
        new_firstname = 'student1_new'
        old_email = self.user_stu.email #abcstu@gmail.com
        new_email = 'xyzstu@gmail.com'
        verified_status = 0

        self.client.login(username=self.user.username, password=self.user_pass)
        response = self.client.post(reverse('events:update_student', 
            kwargs = {'bid': self.batch1.id, 'pk': self.user_stu.id}), 
            data = {'gender': self.student1.gender, 'first_name': 'student1_new',
                'last_name': self.user_stu.last_name, 'email': new_email}, 
            follow=True)

        user_stu_new = User.objects.get(id=self.user_stu.id)
        self.assertEquals(user_stu_new.email, new_email)

        stu = Student.objects.get(user=self.user_stu)
        self.assertEquals(stu.verified, verified_status)


class TestStudentMasterDeleteView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')#organiser
        self.user2 = create_user('nancy', 'xyz@gmail.com')#organiser2
        self.user_stu = create_user('student1', 'abcstu@gmail.com')#student
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user, self.state, 'IITB', 'MAH-001', 'institutetype1', 'institutecategory1', 'university1', 'mumbai', 'location1', 'mumbai')
        self.academic2 = create_academic(self.user, self.state, 'IITM', 'MAH-002', 'institutetype2', 'institutecategory2', 'university2', 'district2', 'location2', 'city2')
        
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)
        self.organiser2 = create_organiser(self.user2, self.academic2, self.group.name)

        self.year = 2018
        self.participant_count = 1
        self.department = Department.objects.create(name='department 1')
        self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year, self.participant_count)
        
        self.verified = 1

        self.student1 = create_student('Female', self.verified, self.user_stu.id)
        self.student_master = create_student_master(self.batch1.id, self.student1.id)

    # def test_denies_other_organiser(self):
    #     self.client.login(username=self.user2.username, password=self.user_pass)
    #     response = self.client.get(reverse('events:student_delete', 
    #         kwargs={'bid': self.batch1.id, 'pk': self.student_master.id}), follow=True)

    #     self.assertEqual(response.status_code, 404)
    
    def test_delete(self):
        self.client.login(username=self.user.username, password=self.user_pass)
        response = self.client.post(reverse('events:student_delete', 
            kwargs={'bid': self.batch1.id, 'pk': self.student_master.id}), follow=True)
        sm = StudentMaster.objects.filter(id=self.student_master.id)
        self.assertEquals(sm.count(), 0)

class TestStudentBatchUpdateView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')#organiser
        self.user_stu = create_user('student1', 'abcstu@gmail.com')#student
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user, self.state, 'IITB', 'institutetype1', 'MAH-001', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)

        self.year = 2018
        self.participant_count = 1
        self.department = Department.objects.create(name='department 1')
        self.department2 = Department.objects.create(name='department 123')
        self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year, self.participant_count)
        
    def test_denies_anonymous(self):
        response = self.client.get(reverse('events:edit_batch', 
            kwargs={'pk': self.batch1.id}), follow=True)
        redirect_url = 'accounts/login/?next=/software-training/student-batch/'+str(self.batch1.id)+'/'
        self.assertRedirects(response, redirect_url)

    def test_post_data(self):
        old_department = self.batch1.department.name
        old_year = self.year

        self.client.login(username=self.user.username, password=self.user_pass)

        response = self.client.post(reverse('events:edit_batch', 
            kwargs={'pk': self.batch1.id}),
            {'department':self.department2.id, 'year':2017},
            follow=True)
        print(response)


        sb = StudentBatch.objects.get(id=self.batch1.id)

        self.assertEquals(sb.department.name, self.department2.name)

class TestTrainingRequestCreateView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')#organiser
        self.user_stu = create_user('student1', 'abcstu@gmail.com')#student
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user, self.state, 'IITB', 'institutetype1', 'MAH-001', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)

        self.year = 2018
        self.participant_count = 1
        self.department = Department.objects.create(name='department 1')
        self.department2 = Department.objects.create(name='department 123')
        self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year, self.participant_count)
        
        self.verified = 1

        self.student1 = create_student('Female', self.verified, self.user_stu.id)
        self.student_master = create_student_master(self.batch1.id, self.student1.id)

        self.sem_odd, self.sem_even = create_sem()
        # self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')

        self.foss = FossCategory.objects.create(
            foss='foss1', description = 'testing',
            status=1, user=self.user
            )
        self.foss2 = FossCategory.objects.create(
            foss='foss2', description = 'testing',
            status=1, user=self.user
            )
        self.foss3 = FossCategory.objects.create(
            foss='foss3', description = 'testing',
            status=1, user=self.user
            )
        self.foss4 = FossCategory.objects.create(
            foss='foss4', description = 'testing',
            status=1, user=self.user
            )
        self.coursemap = CourseMap.objects.create(test=1, category=0, foss=self.foss)
        self.coursemap2 = CourseMap.objects.create(test=1, category=0, foss=self.foss2)
        self.coursemap3 = CourseMap.objects.create(test=1, category=0, foss=self.foss3)
        self.coursemap4 = CourseMap.objects.create(test=1, category=0, foss=self.foss4)

    def test_tr_planner(self):
        self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2016')
        self.client.login(username=self.user.username, password=self.user_pass)

        response = self.client.get(reverse('events:training_request', 
            kwargs={'tpid': self.tr_planner.id}), follow=True)
        redirect_destination = '/software-training/training-planner/'
        self.assertRedirects(response, redirect_destination)

    def test_post_form(self):
        self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')
        self.client.login(username=self.user.username, password=self.user_pass)
        
        response = self.client.post(reverse('events:training_request', 
            kwargs={'tpid': self.tr_planner.id}), 
            data={'department':self.department.id,
                  'batch':self.batch1.id,
                  'course_type':0,
                  'sem_start_date':date(2018, 7, 1),
                  'foss_category':1,
                  'course': self.coursemap.id,
                  'training_planner':self.tr_planner.id}, follow=True)

        self.tr = TrainingRequest.objects.get(training_planner_id=self.tr_planner.id)
        tr_count = TrainingRequest.objects.filter(training_planner_id=self.tr_planner.id).count()
        self.assertTrue(self.tr)
        self.assertEquals(tr_count, 1)

        response2 = self.client.post(reverse('events:training_request', 
            kwargs={'tpid': self.tr_planner.id}), 
            data={'department':self.department.id,
                  'batch':self.batch1.id,
                  'course_type':0,
                  'sem_start_date':date(2018, 7, 1),
                  'foss_category':1,
                  'course': self.coursemap2.id,
                  'training_planner':self.tr_planner.id}, follow=True)
        tr_count2 = TrainingRequest.objects.filter(training_planner_id=self.tr_planner.id).count()
        self.assertEquals(tr_count2, 2)

        response3 = self.client.post(reverse('events:training_request', 
            kwargs={'tpid': self.tr_planner.id}), 
            data={'department':self.department.id,
                  'batch':self.batch1.id,
                  'course_type':0,
                  'sem_start_date':date(2018, 7, 1),
                  'foss_category':1,
                  'course': self.coursemap3.id,
                  'training_planner':self.tr_planner.id}, follow=True)
        tr_count3 = TrainingRequest.objects.filter(training_planner_id=self.tr_planner.id).count()
        self.assertEquals(tr_count3, 3)

        #testing for college- it shuld not accept more than 3 training request per sem
        response4 = self.client.post(reverse('events:training_request', 
            kwargs={'tpid': self.tr_planner.id}), 
            data={'department':self.department.id,
                  'batch':self.batch1.id,
                  'course_type':0,
                  'sem_start_date':date(2018, 7, 1),
                  'foss_category':1,
                  'course': self.coursemap4.id,
                  'training_planner':self.tr_planner.id}, follow=True)
        tr_count4 = TrainingRequest.objects.filter(training_planner_id=self.tr_planner.id).count()
        self.assertEquals(tr_count4, 3)


    def test_denies_post_same_foss(self):
        self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')
        self.client.login(username=self.user.username, password=self.user_pass)

        response = self.client.post(reverse('events:training_request', 
            kwargs={'tpid': self.tr_planner.id}), 
            data={'department':self.department.id,
                  'batch':self.batch1.id,
                  'course_type':0,
                  'sem_start_date':date(2018, 7, 1),
                  'foss_category':1,
                  'course': self.coursemap2.id,
                  'training_planner':self.tr_planner.id}, follow=True)



        response2 = self.client.post(reverse('events:training_request', 
            kwargs={'tpid': self.tr_planner.id}), 
            data={'department':self.department.id,
                  'batch':self.batch1.id,
                  'course_type':0,
                  'sem_start_date':date(2018, 7, 1),
                  'foss_category':1,
                  'course': self.coursemap2.id,
                  'training_planner':self.tr_planner.id}, follow=True)
        
        tr_count = TrainingRequest.objects.filter(training_planner_id=self.tr_planner.id).count()
        self.assertEquals(tr_count, 1)

    # def test_next_sem_request(self):
    #     self.tr_planner = create_tr_planner(self.sem_even, self.academic, self.organiser, '2018')
    #     self.tr_planner2 = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')

    #     self.client.login(username=self.user.username, password=self.user_pass)

    #     response = self.client.post(reverse('events:training_request', 
    #         kwargs={'tpid': self.tr_planner.id}), 
    #         data={'department':self.department.id,
    #               'batch':self.batch1.id,
    #               'course_type':0,
    #               'sem_start_date':date(2019, 1, 5),
    #               'foss_category':1,
    #               'course': self.coursemap.id,
    #               'training_planner':self.tr_planner.id}, follow=True)

    #     tr_count = TrainingRequest.objects.filter(training_planner_id=self.tr_planner.id)
    #     self.assertEquals(tr_count.count(), 1)
    #     participants = TrainingRequest.objects.filter(training_planner_id=self.tr_planner.id).values('participants')
    #     self.assertEquals(participants,1)


class  TestTrainingAttendanceListView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('kirtist', 'abc@gmail.com')#organiser
        self.user_stu = create_user('student1', 'abcstu@gmail.com')#student
        self.user_pass = 'demo1'

        self.state = create_state('maharashtra')
        self.academic = create_academic(self.user, self.state, 'IITB', 'institutetype1', 'MAH-001', 'institutecategory', 'university1', 'mumbai', 'location1', 'mumbai')
        self.group = create_group('Organiser')
        self.organiser = create_organiser(self.user, self.academic, self.group.name)

        self.year = 2018
        self.participant_count = 1
        self.department = Department.objects.create(name='department 1')
        self.department2 = Department.objects.create(name='department 123')
        self.batch1 = create_batch(self.organiser, self.academic, self.department, self.year, self.participant_count)
        
        self.verified = 1

        self.student1 = create_student('Female', self.verified, self.user_stu.id)
        self.student_master = create_student_master(self.batch1.id, self.student1.id)

        self.sem_odd, self.sem_even = create_sem()
        # self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')

        self.foss = FossCategory.objects.create(
            foss='foss1', description = 'testing',
            status=1, user=self.user
            )
        
        self.coursemap = CourseMap.objects.create(test=1, category=0, foss=self.foss)

        self.tr_planner = create_tr_planner(self.sem_odd, self.academic, self.organiser, '2018')
       
    def test_post_form(self):
        self.client.login(username=self.user.username, password=self.user_pass)
        
        response = self.client.post(reverse('events:training_request', 
            kwargs={'tpid': self.tr_planner.id}), 
            data={'department':self.department.id,
                  'batch':self.batch1.id,
                  'course_type':0,
                  'sem_start_date':date(2018, 7, 1),
                  'foss_category':1,
                  'course': self.coursemap.id,
                  'training_planner':self.tr_planner.id}, follow=True)

        self.tr = TrainingRequest.objects.get(training_planner_id=self.tr_planner.id)
        tr_count = TrainingRequest.objects.filter(training_planner_id=self.tr_planner.id).count()
        self.assertTrue(self.tr)
        self.assertEquals(tr_count, 1)

        self.language = Language.objects.create(name='English', code='en', user=self.user)
        
        self.tr_attendance = create_training_attendance(self.tr, self.student1, self.language)
        self.assertEquals(self.tr_attendance.student, self.student1)
       #attendance view has to be tested here


