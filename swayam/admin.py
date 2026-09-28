from django.contrib import admin

from .models import (
    SwayamEnrollment,
    SwayamUser,
    SwayamTutorialProgress,
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


@admin.register(SwayamTutorialProgress)
class SwayamTutorialProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'foss', 'tutorial_detail', 'video_time', 'progress_percent', 'is_completed', 'updated')
    list_filter = ('is_completed', 'foss')
    search_fields = ('user__username', 'tutorial_detail__tutorial')