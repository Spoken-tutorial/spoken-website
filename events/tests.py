import os
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group, Permission
from creation.models import *
from events.models import *
# from events.models import Department, Student, State, District, City, ResourcePerson, University, InstituteCategory, 
# InstituteType, Organiser, AcademicCenter
from spoken.forms import TestimonialsForm
from datetime import datetime, date



def tearDownModule():
    User.objects.all().delete()
    Department.objects.all().delete()
    State.objects.all().delete()
    District.objects.all().delete()
    City.objects.all().delete()
    ResourcePerson.objects.all().delete()
    University.objects.all().delete()
    InstituteCategory.objects.all().delete()
    InstituteType.objects.all().delete()
    
    AcademicCenter.objects.all().delete()
    Student.objects.all().delete()
    


class DepartmentTestCase(TestCase):
    def setUp(self):
        Department.objects.create(name='Testcase Department 1')

    def test_department(self):
        # Given
        department_name = 'Testcase Department 1' 
        # When
        department = Department.objects.get(name='Testcase Department 1')
        # Then
        self.assertEqual(department.name, department_name)


class DistrictTestCase(TestCase):
    def setUp(self):
        self.state = State.objects.create(name='maharashtra')
        District.objects.create(state=self.state, name='mumbai')

    def test_district(self):
        # Given
        name = 'mumbai'
        # When
        district = District.objects.get(state=self.state)
        # Then
        self.assertEquals(self.state, district.state)
        self.assertEquals(name, district.name)


class CityTestCase(TestCase):
    def setUp(self):
        self.state = State.objects.create(name='maharashtra')
        City.objects.create(state=self.state, name='mumbai')

    def test_city(self):
        # Given
        name = 'mumbai'
        # When
        city = City.objects.get(state=self.state)
        # Then
        self.assertEquals(self.state, city.state)
        self.assertEquals(name, city.name)


class ResourcePersonTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirtist')
        self.state = State.objects.create(name='maharashtra')
        ResourcePerson.objects.create(user=self.user, state=self.state, status=0, assigned_by=1)

    def test_rp(self):
        # Given
        status = 0
        assigned_by = 1
        # When
        rp = ResourcePerson.objects.get(state=self.state)
        # Then
        # self.assertEquals(self.state, rp.state)
        self.assertEquals(status, rp.status)
        self.assertEquals(assigned_by, rp.assigned_by)


class UniversityTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirtist')
        self.state = State.objects.create(name='maharashtra')
        University.objects.create(state=self.state, name='IITB', user=self.user)

    def test_university(self):
        # Given
        name = 'IITB'
        # When
        university = University.objects.get(state=self.state)
        # Then
        self.assertEquals(self.state, university.state)
        self.assertEquals(name, university.name)


class InstituteCategoryTestCase(TestCase):
    def setUp(self):
        InstituteCategory.objects.create(name='InstituteCategory 1')

    def test_institutecategory(self):
        # Given
        institutecategory_name = 'InstituteCategory 1' 
        # When
        institutecategory = InstituteCategory.objects.get(name='InstituteCategory 1')
        # Then
        self.assertEqual(institutecategory.name, institutecategory_name)


class InstituteTypeTestCase(TestCase):
    def setUp(self):
        InstituteType.objects.create(name='InstituteType 1')

    def test_InstituteType(self):
        # Given
        institutetype_name = 'InstituteType 1' 
        # When
        institutetype = InstituteType.objects.get(name='InstituteType 1')
        # Then
        self.assertEqual(institutetype.name, institutetype_name)


class AcademicTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirtist1')
        self.state = State.objects.create(name='maharashtra')
        self.institutetype = InstituteType.objects.create(name='InstituteType 1')
        self.institutecategory = InstituteCategory.objects.create(name='InstituteCategory 1')
        self.university = University.objects.create(state=self.state, name='Mumbai University', user=self.user)
        self.institution_name = 'IITB'
        self.district = District.objects.create(state=self.state, name='mumbai')
        self.location = Location.objects.create(district=self.district, name='location 1', pincode=400075)
        self.city = City.objects.create(state=self.state, name='mumbai')
        self.status = 0
        self.pincode = 400075
        self.resource_center = 'IIT Powai'
        self.rating = 1
        self.contact_person = 'ABC'
        self.remarks = 'Good'
        AcademicCenter.objects.create(
            user=self.user, state=self.state, institution_type=self.institutetype,
            institute_category=self.institutecategory,
            university=self.university,
            institution_name=self.institution_name,
            district=self.district,
            location=self.location,
            city=self.city,
            status=0,
            pincode=self.pincode,
            resource_center=self.resource_center,
            contact_person=self.contact_person,
            rating=self.rating,
            remarks=self.remarks
            )
    def test_academic(self):
        # Given
        status=0
        institution_name = 'IITB'
        # When
        academic = AcademicCenter.objects.get(user=self.user, institution_name=self.institution_name)
        # Then
        self.assertEquals(self.user, academic.user)
        self.assertEquals(institution_name, academic.institution_name)

    def test_get_training_count(self):
        #given
        count = 0
        #when
        academic = AcademicCenter.objects.get(institution_name=self.institution_name)
        #then
        self.assertEquals(count, academic.get_training_count())

    def test_get_training_participant_count(self):
        #given
        sum = None
        #when
        academic = AcademicCenter.objects.get(institution_name=self.institution_name)
        #then
        self.assertEquals(sum, academic.get_training_participant_count())


class TestTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirti')
        self.user1 = User.objects.create(username='nancy')
        
        self.test_category = TestCategory.objects.create(name='Lab Hours')
        self.appoved_by = self.user

        self.state = State.objects.create(name='maharashtra')
        self.institutetype = InstituteType.objects.create(name='InstituteType 1')
        self.institutecategory = InstituteCategory.objects.create(name='InstituteCategory 1')
        self.university = University.objects.create(state=self.state, name='Mumbai University', user=self.user)
        self.institution_name = 'IITB'
        self.district = District.objects.create(state=self.state, name='mumbai')
        self.location = Location.objects.create(district=self.district, name='location 1', pincode=400075)
        self.city = City.objects.create(state=self.state, name='mumbai')
        self.status = 0
        self.pincode = 400075
        self.resource_center = 'IIT Powai'
        self.rating = 1
        self.contact_person = 'ABC'
        self.remarks = 'Good'
        self.academic = AcademicCenter.objects.create(
            user=self.user, state=self.state, 
            institution_type=self.institutetype,
            institute_category=self.institutecategory,
            university=self.university,
            institution_name=self.institution_name,
            district=self.district,
            location=self.location,
            city=self.city,
            status=0,
            pincode=self.pincode,
            resource_center=self.resource_center,
            contact_person=self.contact_person,
            rating=self.rating,
            remarks=self.remarks
            )
        self.organiser = Organiser.objects.create(user=self.user)
        self.invigilator = Invigilator.objects.create(user=self.user1, academic=self.academic)
        self.foss = FossCategory.objects.create(
            foss='foss1', description = 'test',
            status=0, user=self.user
            )
        self.test_code = 'TC-001'
        self.tdate = '2018-11-11'
        self.ttime = '12:00:00'

        Test.objects.create(organiser=self.organiser,
            test_category=self.test_category,
            invigilator=self.invigilator,
            academic=self.academic,
            foss=self.foss,
            test_code=self.test_code,
            tdate=self.tdate,
            ttime=self.ttime,
            )

    def test_test(self):
        #given
        test_code = 'TC-001'
        #when
        test = Test.objects.get(test_code=self.test_code)
        test1 = Test.objects.get(tdate=self.tdate)
        #then
        self.assertEquals(test.test_code, test_code)
    
    def test_get_test_attendance_count(self):
        #given
        attendance_count = 0
        #when
        test = Test.objects.get(test_code=self.test_code)
        #then
        self.assertEquals(test.get_test_attendance_count(), attendance_count)

    def test_update_test_participant_count(self):
        #given
        attendance_count = 0
        #when
        test = Test.objects.get(test_code=self.test_code)
        test.update_test_participant_count()
        #then
        self.assertEquals(test.participant_count, attendance_count)

class TestAttendancetestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirti')
        self.user1 = User.objects.create(username='nancy')
        self.user2 = User.objects.create(username='student1')
        
        self.test_category = TestCategory.objects.create(name='Lab Hours')
        self.appoved_by = self.user

        self.state = State.objects.create(name='maharashtra')
        self.institutetype = InstituteType.objects.create(name='InstituteType 1')
        self.institutecategory = InstituteCategory.objects.create(name='InstituteCategory 1')
        self.university = University.objects.create(state=self.state, name='Mumbai University', user=self.user)
        self.institution_name = 'IITB'
        self.district = District.objects.create(state=self.state, name='mumbai')
        self.location = Location.objects.create(district=self.district, name='location 1', pincode=400075)
        self.city = City.objects.create(state=self.state, name='mumbai')
        self.status = 0
        self.pincode = 400075
        self.resource_center = 'IIT Powai'
        self.rating = 1
        self.contact_person = 'ABC'
        self.remarks = 'Good'
        self.academic = AcademicCenter.objects.create(
            user=self.user, state=self.state, 
            institution_type=self.institutetype,
            institute_category=self.institutecategory,
            university=self.university,
            institution_name=self.institution_name,
            district=self.district,
            location=self.location,
            city=self.city,
            status=0,
            pincode=self.pincode,
            resource_center=self.resource_center,
            contact_person=self.contact_person,
            rating=self.rating,
            remarks=self.remarks
            )
        self.organiser = Organiser.objects.create(user=self.user)
        self.invigilator = Invigilator.objects.create(user=self.user1, academic=self.academic)
        self.foss = FossCategory.objects.create(
            foss='foss1', description = 'test',
            status=0, user=self.user
            )
        self.test_code = 'TC-001'
        self.tdate = '2018-11-11'
        self.ttime = '12:00:00'

        self.test = Test.objects.create(organiser=self.organiser,
            test_category=self.test_category,
            invigilator=self.invigilator,
            academic=self.academic,
            foss=self.foss,
            test_code=self.test_code,
            tdate=self.tdate,
            ttime=self.ttime,
            )
        self.student = Student.objects.create(user=self.user2, gender='Female')
        self.mdluser_firstname = 'student_fname'
        self.mdluser_lastname = 'student_lname'
        self.mdluserid = 1
        TestAttendance.objects.create(test=self.test, student=self.student,
            mdluser_firstname=self.mdluser_firstname,
            mdluser_lastname=self.mdluser_lastname,
            mdluser_id=self.mdluserid)

    def test_testattendance(self):
        #given
        test_code = self.test_code
        #when
        testattendance = TestAttendance.objects.get(test=self.test)
        #then
        self.assertEquals(testattendance.student, self.student)

class FossMdlCoursesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirtist')
        self.foss = FossCategory.objects.create(
            foss='foss1', description = 'testing',
            status=0, user=self.user
            )
        self.mdlcourse_id = 1
        self.mdlquiz_id = 11
        FossMdlCourses.objects.create(foss=self.foss, mdlcourse_id=self.mdlcourse_id, mdlquiz_id=self.mdlquiz_id)

    def test_fossmdlcourses(self):
        #given
        foss = 'foss1'
        #when
        fossmdlcourse = FossMdlCourses.objects.get(foss=foss)
        #then
        self.assertEquals(fossmdlcourse.mdlquiz_id, self.mdlquiz_id)



class StudentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirtist')
        Student.objects.create(user=self.user, gender='Female')

    def test_student(self):
        # Given
        gender = 'Female'
        # When
        student = Student.objects.get(user=self.user)
        # Then
        self.assertEquals(self.user, student.user)
        self.assertEquals(gender, student.gender)

    def test_student_fullname(self):
        # Given
        fullname = 'kirtist'
        # When
        student = Student.objects.get(user=self.user)
        # Then
        self.assertEquals(student.student_fullname(), fullname)

    def test_is_student_has_attendance(self):
        # Given
        # When
        student = Student.objects.get(user=self.user)
        # Then
        self.assertTrue(student.is_student_has_attendance())


class StudentbatchTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirtist1')
        self.user1 = User.objects.create(username='nancy')
        self.state = State.objects.create(name='maharashtra')
        self.institutetype = InstituteType.objects.create(name='InstituteType 1')
        self.institutecategory = InstituteCategory.objects.create(name='InstituteCategory 1')
        self.university = University.objects.create(state=self.state, name='Mumbai University', user=self.user)
        self.institution_name = 'IITB'
        self.district = District.objects.create(state=self.state, name='mumbai')
        self.location = Location.objects.create(district=self.district, name='location 1', pincode=400075)
        self.city = City.objects.create(state=self.state, name='mumbai')
        self.status = 0
        self.pincode = 400075
        self.resource_center = 'IIT Powai'
        self.rating = 1
        self.contact_person = 'ABC'
        self.remarks = 'Good'
        self.academic = AcademicCenter.objects.create(
            user=self.user, state=self.state, institution_type=self.institutetype,
            institute_category=self.institutecategory,
            university=self.university,
            institution_name=self.institution_name,
            district=self.district,
            location=self.location,
            city=self.city,
            status=0,
            pincode=self.pincode,
            resource_center=self.resource_center,
            contact_person=self.contact_person,
            rating=self.rating,
            remarks=self.remarks
            )
        self.organiser = Organiser.objects.create(user=self.user, academic=self.academic)
        self.organiser1 = Organiser.objects.create(user=self.user1)
        self.department = Department.objects.create(name='department 1')
        self.year = 2018
        StudentBatch.objects.create(academic=self.academic,
            organiser=self.organiser, department=self.department, year=self.year)
        self.coursemapid=101
    
    def  test_studentbatch(self):
        #given
        year = 2018
        #when
        sb = StudentBatch.objects.get(year=year)
        #then
        self.assertEquals(sb.organiser, self.organiser)

    def test_student_count(self):
        #given
        count=0
        #when
        sb = StudentBatch.objects.get(organiser=self.organiser)
        #then
        self.assertEquals(sb.student_count(), count)

    def test_can_add_student(self):
        #given
        organiser = self.organiser1
        #when
        sb = StudentBatch.objects.get(department=self.department)
        #then
        self.assertFalse(sb.can_add_student(organiser.id))

    def test_update_student_count(self):
        #given
        stcount = 0
        #when
        sb = StudentBatch.objects.get(department=self.department)
        sb.update_student_count()
        #then
        self.assertEquals(sb.stcount, stcount)

    def test_is_foss_batch_acceptable(self):
        #given
        #when
        sb = StudentBatch.objects.get(department=self.department)
        #then
        self.assertFalse(sb.is_foss_batch_acceptable(self.coursemapid))

    def test_has_training(self):
        #given
        #when
        sb = StudentBatch.objects.get(department=self.department)
        #then
        self.assertTrue(sb.has_training())

class StudentMasterTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirtist1')
        self.user1 = User.objects.create(username='nancy')
        self.state = State.objects.create(name='maharashtra')
        self.institutetype = InstituteType.objects.create(name='InstituteType 1')
        self.institutecategory = InstituteCategory.objects.create(name='InstituteCategory 1')
        self.university = University.objects.create(state=self.state, name='Mumbai University', user=self.user)
        self.institution_name = 'IITB'
        self.district = District.objects.create(state=self.state, name='mumbai')
        self.location = Location.objects.create(district=self.district, name='location 1', pincode=400075)
        self.city = City.objects.create(state=self.state, name='mumbai')
        self.status = 0
        self.pincode = 400075
        self.resource_center = 'IIT Powai'
        self.rating = 1
        self.contact_person = 'ABC'
        self.remarks = 'Good'
        self.academic = AcademicCenter.objects.create(
            user=self.user, state=self.state, institution_type=self.institutetype,
            institute_category=self.institutecategory,
            university=self.university,
            institution_name=self.institution_name,
            district=self.district,
            location=self.location,
            city=self.city,
            status=0,
            pincode=self.pincode,
            resource_center=self.resource_center,
            contact_person=self.contact_person,
            rating=self.rating,
            remarks=self.remarks
            )
        self.organiser = Organiser.objects.create(user=self.user, academic=self.academic)
        self.department = Department.objects.create(name='department 1')
        self.year = 2018
        self.batch = StudentBatch.objects.create(academic=self.academic,
            organiser=self.organiser, department=self.department, year=self.year)
        self.student = Student.objects.create(user=self.user1, gender='Female')
        StudentMaster.objects.create(batch=self.batch, student=self.student)

    def test_studentmaster(self):
        #given
        #when
        studentmaster = StudentMaster.objects.get(batch=self.batch)
        #then
        self.assertFalse(studentmaster.is_student_has_attendance())

