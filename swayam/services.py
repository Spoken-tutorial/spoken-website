import logging

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from creation.models import (
    FossCategory,
    TutorialDetail,
    Language,
)
from .client import SwayamClient
from .models import (
    SwayamEnrollment,
    SwayamUser,
    SwayamTutorialProgress,
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


# to track video progress, update enrollment course completion
class SwayamProgressService(object):
    def __init__(self, client=None):
        self.client = client or SwayamClient()

    @transaction.atomic
    def record_progress(self, user, foss, tutorial_detail, video_time=0.0, duration=0.0, language=None):
        video_time, duration = float(video_time or 0.0), float(duration or 0.0)
        calc_percent = min(100, int(round((video_time / duration) * 100))) if duration > 0 else 0
        enrollment = SwayamEnrollment.objects.filter(user=user, foss=foss).first()

        prog, created = SwayamTutorialProgress.objects.select_for_update().get_or_create(
            user=user, tutorial_detail=tutorial_detail,
            defaults={
                'enrollment': enrollment, 'foss': foss, 'language': language,
                'video_time': video_time, 'video_duration': duration,
                'progress_percent': calc_percent,
                'is_completed': (calc_percent >= 90),
                'completed_at': timezone.now() if calc_percent >= 90 else None,
            }
        )
        if not created:
            prog.video_time = video_time
            if duration > 0:
                prog.video_duration = duration
            prog.progress_percent = max(prog.progress_percent, calc_percent)
            if prog.progress_percent >= 90 and not prog.is_completed:
                prog.is_completed = True
                prog.completed_at = timezone.now()
            if enrollment and not prog.enrollment:
                prog.enrollment = enrollment
            if language and not prog.language:
                prog.language = language
            prog.save()

        # Update overall enrollment course progress
        if enrollment:
            total = TutorialDetail.objects.filter(foss=enrollment.foss).count()
            completed = SwayamTutorialProgress.objects.filter(user=user, foss=enrollment.foss, is_completed=True).count()
            course_percent = min(100, int(round((float(completed) / float(total)) * 100))) if total > 0 else 0

            enrollment.progress_percent = course_percent
            if enrollment.status == SwayamEnrollment.STATUS_ACCESS_PROVISIONED and course_percent > 0:
                enrollment.status = SwayamEnrollment.STATUS_IN_PROGRESS
            if course_percent >= 100:
                enrollment.status = SwayamEnrollment.STATUS_COMPLETED
                if not enrollment.completed_at:
                    enrollment.completed_at = timezone.now()
            enrollment.save(update_fields=['progress_percent', 'status', 'completed_at', 'updated'])

            # for swayam api
            self.report_progress(enrollment)

        return prog

    # to transmit progress to swayam api
    def report_progress(self, enrollment):
        try:
            self.client.update_progress(enrollment.swayam_enrollment_id, enrollment.progress_percent)
            if enrollment.status == SwayamEnrollment.STATUS_COMPLETED:
                self.client.confirm_completion(enrollment.swayam_enrollment_id)
        except Exception as exc:
            logger.warning('SWAYAM API progress report skipped/failed: %s', exc)