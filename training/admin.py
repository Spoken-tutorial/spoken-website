from django.contrib import admin

# Register your models here.
from .models import ILWFossMdlCourses, Company

class CompanyAdmin(admin.ModelAdmin):
    pass

admin.site.register(ILWFossMdlCourses)
admin.site.register(Company, CompanyAdmin)