class SemestertestCase(TestCase):
    def setUp(self):
        self.name = 'Odd'
        Semester.objects.create(name=self.name)

    def test_sem(self):
        #given
        name = 'Odd'
        #when
        sem = Semester.objects.get(name=name)
        #then
        self.assertEquals(sem.name, name)

class CourseMapTestcase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirtist')
        self.foss = FossCategory.objects.create(
            foss='foss1', description = 'testing',
            status=0, user=self.user
            )
        CourseMap.objects.create(foss=self.foss)

    def test_coursemap(self):
        #given
        foss = 'foss1'
        #when
        coursemap = CourseMap.objects.get(foss=self.foss)
        #then
        self.assertEquals(coursemap.foss.foss, foss)

    def test_course_name(self):
        #given
        foss = 'foss1'
        #when
        coursemap = CourseMap.objects.get(foss=self.foss)
        #then
        name = coursemap.course_name()
        self.assertEquals(name, coursemap.foss)

class TrainingPlannerTestCase(TestCase):
    def setUp(self):
        self.year = '2018'
        self.user = User.objects.create(username='kirtist1')
        self.state = State.objects.create(name='maharashtra')
        self.institutetype = InstituteType.objects.create(name='InstituteType 1')
        self.institutecategory = InstituteCategory.objects.create(name='InstituteCategory 1')
        self.university = University.objects.create(state=self.state, name='Mumbai University', user=self.user)
        self.institution_name = 'IITB'
        self.district = District.objects.create(state=self.state, name='mumbai')
        self.location = Location.objects.create(district=self.district, name='location 1', pincode=400075)
        self.city = City.objects.create(state=self.state, name='mumbai')
        self.status = 0
        self.pincode = 400075
        self.resource_center = 'IIT Powai'
        self.rating = 1
        self.contact_person = 'ABC'
        self.remarks = 'Good'
        self.academic = AcademicCenter.objects.create(
            user=self.user, state=self.state, institution_type=self.institutetype,
            institute_category=self.institutecategory,
            university=self.university,
            institution_name=self.institution_name,
            district=self.district,
            location=self.location,
            city=self.city,
            status=0,
            pincode=self.pincode,
            resource_center=self.resource_center,
            contact_person=self.contact_person,
            rating=self.rating,
            remarks=self.remarks
            )
        self.name = 'Odd'
        self.semester = Semester.objects.create(name=self.name, even=False)
        self.organiser = Organiser.objects.create(user=self.user, academic=self.academic)
        
        self.department = Department.objects.create(name='department 1')
        self.batch = StudentBatch.objects.create(academic=self.academic,
            organiser=self.organiser, department=self.department, year=self.year)

        TrainingPlanner.objects.create(year=self.year, academic=self.academic, 
            organiser=self.organiser, semester=self.semester)
        

    def test_trplanner(self):
        #given
        year = '2018'
        #when
        trplanner = TrainingPlanner.objects.get(year=year)
        #then
        self.assertEquals(trplanner.year, year)
        self.assertEquals(trplanner.organiser, self.organiser)

    # def test_training_requests(self):
    #     #given
    #     year = '2018'
    #     tr_request = []
    #     tr = TrainingRequest.objects.all()
    #     #WHEN
    #     trplanner = TrainingPlanner.objects.get(year=year)
    #     #then
    #     self.assertEquals(trplanner.training_requests(), tr)

    def test_get_semester(self):
        #given
        year = 2018
        sem_name = 'July - December, 2018'
        #when
        trplanner = TrainingPlanner.objects.get(year=year)
        #then
        self.assertEquals(trplanner.get_semester(), sem_name)

    def test_get_current_year_and_sem(self):
        #given
        year1 = 2018
        sem = self.semester
        #when
        trplanner = TrainingPlanner.objects.get(year=year1)
        #then
        self.assertEquals(trplanner.get_current_year_and_sem(), (year1, sem))

    def test_completed_training(self):
        #given
        year = 2018
        tr = []
        #when
        trplanner = TrainingPlanner.objects.get(year=year)
        #then
        self.assertEquals(list(trplanner.completed_training()), tr)

    def test_ongoing_training(self):
        #given
        year = 2018
        tr = []
        #when
        trplanner = TrainingPlanner.objects.get(year=year)
        #then
        self.assertEquals(list(trplanner.ongoing_training()), tr)

    def test_is_full(self):
        #given
        year= 2018
        #when
        trplanner = TrainingPlanner.objects.get(year=year)
        #then
        self.assertFalse(trplanner.is_full(self.department.id, self.batch.id))

    def test_is_school_full(self):
        #given
        year= 2018
        #when
        trplanner = TrainingPlanner.objects.get(year=year)
        #then
        self.assertFalse(trplanner.is_school_full(self.department.id, self.batch.id))

    def test_get_current_semester_date_duration(self):
        #given
        duration = (date(2018, 7, 1), date(2018, 12, 31))
        #when
        trplanner = TrainingPlanner.objects.get(year=self.year)
        #then
        self.assertEquals(trplanner.get_current_semester_date_duration(), duration)

    def test_get_current_semester_date_duration_new(self):
        #given
        duration = (date(2018, 7, 1), date(2018, 9, 30))
        #when
        trplanner = TrainingPlanner.objects.get(year=self.year)
        #then
        self.assertEquals(trplanner.get_current_semester_date_duration_new(), duration)

