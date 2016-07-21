# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

# Standard Library
# import random

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx

# Spoken Tutorial Stuff
from events.models import Department

from .data import EVENTS_DEPARTMENTS


class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        print('>> creating departments...')
        for name in EVENTS_DEPARTMENTS:
            Department.objects.get_or_create(name=name)
