import logging

from django.db import transaction
from django.utils.dateparse import parse_datetime

from creation.models import FossCategory
from .client import SwayamClient

from django.contrib.auth.models import User

from .models import SwayamUser

from .models import (
    SwayamEnrollment,
    SwayamUser,
)

logger = logging.getLogger(__name__)

class SwayamEnrollmentService(object):
    def __init__(self, client=None):
        self.client = client or SwayamClient()

    def _get_foss(self, partner_course_id):
        """
        We are defining partnerCourseId as FossCategory.id.

        Example:
            partnerCourseId = "42"
            -> FossCategory.objects.get(pk=42)
        """
        if partner_course_id in (None, ''):
            raise ValueError('SWAYAM enrollment has no partnerCourseId.')
        try:
            foss_id = int(partner_course_id)
        except (TypeError, ValueError):
            raise ValueError('Invalid partnerCourseId: {}'.format(partner_course_id))

        try:
            return FossCategory.objects.get(pk=foss_id)
        except FossCategory.DoesNotExist:
            raise ValueError(
                'No FossCategory exists for partnerCourseId={}'
                .format(partner_course_id)
            )

    def _parse_datetime(self, value):
        if not value:
            return None
        return parse_datetime(value)

    @transaction.atomic
    def sync_enrollment_row(self, row):
        enrollment_id = row.get('enrollmentId')
        if not enrollment_id:
            raise ValueError('SWAYAM row is missing enrollmentId.')
        foss = self._get_foss(row.get('partnerCourseId'))
        enrollment, created = (
                    SwayamEnrollment.objects.update_or_create(
                        swayam_enrollment_id=enrollment_id,
                        defaults={
                            'swayam_course_id': (
                                row.get('courseId') or ''
                            ),
                            'foss': foss,
                            'student_name': (
                                row.get('studentName') or ''
                            ),
                            'status': (
                                row.get('status')
                                or SwayamEnrollment.STATUS_ACCESS_PROVISIONED
                            ),
                            'progress_percent': (
                                row.get('progressPercent') or 0
                            ),
                            'preferred_language': (
                                row.get('preferredLanguage')
                            ),
                            'registered_at': self._parse_datetime(
                                row.get('registeredAt')
                            ),
                            'completed_at': self._parse_datetime(
                                row.get('completedAt')
                            ),
                        },
                    )
                )
        return enrollment, created

    def sync_all_enrollments(self):
            created_count = 0
            updated_count = 0
            failed_count = 0
    
            for row in self.client.iter_enrollments():
                try:
                    enrollment, created = (
                        self.sync_enrollment_row(row)
                    )
    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
    
                except Exception:
                    failed_count += 1
    
                    logger.exception(
                        'Could not sync SWAYAM enrollment %s',
                        row.get('enrollmentId'),
                    )
    
            return {
                'created': created_count,
                'updated': updated_count,
                'failed': failed_count,
            }


class SwayamUserService(object):

    @transaction.atomic
    def get_or_create_user(
        self,
        swayam_sub,
        email,
        name='',
    ):
        """
        1. Existing SWAYAM sub wins.
        2. Otherwise link to an existing unique email.
        3. Otherwise create a minimal Django User.

        No profile is created.
        """

        try:
            identity = (
                SwayamUser.objects.select_related('user')
                .get(swayam_sub=swayam_sub)
            )

            return identity.user, False

        except SwayamUser.DoesNotExist:
            pass

        email = (email or '').strip().lower()

        if not email:
            raise ValueError(
                'SWAYAM did not provide an email address.'
            )

        matching_users = User.objects.filter(
            email__iexact=email
        )

        count = matching_users.count()

        if count > 1:
            # Do not arbitrarily attach a SWAYAM identity
            # to one of multiple local accounts.
            raise ValueError(
                'Multiple local users use this email address.'
            )

        if count == 1:
            user = matching_users[0]
            user_created = False

        else:
            username = self._build_username(
                swayam_sub,
                email,
            )

            first_name, last_name = (
                self._split_name(name)
            )

            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )

            # The user authenticates through SWAYAM.
            # Do not create a fake local password.
            user.set_unusable_password()
            user.save()

            user_created = True

        SwayamUser.objects.create(
            user=user,
            swayam_sub=swayam_sub,
            email=email,
        )

        return user, user_created

    def _build_username(self, swayam_sub, email):
        """
        Prefer email when available, because the existing
        Spoken Tutorial authentication backend already treats
        email/username as login identifiers.

        If username already exists, use the SWAYAM sub.
        """

        candidate = email[:150]

        if not User.objects.filter(
            username=candidate
        ).exists():
            return candidate

        candidate = 'swayam_{}'.format(
            swayam_sub.replace('-', '')
        )

        return candidate[:150]

    def _split_name(self, name):
        parts = (name or '').strip().split()

        if not parts:
            return '', ''

        if len(parts) == 1:
            return parts[0][:30], ''

        return (
            parts[0][:30],
            ' '.join(parts[1:])[:30],
        )

    @transaction.atomic
    def link_enrollment(
        self,
        user,
        swayam_enrollment_id,
    ):
        try:
            enrollment = SwayamEnrollment.objects.select_for_update().get(
                swayam_enrollment_id=swayam_enrollment_id
            )

        except SwayamEnrollment.DoesNotExist:
            raise ValueError(
                'Unknown SWAYAM enrollment: {}'.format(
                    swayam_enrollment_id
                )
            )

        if (
            enrollment.user_id
            and enrollment.user_id != user.id
        ):
            raise ValueError(
                'SWAYAM enrollment is already linked '
                'to another local user.'
            )

        enrollment.user = user
        enrollment.save(
            update_fields=[
                'user',
                'updated',
            ]
        )

        return enrollment