# Third Party Stuff
from django.db import models

events = (
    ('DCM', 'DrupalCamp Mumbai'),
    ('DRP', 'Drupal Workshop'),
)


class Event(models.Model):
    purpose = models.CharField(max_length=25, choices=events)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    # other details


class Certificate(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50, null=True, blank=True)
    serial_no = models.CharField(max_length=50)  # purpose+uin+1stletter
    counter = models.IntegerField()
    workshop = models.CharField(max_length=100, null=True, blank=True)
    paper = models.CharField(max_length=100, null=True, blank=True)
    verified = models.IntegerField(default=0)
    serial_key = models.CharField(max_length=200, null=True)
    short_key = models.CharField(max_length=50, null=True)


class FeedBack(models.Model):
    ''' Feed back form for the event '''
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    institution = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    pin_number = models.CharField(max_length=10)
    state = models.CharField(max_length=50)
    purpose = models.CharField(max_length=10, default='SLC')
    submitted = models.BooleanField(default=False)
    answer = models.ManyToManyField('Answer')


class Question(models.Model):
    question = models.CharField(max_length=500)
    purpose = models.CharField(max_length=10, default='SLC')


class Answer(models.Model):
    question = models.ForeignKey(Question)
    answer = models.CharField(max_length=1000)


class Drupal_camp(models.Model):
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    email = models.EmailField(null=True, blank=True)
    # Day 1 - 1, Day 2 - 2, Both days - 3, else 0
    attendance = models.PositiveSmallIntegerField(default=0)
    role = models.CharField(max_length=100, null=True, blank=True)
    purpose = models.CharField(max_length=10, default='DCM')
    is_student = models.IntegerField(default=0)


class Drupal_WS(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    purpose = models.CharField(max_length=10, default='DRP')
