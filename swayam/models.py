from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from events.models import AcademicCenter
from creation.models import FossCategory



@python_2_unicode_compatible
class SwayamTracking(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='swayam_trackings'
    )
    academic_center = models.ForeignKey(
        AcademicCenter,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Academic Center",
        related_name='swayam_trackings'
    )
    dropdown_option = models.CharField(max_length=255, verbose_name="Option chosen from dropdown")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date and time")
    is_logged_in = models.BooleanField(default=False, verbose_name="Is logged in")
    is_subscribed_institution = models.BooleanField(default=False, verbose_name="Is part of a subscribed college/school")
    roles = models.CharField(max_length=255, blank=True, default='', verbose_name="Roles in subscribed institution")

    class Meta(object):
        verbose_name = "SWAYAM Tracking"
        verbose_name_plural = "SWAYAM Trackings"
        ordering = ['-created']

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return "{0} - {1} - {2}".format(username, self.dropdown_option, self.created)

    @property
    def option_chosen(self):
        return self.dropdown_option

    @property
    def date_time(self):
        return self.created


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