class TrainingRequestTestCase(TestCase):
    def setUp(self):
        self.year = '2018'
        self.user = User.objects.create(username='kirtist1')
        self.state = State.objects.create(name='maharashtra')
        self.institutetype = InstituteType.objects.create(name='InstituteType 1')
        self.institutecategory = InstituteCategory.objects.create(name='InstituteCategory 1')
        self.university = University.objects.create(state=self.state, name='Mumbai University', user=self.user)
        self.institution_name = 'IITB'
        self.district = District.objects.create(state=self.state, name='mumbai')
        self.location = Location.objects.create(district=self.district, name='location 1', pincode=400075)
        self.city = City.objects.create(state=self.state, name='mumbai')
        self.status = 0
        self.pincode = 400075
        self.resource_center = 'IIT Powai'
        self.rating = 1
        self.contact_person = 'ABC'
        self.remarks = 'Good'
        self.academic = AcademicCenter.objects.create(
            user=self.user, state=self.state, institution_type=self.institutetype,
            institute_category=self.institutecategory,
            university=self.university,
            institution_name=self.institution_name,
            district=self.district,
            location=self.location,
            city=self.city,
            status=0,
            pincode=self.pincode,
            resource_center=self.resource_center,
            contact_person=self.contact_person,
            rating=self.rating,
            remarks=self.remarks
            )
        self.name = 'Odd'
        self.semester = Semester.objects.create(name=self.name, even=False)
        self.organiser = Organiser.objects.create(user=self.user, academic=self.academic)
        
        self.department = Department.objects.create(name='department 1')
        self.batch = StudentBatch.objects.create(academic=self.academic,
            organiser=self.organiser, department=self.department, year=self.year)

        self.trplanner = TrainingPlanner.objects.create(year=self.year, academic=self.academic, 
            organiser=self.organiser, semester=self.semester)
        self.sem_start_date = '2018-07-10'
        self.foss = FossCategory.objects.create(
            foss='foss1', description = 'testing',
            status=0, user=self.user
            )
        self.coursemap = CourseMap.objects.create(foss=self.foss)
        TrainingRequest.objects.create(training_planner=self.trplanner,
            department=self.department, sem_start_date=self.sem_start_date,
            course=self.coursemap, batch=self.batch)

    def test_trainingrequest(self):
        #given
        trp = self.trplanner
        #when
        tr = TrainingRequest.objects.get(training_planner=trp)
        #then
        self.assertEquals(tr.batch, self.batch)

    def test_get_course_type(self):
        #given
        course_type = 'Outside Lab Hours'
        #when
        tr = TrainingRequest.objects.get(training_planner=self.trplanner)
        #then
        self.assertEquals(tr.get_course_type(), course_type)

    def test_is_learners_allowed(self):
        tr = TrainingRequest.objects.get(training_planner=self.trplanner)
        self.assertFalse(tr.is_learners_allowed())

    def test_have_test(self):
        tr = TrainingRequest.objects.get(training_planner=self.trplanner)
        self.assertFalse(tr.have_test())

    def test_is_training_before_july2017(self):
        #given
        sem_start_date = date(2018, 7, 10)
        #when
        tr = TrainingRequest.objects.get(training_planner=self.trplanner)
        #then
        self.assertEquals(tr.sem_start_date, sem_start_date)
        self.assertFalse(tr.is_training_before_july2017())

    def test_is_certificate_not_allowed(self):
        #given
        tr = TrainingRequest.objects.get(training_planner=self.trplanner)
        self.assertFalse(tr.is_certificate_not_allowed())

    def test_can_mark_attendance(self):
        tr = TrainingRequest.objects.get(training_planner=self.trplanner)
        self.assertTrue(tr.can_mark_attendance())

    def test_update_participants_count(self):
        #given
        count = 0
        #when
        tr = TrainingRequest.objects.get(training_planner=self.trplanner)
        #then
        self.assertEquals(tr.update_participants_count(), count)

    def test_get_partipants_from_attendance(self):
        #given
        count = 0
        #when
        tr = TrainingRequest.objects.get(training_planner=self.trplanner)
        #then
        self.assertEquals(tr.get_partipants_from_attendance(), count)

    # def test_attendance_summery(self):
    #     #when
    #     tr = TrainingRequest.objects.get(training_planner=self.trplanner)

    def test_can_edit(self):
        #when
        tr = TrainingRequest.objects.get(training_planner=self.trplanner)
        self.assertTrue(tr.can_edit())

    def test_training_name(self):
        tr = TrainingRequest.objects.get(training_planner=self.trplanner)
        name = 'WC-'+str(tr.id)+', foss1, department 1, 2018 Batch - 2018 - 2019'
        # WC-82, foss1, department 1, 2018 Batch - 2018 - 2019
        self.assertEquals(tr.training_name(), name)


