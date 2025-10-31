import os

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

from .models import TutorialPayment
from .views import money_as_text


class PaymentTestClass(TestCase):

    @classmethod
    def setUpTestData(self):
        """
        Create class level data which will stay for all method
        """
        user_qr = User.objects.create_user(
            username='user_quality_reviewer',
            password='pass1234'
        )
        qr_group = Group.objects.create(name="Quality-Reviewer")
        qr_group.user_set.add(user_qr)
        user_normal = User.objects.create_user(
            username='user_normal',
            password='pass1234'
        )

    def test_due_tutorial_url_for_no_user(self):
        """
            due tutorials list link is
            reirects for non logged in user
        """
        response = self.client.get(reverse('creation:payment_due_tutorials'))
        self.assertEquals(response.status_code, 302)

    def test_due_tutorial_url_for_normal_user(self):
        """
            due tutorial denies oermission for normal user
        """
        login = self.client.login(username='user_normal', password='pass1234')
        response = self.client.get(reverse('creation:payment_due_tutorials'))
        self.assertEquals(response.status_code, 403)

    def test_due_tutorial_url_for_quality_reviewer(self):
        """
            due tutorial rendering for quality reviewer
        """
        login = self.client.login(
            username='user_quality_reviewer',
            password='pass1234'
        )
        response = self.client.get(reverse('creation:payment_due_tutorials'))
        self.assertEquals(response.status_code, 200)

    def test_payment_honorarium_list_for_no_user(self):
        """
            payment honorarium list redirect no login user
        """
        response = self.client.get(
            reverse('creation:payment_honorarium_list')
        )
        self.assertEquals(response.status_code, 302)

    def test_payment_honorarium_list_for_normal_user(self):
        """
            payment honorarium list permission denied no normal user
        """
        login = self.client.login(username='user_normal', password='pass1234')
        response = self.client.get(
            reverse('creation:payment_honorarium_list')
        )
        self.assertEquals(response.status_code, 403)

    def test_payment_honorarium_list_for_quality_reviewer(self):
        """
            payment honorarium list rendering for quality reviewer
        """
        login = self.client.login(
            username='user_quality_reviewer',
            password='pass1234'
        )
        response = self.client.get(reverse('creation:payment_honorarium_list'))
        self.assertEquals(response.status_code, 200)

    def test_payment_honorarium_detail_for_no_user(self):
        """
            payment honorarium list redirect no login user
        """
        response = self.client.get(
            reverse('creation:payment_honorarium_detail', args=(1,))
        )
        self.assertEquals(response.status_code, 302)

    def test_payment_honorarium_detail_for_normal_user(self):
        """
            payment honorarium list 404 for normal user
        """
        login = self.client.login(username='user_normal', password='pass1234')
        response = self.client.get(
            reverse('creation:payment_honorarium_detail', args=(1,))
        )
        self.assertEquals(response.status_code, 404)

    # Test for money_as_text function
    def test_money_as_text_for_negative_value(self):
        res = money_as_text(-4.00)
        self.assertEquals(res, "Invalid Amount")

    def test_money_as_text_for_zero_value(self):
        res = money_as_text(0.00)
        self.assertEquals(res, "Invalid Amount")

    def test_money_as_text_for_large_value(self):
        """
        testing for amount larger than 1lakh
        """
        res = money_as_text(987654.00)
        self.assertEquals(res, "Invalid Amount")

    def test_money_as_text_for_integer_value(self):
        """
        testing for only integer value
        """
        res = money_as_text(13579)
        self.assertEquals(
            res,
            "Thirteen Thousand Five Hundred Seventy Nine Only"
        )

    def test_money_as_text_for_normal_value(self):
        res = money_as_text(97531.48)
        self.assertEquals(
            res,
            "Ninety Seven Thousand Five Hundred Thirty One And Forty Eight Paise Only"
        )

    def test_hr_receipt_template_file_exists(self):
        """
            Template for honorarium receipt generation exist
        """
        res = os.path.isfile(
            'media/hr-receipts/honorarium-receipt-template.docx'
        )
        self.assertTrue(res)
