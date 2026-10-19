from django.contrib import admin
from django.contrib.auth.models import User
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
    fields = ['foss', 'mdlcourse_id', 'mdlquiz_id', 'language', 'level']
    list_display = ('foss', 'mdlcourse_id', 'mdlquiz_id', 'language', 'level')

    
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

class PaymentVerificationUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'created_at', 'updated_at')
    list_filter = ('state',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'state__name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(groups__name='Payment Verification Staff')
        return super(PaymentVerificationUserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(CourseMap, CourseMapAdmin)
admin.site.register(PaymentVerificationUser, PaymentVerificationUserAdmin)


class AcademicDocumentAdmin(admin.ModelAdmin):
    list_display = ('reference_no', 'doc_type', 'academic', 'salutation', 'recipient_name', 'organiser', 'issued_date')
    list_filter = ('doc_type', 'issued_date')
    search_fields = ('reference_no', 'academic__institution_name', 'recipient_name', 'payment__id')
    readonly_fields = ('issued_date', 'created_at')

admin.site.register(AcademicDocument, AcademicDocumentAdmin)

