from django.contrib import admin

# Register your models here.

from events.models import University, InstituteType, State, ResourcePerson, Department, PermissionType, TestCategory, InstituteCategory
from events.forms import RpForm

class UniversityAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'name')
    
class InstituteTypeAdmin(admin.ModelAdmin):
    fields = ['name']

class InstituteCategoryAdmin(admin.ModelAdmin):
    fields = ['name']

class TestCategoryAdmin(admin.ModelAdmin):
    fields = ['name']

class StateAdmin(admin.ModelAdmin):
	fields = ['name']

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
    
admin.site.register(University, UniversityAdmin)
admin.site.register(InstituteType, InstituteTypeAdmin)
admin.site.register(InstituteCategory, InstituteCategoryAdmin)
admin.site.register(TestCategory, TestCategoryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(ResourcePerson, RpRoleAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(PermissionType, PermissionTypeAdmin)
