import os
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group, Permission
from events.models import Department, Student, State, District, City, ResourcePerson, University, InstituteCategory, 
InstituteType, Organiser, AcademicCenter
from spoken.forms import TestimonialsForm


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


class OrganiserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='kirtist')
        self.approved_by = 'nancy'
        self.academic = AcademicCenter.objects.create(institution_name='IITB')
        Organiser.objects.create(user=self.user, academic=self.academic, status=0)

    def test_organiser(self):
        # GIven
        status = 0
        


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