class TrainingAttendTestcase(TestCase):
    self.year = '2018'
        self.user = User.objects.create(username='kirtist1')
        self.state = State.objects.create(name='maharashtra')
        self.institutetype = InstituteType.objects.create(name='InstituteType 1')
        self.institutecategory = InstituteCategory.objects.create(name='InstituteCategory 1')
        self.university = University.objects.create(state=self.state, name='Mumbai University', user=self.user)
        self.institution_name = 'IITB'
        self.district = District.objects.create(state=self.state, name='mumbai')
        self.location = Location.objects.create(district=self.district, name='location 1', pincode=400075)
        self.city = City.objects.create(state=self.state, name='mumbai')
        self.status = 0
        self.pincode = 400075
        self.resource_center = 'IIT Powai'
        self.rating = 1
        self.contact_person = 'ABC'
        self.remarks = 'Good'
        self.academic = AcademicCenter.objects.create(
            user=self.user, state=self.state, institution_type=self.institutetype,
            institute_category=self.institutecategory,
            university=self.university,
            institution_name=self.institution_name,
            district=self.district,
            location=self.location,
            city=self.city,
            status=0,
            pincode=self.pincode,
            resource_center=self.resource_center,
            contact_person=self.contact_person,
            rating=self.rating,
            remarks=self.remarks
            )
        self.name = 'Odd'
        self.semester = Semester.objects.create(name=self.name, even=False)
        self.organiser = Organiser.objects.create(user=self.user, academic=self.academic)
        
        self.department = Department.objects.create(name='department 1')
        self.batch = StudentBatch.objects.create(academic=self.academic,
            organiser=self.organiser, department=self.department, year=self.year)

        self.trplanner = TrainingPlanner.objects.create(year=self.year, academic=self.academic, 
            organiser=self.organiser, semester=self.semester)
        self.sem_start_date = '2018-07-10'
        self.foss = FossCategory.objects.create(
            foss='foss1', description = 'testing',
            status=0, user=self.user
            )
        self.coursemap = CourseMap.objects.create(foss=self.foss)
        self.tr = TrainingRequest.objects.create(training_planner=self.trplanner,
            department=self.department, sem_start_date=self.sem_start_date,
            course=self.coursemap, batch=self.batch)
        self.lang_name = 'English'
        self.language = Language.objects.create(name=self.lang_name, user=self.user, code=self.code)
        TrainingAttend.objects.create(training=self.tr, student=self.student, language=self.language)



















