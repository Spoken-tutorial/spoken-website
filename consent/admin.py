from django.contrib import admin

from .models import Consent


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ('file', 'type', 'is_active', 'file_hash', 'created_at')
    list_filter = ('is_active', 'type')
    readonly_fields = ('file_hash', 'created_at')
