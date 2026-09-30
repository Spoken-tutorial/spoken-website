from __future__ import unicode_literals

from django.contrib import admin

from .models import (
    SwayamEnrollment,
    SwayamTracking,
    SwayamUser,
)


@admin.register(SwayamUser)
class SwayamUserAdmin(admin.ModelAdmin):
    list_display = (
        'swayam_sub',
        'user',
        'email',
        'created',
    )
    search_fields = (
        'swayam_sub',
        'email',
        'user__username',
        'user__email',
    )


@admin.register(SwayamEnrollment)
class SwayamEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        'swayam_enrollment_id',
        'student_name',
        'foss',
        'user',
        'status',
        'progress_percent',
        'updated',
    )
    list_filter = (
        'status',
        'foss',
    )
    search_fields = (
        'swayam_enrollment_id',
        'student_name',
        'user__username',
        'user__email',
    )


@admin.register(SwayamTracking)
class SwayamTrackingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'academic_center',
        'dropdown_option',
        'is_logged_in',
        'is_subscribed_institution',
        'roles',
        'created',
    )
    list_filter = (
        'is_logged_in',
        'is_subscribed_institution',
        'created',
    )
    search_fields = (
        'user__username',
        'user__email',
        'academic_center__institution_name',
        'dropdown_option',
        'roles',
    )
    readonly_fields = ('created',)
