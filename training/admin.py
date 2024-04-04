from django.contrib import admin

# Register your models here.
from .models import ILWFossMdlCourses, TrainingEvents


class TrainingEventsAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'entry_user', 'event_type', 'event_fee', 'state', 'host_college', 'foss', 'Language_of_workshop', 'event_start_date', 'event_end_date', 'event_coordinator_name', 'event_coordinator_email', 'event_coordinator_contact_no', 'registartion_start_date', 'registartion_end_date', 'training_status', 'entry_date')
    list_filter = ('event_type', 'state',  'foss', 'Language_of_workshop', 'event_start_date', 'event_end_date', 'training_status')
    search_fields = ('event_name', 'event_coordinator_name', 'event_coordinator_email', 'event_coordinator_contact_no')
    ordering = ('-entry_date',)


admin.site.register(ILWFossMdlCourses)
admin.site.register(TrainingEvents, TrainingEventsAdmin)
