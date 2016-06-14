# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction as tx


class Command(BaseCommand):

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

    # Helpers / Factories
    # =========================================================================
    def create_user(self, **kwargs):
        user = get_user_model().objects.create(**kwargs)
        password = '123123123'

        user.set_password(password)
        user.save()

        print(">> User created with username:{username} email: {email} and password: {password}".format(
            username=kwargs['username'], email=kwargs['email'], password=password))

        return user