####################### testimonial test case ##############################################
class TestimonialTestClass(TestCase):
    '''
    This class contains test cases for audio / 
    video / text testimonial pages.
    '''

    @classmethod
    def setUpTestData(self):
        """
        Function creates elements required during testing
        this function is executed only once.
        """
        user_administrator = User.objects.create_user(
            username='user_administrator',
            password='atb00ker'
        )
        adminuser_permission = Permission.objects.get(name='Can add testimonials')
        user_administrator.user_permissions.add(adminuser_permission)
       
        user_normal = User.objects.create_user(
            username='user_normal',
            password='atb00ker'
        )

    # Check status code with no login
    def test_new_testimonial_no_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should redirect.
        """
        response = self.client.get(reverse('testimonials_new'))
        self.assertEquals(response.status_code, 403)
    

    def test_new_media_testimonial_no_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should redirect.
        """
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'tutorial'}))
        self.assertEquals(response.status_code, 403)
    
    
    def test_new_series_testimonial_no_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should redirect.
        """
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'series'}))
        self.assertEquals(response.status_code, 403)


    # Check status code with normal_user login
    def test_new_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should return page not found.
        """
        login = self.client.login(username='user_normal', password='atb00ker')
        response = self.client.get(reverse('testimonials_new'))
        self.assertEquals(response.status_code, 403)
    

    def test_new_media_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should return page not found.
        """
        login = self.client.login(username='user_normal', password='atb00ker')
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'tutorial'}))
        self.assertEquals(response.status_code, 403)
    
    
    def test_new_series_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should return page not found.
        """
        login = self.client.login(username='user_normal', password='atb00ker')
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'series'}))
        self.assertEquals(response.status_code, 403)


    # Check status code with administrator login
    def test_new_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should accept the request.
        """
        login = self.client.login(username='user_administrator', password='atb00ker')
        response = self.client.get(reverse('testimonials_new'))
        self.assertEquals(response.status_code, 200)
    

    def test_new_media_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should accept the request.
        """
        login = self.client.login(username='user_administrator', password='atb00ker')
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'tutorial'}))
        self.assertEquals(response.status_code, 200)
    
    
    def test_new_series_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should accept the request.
        """
        login = self.client.login(username='user_administrator', password='atb00ker')
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'series'}))
        self.assertEquals(response.status_code, 200)
    
    # TestimonialsForm Test Case
    def test_testimonialform_valid(self):
        # Fill fields
        source_title = 'Title Message'
        source_link = 'https://www.spoken-tutorials.org'
        status = True
        short_description = 'This field is required.'
        actual_content = 'This field is required.'
        user_name = 'This field is required.'
        minified_content = 'This field is required.'
        # Create form and check validity
        form_data = {
            'source_title': source_title,
            'source_link': source_link,
            'status': status,
            'short_description': short_description,
            'actual_content': actual_content,
            'user_name': user_name,
            'minified_content': minified_content,
        }
        form = TestimonialsForm(data=form_data)
        self.assertTrue(form.is_valid())