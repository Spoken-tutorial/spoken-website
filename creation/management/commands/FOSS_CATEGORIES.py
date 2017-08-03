# Code to create category table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py FOSS_CATEGORIES"

from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from creation.models import FossSuperCategory

all_categories = [
    "Animation and Graphics",
    "Application Software",
    "Biochemistry-Related Software",
    "Chemistry-Related Software",
    "Computational Fluid Dynamics",
    "Computational Software",
    "EDA Tools",
    "Physics",
    "Programming Software",
    "Scripting Software",
    "Skill Development",
    "Software for Schools",
    "Typesetting Software",
    "Utility Software",
    "Version Control System",
    "Website Building"
]


class Command(BaseCommand):
    categories = []

    @tx.atomic
    def handle(self, *args, **options):
        print('>> Creating Categories')
        for item in all_categories:
            category, _ = FossSuperCategory.objects.get_or_create(name=item)
            self.categories.append(category)
