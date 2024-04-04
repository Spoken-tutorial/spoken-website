from django.contrib import admin

# Register your models here.
from .models import ILWFossMdlCourses, TrainingEvents

class TrainingEventsAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'entry_user')


admin.site.register(ILWFossMdlCourses)
admin.site.register(TrainingEvents, TrainingEventsAdmin)
