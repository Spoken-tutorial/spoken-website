from django.contrib import admin
from django.template.defaultfilters import slugify
# Register your models here.

from events.models import *
from events.forms import RpForm
from events.formsv2 import MapCourseWithFossForm

class UniversityAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('user', 'state', 'name')
    list_filter = ('state',)
    def save_model(self, request, obj, form, change):
        obj.user_id = request.user.id
        obj.save()

class CourseAdmin(admin.ModelAdmin):
    fields = ['name']

class InstituteTypeAdmin(admin.ModelAdmin):
    fields = ['name']

class InstituteCategoryAdmin(admin.ModelAdmin):
    fields = ['name']

class TestCategoryAdmin(admin.ModelAdmin):
    fields = ['name']

class StateAdmin(admin.ModelAdmin):
    fields = ['name', 'code']
    def save_model(self, request, obj, form, change):
        obj.slug = slugify(request.POST['name'])
        obj.save()

class DistrictAdmin(admin.ModelAdmin):
    fields = ['name', 'state']
    list_display = ('name', 'state', 'created')
    list_filter = ('state',)

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'created')
    fields = ['name', 'state']
    list_filter = ('state',)

class FossMdlCoursesAdmin(admin.ModelAdmin):
    fields = ['foss', 'mdlcourse_id', 'mdlquiz_id']
    list_display = ('foss', 'mdlcourse_id', 'mdlquiz_id')
    
class RpRoleAdmin(admin.ModelAdmin):
    form = RpForm
    fields = ('user', 'state', 'status')
    list_display = ('user', 'state', 'status')
    
    def save_model(self, request, obj, form, change):
        obj.assigned_by = request.user.id
        obj.save()

class DepartmentAdmin(admin.ModelAdmin):
    fields = ['name']

class PermissionTypeAdmin(admin.ModelAdmin):
    fields = ['name']

admin.site.register(Course, CourseAdmin)
admin.site.register(University, UniversityAdmin)
admin.site.register(InstituteType, InstituteTypeAdmin)
admin.site.register(InstituteCategory, InstituteCategoryAdmin)
admin.site.register(TestCategory, TestCategoryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(ResourcePerson, RpRoleAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(PermissionType, PermissionTypeAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(FossMdlCourses, FossMdlCoursesAdmin)


# EVENTS V2

class CourseMapAdmin(admin.ModelAdmin):
    # Custom form to overwrite the default form field options
    form = MapCourseWithFossForm

admin.site.register(CourseMap, CourseMapAdmin)
