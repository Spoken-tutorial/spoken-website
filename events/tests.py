import os
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from spoken.forms import TestimonialsForm

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
        self.assertEqual(response.status_code, 403)
    

    def test_new_media_testimonial_no_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should redirect.
        """
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'tutorial'}))
        self.assertEqual(response.status_code, 403)
    
    
    def test_new_series_testimonial_no_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should redirect.
        """
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'series'}))
        self.assertEqual(response.status_code, 403)


    # Check status code with normal_user login
    def test_new_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should return page not found.
        """
        login = self.client.login(username='user_normal', password='atb00ker')
        response = self.client.get(reverse('testimonials_new'))
        self.assertEqual(response.status_code, 403)
    

    def test_new_media_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should return page not found.
        """
        login = self.client.login(username='user_normal', password='atb00ker')
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'tutorial'}))
        self.assertEqual(response.status_code, 403)
    
    
    def test_new_series_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should return page not found.
        """
        login = self.client.login(username='user_normal', password='atb00ker')
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'series'}))
        self.assertEqual(response.status_code, 403)


    # Check status code with administrator login
    def test_new_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should accept the request.
        """
        login = self.client.login(username='user_administrator', password='atb00ker')
        response = self.client.get(reverse('testimonials_new'))
        self.assertEqual(response.status_code, 200)
    

    def test_new_media_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should accept the request.
        """
        login = self.client.login(username='user_administrator', password='atb00ker')
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'tutorial'}))
        self.assertEqual(response.status_code, 200)
    
    
    def test_new_series_testimonial_normal_user(self):
        """
        Since only administrator is allowed to 
        create new testimonials, this should accept the request.
        """
        login = self.client.login(username='user_administrator', password='atb00ker')
        response = self.client.get(reverse('testimonials_new_media',kwargs={'type':'series'}))
        self.assertEqual(response.status_code, 200)
    
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