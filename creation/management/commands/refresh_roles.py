#!/usr/bin/python
# -*- coding: utf-8 -*-
# Code to add publish date in tutorialresource table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py refresh_roles"

# This will refresh contributor list into contributorrole

from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff

from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

# Spoken Tutorial Stuff

from creation.models import TutorialResource, ContributorRole, \
    DomainReviewerRole, QualityReviewerRole, TutorialsAvailable, \
    TutorialDetail, ContributorRating, RoleRequest, User, Language
from creation.views import send_mail_to_contributor, is_contributor, is_external_contributor


class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):

        ROLES_DICT = {
            'contributor': 0,
            'external-contributor': 1,
            'video-reviewer': 2,
            'domain-reviewer': 3,
            'quality-reviewer': 4,
            }

        STATUS_DICT = {'inactive': 0, 'active': 1}

        contrib_count = 0
        domain_count = 0
        quality_count = 0
        contributor_roles = \
            ContributorRole.objects.filter(status=1).values('user_id','user__username',
                'language_id','language__name').distinct()
        domain_roles = \
            DomainReviewerRole.objects.filter(status=1).values('user_id','user__username'
                , 'language_id','language__name').distinct()
        quality_roles = \
            QualityReviewerRole.objects.filter(status=1).values('user_id','user__username'
                , 'language_id','language__name').distinct()

        for quality_reviewer in quality_roles:
            role_request = \
                RoleRequest.objects.filter(role_type=ROLES_DICT['quality-reviewer'
                    ], user_id=quality_reviewer['user_id'],
                    language_id=quality_reviewer['language_id'])
            if not role_request.exists():
                role_request = RoleRequest()
                role_request.user = \
                    User.objects.get(id=quality_reviewer['user_id'])
                role_request.language = \
                    Language.objects.get(id=quality_reviewer['language_id'
                        ])
                role_request.role_type = ROLES_DICT['quality-reviewer']
                role_request.status = STATUS_DICT['active']
                role_request.save()
                quality_count += 1
                print(quality_reviewer['user__username'], "added in QualityReviewerRole for",\
                    quality_reviewer['language__name'])
            else:
                role_request.update(status=STATUS_DICT['active'])

            for domain_reviewer in domain_roles:
                role_request = \
                    RoleRequest.objects.filter(role_type=ROLES_DICT['domain-reviewer'
                        ], user_id=domain_reviewer['user_id'],
                        language_id=domain_reviewer['language_id'])
                if not role_request.exists():
                    role_request = RoleRequest()
                    role_request.user = \
                        User.objects.get(id=domain_reviewer['user_id'])
                    role_request.language = \
                        Language.objects.get(id=domain_reviewer['language_id'
                            ])
                    role_request.role_type = \
                        ROLES_DICT['domain-reviewer']
                    role_request.status = STATUS_DICT['active']
                    role_request.save()
                    domain_count += 1
                    print(domain_reviewer['user__username'], "added in DomainReviewerRole for",
                        domain_reviewer['language__name'])
               	else:
               		role_request.update(status=STATUS_DICT['active'])

        for contributor in contributor_roles:
            role_request = \
                RoleRequest.objects.filter(Q(role_type=ROLES_DICT['contributor'
                    ]) | Q(role_type=ROLES_DICT['external-contributor'
                    ]), user_id=contributor['user_id'],
                    language_id=contributor['language_id'])
            if not role_request.exists():
                contrib_user = User.objects.get(id=contributor['user_id'
                        ])
                role_request = RoleRequest()
                role_request.user = contrib_user
                role_request.language = \
                    Language.objects.get(id=contributor['language_id'])
                if is_contributor(contrib_user):
                    role_request.role_type = ROLES_DICT['contributor']
                elif is_external_contributor(contrib_user):
                    role_request.role_type = \
                        ROLES_DICT['external-contributor']
                role_request.status = 1
                role_request.save()
                contributor_with_rating = \
                    ContributorRating.objects.filter(user_id=contributor['user_id'
                        ], language_id=contributor['language_id'])
                if not contributor_with_rating.exists():
                    new_contrib_rating_request = ContributorRating()
                    new_contrib_rating_request.user_id = \
                        contributor['user_id']
                    new_contrib_rating_request.language_id = \
                        contributor['language_id']
                    new_contrib_rating_request.save()
                contrib_count += 1
                print(contributor['user__username'], "added in ContributorReviewerRole for",
                    contributor['language__name'])
            else:
                role_request.update(status=STATUS_DICT['active'])

        print(str(contrib_count), ' Contributors added')
        print(str(domain_count), ' Domain Reviewers added')
        print(str(quality_count), ' Quality Reviewers added')
