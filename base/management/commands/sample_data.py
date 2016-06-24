# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

# Standard Library
import random

# Third Party Stuff
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import transaction as tx

# Spoken Tutorial Stuff
from events.models import City, District, InstituteCategory, InstituteType, Location, State, University

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
    states = []
    districts = []
    cities = []
    locations = []
    institutetypes = []
    institutecategories = []
    universites = []

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
        print('>> Creating States')
        for i in range(1, 15):
            state = self.create_state(counter=i)
            self.states.append(state)

            print('>> Creating Universites in %s' % state)
            for i in range(1, random.randint(1, 8)):
                self.universites.append(self.create_university(counter=i, state=state))

        print('>> Creating Districts')
        for i in range(1, 90):
            self.districts.append(self.create_district(counter=i))

        print('>> Creating Cities')
        for i in range(1, 90):
            self.cities.append(self.create_city(counter=i))

        print('>> Creating Locations')
        for i in range(1, 90):
            self.locations.append(self.create_location(counter=i))

        print('>> Creating Institute Types')
        for name in INSTITUTE_TYPES:
            self.institutetypes.append(InstituteType.objects.get_or_create(name=name))

        print('>> Creating Institute Categories')
        for name in INSTITUTE_CATEGORIES:
            self.institutecategories.append(InstituteCategory.objects.get_or_create(name=name))

    # Helpers / Factories
    # =========================================================================
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
                                                code='D%s' % counter,
                                                state=state)
        return obj

    def create_city(self, counter=None, state=None):
        state = state if state else random.choice(self.states)
        obj, _ = City.objects.get_or_create(name='City %s' % counter,
                                            state=state)
        return obj

    def create_location(self, counter=None, district=None):
        district = district if district else random.choice(self.districts)
        obj, _ = Location.objects.get_or_create(name='City %s' % counter,
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
