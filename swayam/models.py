from django.contrib.auth.models import User
from django.db import models

from creation.models import FossCategory


class SwayamUser(models.Model):
    """
    Links a SWAYAM identity to an existing Django User.

    swayam_sub is the stable 'sub' claim supplied by SWAYAM OIDC.
    """

    user = models.OneToOneField(
        User,
        related_name='swayam_identity',
        on_delete=models.CASCADE,
    )

    swayam_sub = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    email = models.EmailField(
        blank=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} -> {}'.format(
            self.swayam_sub,
            self.user.username,
        )


class SwayamEnrollment(models.Model):

    STATUS_ACCESS_PROVISIONED = 'ACCESS_PROVISIONED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_TERMINATED = 'TERMINATED'

    STATUS_CHOICES = (
        (STATUS_ACCESS_PROVISIONED, 'Access Provisioned'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_TERMINATED, 'Terminated'),
    )

    # SWAYAM's unique identifier for:
    # learner + course enrollment
    swayam_enrollment_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    # SWAYAM's own course identifier.
    swayam_course_id = models.CharField(
        max_length=255,
        blank=True,
    )

    # partnerCourseId from SWAYAM maps to this FossCategory.
    foss = models.ForeignKey(
        FossCategory,
        related_name='swayam_enrollments',
        on_delete=models.PROTECT,
    )

    # Null until learner comes through SSO.
    user = models.ForeignKey(
        User,
        related_name='swayam_enrollments',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # Name supplied in the roster.
    student_name = models.CharField(
        max_length=255,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_ACCESS_PROVISIONED,
    )

    # We store what SWAYAM says, although we are not
    # implementing progress reporting yet.
    progress_percent = models.PositiveSmallIntegerField(
        default=0,
    )

    preferred_language = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    registered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(
            self.swayam_enrollment_id,
            self.foss,
        )