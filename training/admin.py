from django.contrib import admin

# Register your models here.
from .models import ILWFossMdlCourses, Company, CompanyType

class CompanyAdmin(admin.ModelAdmin):
    pass

class CompanyTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(ILWFossMdlCourses)
admin.site.register(Company, CompanyAdmin)
admin.site.register(CompanyType, CompanyTypeAdmin)

