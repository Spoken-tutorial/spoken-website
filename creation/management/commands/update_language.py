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
        
        # -- Contributor -- 
        all_contributors = ContributorRole.objects.filter(status = 1).values('user_id','language_id','created').order_by('user_id','language_id').distinct()
        for a_user in all_contributors:
        	user = User.objects.get(pk = a_user['user_id'])
        	
	        check = user.groups.filter(name='Contributor').exists()
	        if check:
				role_requests = RoleRequest.objects.filter(user_id = a_user['user_id'],role_type = 0,language_id = a_user['language_id']).values('language_id')
				if not role_requests  :
					if role_requests.values('user_id','language_id') :
						print("Contributor : ",user.id ," exists : " ,a_user['language_id'],role_requests.values('language_id'))	
					else :
						print("Contributor : ",user.id ," does not exists : " ,a_user['language_id'],a_user['created'])
						role_request_new = RoleRequest()
						role_request_new.user_id = a_user['user_id']
						role_request_new.role_type = 0
						role_request_new.status = 1
						role_request_new.approved_user_id = a_user['user_id']
						role_request_new.language_id = a_user['language_id']
						role_request_new.save()
						role_request_new.created = a_user['created']
						role_request_new.save()

# -- External Contributor -- 
        all_contributors = ContributorRole.objects.filter(status = 1).values('user_id','language_id','created').order_by('user_id','language_id').distinct()
        for a_user in all_contributors:
        	user = User.objects.get(pk = a_user['user_id'])
        	
	        check = user.groups.filter(name='Contributor').exists()
	        if check:
				role_requests = RoleRequest.objects.filter(user_id = a_user['user_id'],role_type = 1,language_id = a_user['language_id']).values('language_id')
				if not role_requests  :
					if role_requests.values('user_id','language_id') :
						print("External-Contributor : ",user.id ," exists : " ,a_user['language_id'],role_requests.values('language_id'))	
					else :
						print("External-Contributor : ",user.id ," does not exists : " ,a_user['language_id'],a_user['created'])
						role_request_new = RoleRequest()
						role_request_new.user_id = a_user['user_id']
						role_request_new.role_type = 1
						role_request_new.status = 1
						role_request_new.approved_user_id = a_user['user_id']
						role_request_new.language_id = a_user['language_id']
						role_request_new.save()
						role_request_new.created = a_user['created']
						role_request_new.save()



		# -- Domain Reviewer --

        all_domain = DomainReviewerRole.objects.filter(status =1).values('user_id','language_id','created').order_by('user_id','language_id').distinct()
        for a_user in all_domain:
        	user = User.objects.get(pk = a_user['user_id'])
        	
	        check = user.groups.filter(name='Domain-Reviewer').exists()
	        if check:
				role_requests = RoleRequest.objects.filter(user_id = a_user['user_id'],role_type = 3,language_id = a_user['language_id']).values('language_id')
				if not role_requests  :
					if role_requests.values('user_id','language_id') :
						print("Domain-Reviewer : ",user.id ," exists : " ,a_user['language_id'],role_requests.values('language_id'))	
					else :
						print("Domain-Reviewer : ",user.id ," does not exists : " ,a_user['language_id'],a_user['created'])
						role_request_new = RoleRequest()
						role_request_new.user_id = a_user['user_id']
						role_request_new.role_type = 3
						role_request_new.status = 1
						role_request_new.approved_user_id = a_user['user_id']
						role_request_new.language_id = a_user['language_id']
						role_request_new.save()
						role_request_new.created = a_user['created']
						role_request_new.save()



		# -- Quality Reviewer


        all_domain = QualityReviewerRole.objects.filter(status =1).values('user_id','language_id','created').order_by('user_id','language_id').distinct()
        for a_user in all_domain:
        	user = User.objects.get(pk = a_user['user_id'])
        	
	        check = user.groups.filter(name='Quality-Reviewer').exists()
	        if check:
				role_requests = RoleRequest.objects.filter(user_id = a_user['user_id'],role_type = 4,language_id = a_user['language_id']).values('language_id')
				if not role_requests  :
					if role_requests.values('user_id','language_id') :
						print("Quality-Reviewer : ",user.id ," exists : " ,a_user['language_id'],role_requests.values('language_id'))	
					else :
						print("Quality-Reviewer : ",user.id ," does not exists : " ,a_user['language_id'],a_user['created'])
						role_request_new = RoleRequest()
						role_request_new.user_id = a_user['user_id']
						role_request_new.role_type = 4
						role_request_new.status = 1
						role_request_new.approved_user_id = a_user['user_id']
						role_request_new.language_id = a_user['language_id']
						role_request_new.save()
						role_request_new.created = a_user['created']
						role_request_new.save()
					
				