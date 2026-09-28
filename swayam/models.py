from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from events.models import AcademicCenter


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
