from django.contrib import admin

# Register your models here.
from .models import ILWFossMdlCourses, Company, CompanyType, ExternalCourseMap, ExternalEventCourse

class CompanyAdmin(admin.ModelAdmin):
    pass

class CompanyTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(ILWFossMdlCourses)
admin.site.register(Company, CompanyAdmin)
admin.site.register(CompanyType, CompanyTypeAdmin)
admin.site.register(ExternalCourseMap)
admin.site.register(ExternalEventCourse)
