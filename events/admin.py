from django.contrib import admin

# Register your models here.

from events.models import University, Institute_type

class UniversityAdmin(admin.ModelAdmin):
    #fields to display
    #fields = ['user', 'state', 'name']
    
    #List display fields
    list_display = ('user', 'state', 'name')
    
class Institute_typeAdmin(admin.ModelAdmin):
    fields = ['name']
    
admin.site.register(University, UniversityAdmin)
admin.site.register(Institute_type, Institute_typeAdmin)

