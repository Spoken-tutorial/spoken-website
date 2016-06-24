# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

# Standard Library
import random

# Third Party Stuff
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import transaction as tx

# Spoken Tutorial Stuff
from events.models import AcademicCenter, City, District, InstituteCategory, InstituteType, Location, State, University

GROUPS = [
    "Admin-Team",
    "Administrator",
    "Contributor",
    "Creation-Team",
    "Domain-Reviewer",
    "Event Manager",
    "External-Contributor",
    "Invigilator",
    "Organiser",
    "Quality-Reviewer",
    "Resource Person",
    "Student",
    "Technical-Team",
    "Video-Reviewer",
]


INSTITUTE_TYPES = [
    "College",
    "Polytechnic",
    "ITI",
    "Vocational",
    "School",
    "Uncategorised",
    "Engineering",
    "University",
    "Management",
    "NGO - Training Centre",
    "NGO",
    "Ekal Vidyalaya",
    "Pharmacy",
]

INSTITUTE_CATEGORIES = [
    "Govt",
    "Private",
    "NGO",
    "Uncategorised",
]


class Command(BaseCommand):
    groups = []
    states = []
    districts = []
    cities = []
    locations = []
    institutetypes = []
    institutecategories = []
    universites = []
    academic_centers = []

    @tx.atomic
    def handle(self, *args, **options):

        print('>> Updating domain to localhost:8000')
        site, created = Site.objects.get_or_create(pk=1)
        site.domain, site.name = 'localhost:8000', 'Dev at Localhost'
        site.save()

        print('>> Creating Superuser')
        self.super_user = self.create_user(is_superuser=True,
                                           username='admin',
                                           email='admin@example.com',
                                           is_active=True, is_staff=True)

        print('>> Creating Groups')
        for name in GROUPS:
            group, _ = Group.objects.get_or_create(name=name)
            self.institutetypes.append(group)

        print('>> Creating Institute Types')
        for name in INSTITUTE_TYPES:
            institute_type, _ = InstituteType.objects.get_or_create(name=name)
            self.institutetypes.append(institute_type)

        print('>> Creating Institute Categories')
        for name in INSTITUTE_CATEGORIES:
            institute_cat, _ = InstituteCategory.objects.get_or_create(name=name)
            self.institutecategories.append(institute_cat)

        print('>> Creating States')
        for i in range(1, 15):
            state = self.create_state(counter=i)
            self.states.append(state)

            print('>>> Creating cities in %s' % state)
            for i in range(1, random.randint(1, 12)):
                self.cities.append(self.create_city(counter=i, state=state))

            print('>>> Creating districts in %s' % state)
            for i in range(1, random.randint(1, 6)):
                district = self.create_district(counter=i, state=state)
                self.districts.append(district)

                print('>>>> Creating Locations in %s' % district)
                for i in range(1, random.randint(1, 6)):
                    location = self.create_location(counter=i, district=district)
                    self.locations.append(location)

            print('>> Creating Universites in %s' % state)
            for i in range(1, random.randint(1, 8)):
                university = self.create_university(counter=i, state=state)
                self.universites.append(university)

                print('>> Creating academic centers in %s' % university)
                for i in range(1, random.randint(1, 4)):
                    academic_center = self.create_academic_center(counter=i, university=university)
                    self.academic_centers.append(academic_center)

    # Helpers / Factories
    # =========================================================================
    def create_academic_center(self, counter=None, university=None):
        university = university if university else random.choice(self.universites)
        state = university.state
        district = District.objects.filter(state=state).order_by('?').first()
        location = Location.objects.filter(district=district).order_by('?').first()
        city = City.objects.filter(state=state).order_by('?').first()
        academic_code = "%s%s" % (university.id, counter)
        params = {
            'user': self.super_user,
            'institution_name': "Institute %s" % academic_code,
            'institution_type': random.choice(self.institutetypes),
            'institute_category': random.choice(self.institutecategories),
            'university': university,
            'academic_code': academic_code,
            'district': district,
            'location': location,
            'city': city,
            'state': state,
            'address': "sample address %s" % academic_code,
            'pincode': "111%s" % academic_code,
            'resource_center': random.choice([True, False]),
            'rating': random.choice([1, 2, 3, 4, 5]),
            'contact_person': "Contact Person %s" % counter,
            'remarks': "Remarks %s" % counter,
            'status': True,
        }
        obj, _ = AcademicCenter.objects.get_or_create(**params)
        return obj

    def create_university(self, counter=None, state=None):
        state = state if state else random.choice(self.states)
        obj, _ = University.objects.get_or_create(name="University %s%s" % (counter, state.id),
                                                  state=state,
                                                  user=self.super_user)
        return obj

    def create_state(self, counter=None):
        s, _ = State.objects.get_or_create(name='State %s' % counter,
                                           code='s%s' % counter,
                                           slug='state-%s' % counter)
        return s

    def create_district(self, counter=None, state=None):
        state = state if state else random.choice(self.states)
        obj, _ = District.objects.get_or_create(name='District %s' % counter,
                                                code='%s%s' % (counter, state.id),
                                                state=state)
        return obj

    def create_city(self, counter=None, state=None):
        state = state if state else random.choice(self.states)
        obj, _ = City.objects.get_or_create(name='City %s' % counter,
                                            state=state)
        return obj

    def create_location(self, counter=None, district=None):
        district = district if district else random.choice(self.districts)
        obj, _ = Location.objects.get_or_create(name='%s Location %s' % (district, counter),
                                                pincode='1100%s' % counter,
                                                district=district)
        return obj

    def create_user(self, **kwargs):
        user, _ = get_user_model().objects.get_or_create(**kwargs)
        password = '123123123'

        user.set_password(password)
        user.save()

        print(">> User created with username:{username} email: {email} and password: {password}".format(
            username=kwargs['username'], email=kwargs['email'], password=password))

        return user
