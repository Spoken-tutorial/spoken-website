# Code to create category table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py FOSS_CATEGORIES"

from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from django.db.models import Q
# Spoken Tutorial Stuff
from creation.models import FossSuperCategory , RoleRequest , ContributorRole , DomainReviewerRole , QualityReviewerRole
from django.contrib.auth.models import User

class Command(BaseCommand):
    categories = []

    @tx.atomic
    def handle(self, *args, **options):

    	all_requests = RoleRequest.objects.filter(status = 0).values('user_id').distinct()
    	for a_user in all_requests:
			user = User.objects.get(pk = a_user['user_id'])
			contri_check = user.groups.filter(name='Contributor').exists()
			domain_check = user.groups.filter(name='Domain-Reviewer').exists()
			quality_check = user.groups.filter(name='Quality-Reviewer').exists()
			#print(a_user['user_id'],contri_check,domain_check,quality_check)
			
			if contri_check:
				valid_role = RoleRequest.objects.filter(user_id=a_user['user_id'], status = 1,role_type=0).exists()
				if valid_role:
					#print(a_user," is a Contributor")
					abc = 1
				else:
					print("Remove me as a Contributor")

			if domain_check:
				valid_role = RoleRequest.objects.filter(user_id=a_user['user_id'], status = 1,role_type=3).exists()
				if valid_role:
					#print(a_user['user_id']," is a Domain-Reviewer")
					abc = 1
				else:
					print("Remove",a_user['user_id'],"as a Domain-Reviewer")

			if quality_check:
				valid_role = RoleRequest.objects.filter(user_id=a_user['user_id'], status = 1,role_type=4).exists()
				if valid_role:
					#print(a_user['user_id']," is a Domain-Reviewer")
					abc = 1
				else:
					print("Remove",a_user['user_id'],"as a Quality-Reviewer")
