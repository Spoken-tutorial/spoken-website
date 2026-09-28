from __future__ import unicode_literals

from django.contrib import admin
from .models import SwayamTracking


class SwayamTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'dropdown_option', 'is_logged_in', 'is_subscribed_institution', 'roles', 'created')
    list_filter = ('is_logged_in', 'is_subscribed_institution', 'created')
    search_fields = ('user__username', 'user__email', 'dropdown_option', 'roles')
    readonly_fields = ('created',)


admin.site.register(SwayamTracking, SwayamTrackingAdmin)
