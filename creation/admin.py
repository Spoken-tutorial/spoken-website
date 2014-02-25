import os
from django.conf import settings
from django.contrib import admin

from creation.models import *
from creation.forms import *

class LanguageAdmin(admin.ModelAdmin):
	exclude = ('user',)
	list_display = ('name', 'created', 'updated', 'user')
	def save_model(self, request, obj, form, change):
		obj.user = request.user
		obj.save()

class FossCategoryAdmin(admin.ModelAdmin):
	exclude = ('user',)
	list_display = ('foss', 'status', 'created', 'updated', 'user')

	def save_model(self, request, obj, form, change):
		obj.user = request.user
		obj.save()

	def mark_foss_completed(self, request, queryset):
		rows_updated = queryset.update(status=1)
		if rows_updated == 1:
			message_bit = "1 FOSS category was"
		else:
			message_bit = "%s FOSS categories were" % rows_updated
		self.message_user(request, "%s successfully marked as completed." % message_bit)

	def mark_foss_pending(self, request, queryset):
		rows_updated = queryset.update(status=0)
		if rows_updated == 1:
			message_bit = "1 FOSS category was"
		else:
			message_bit = "%s FOSS categories were" % rows_updated
		self.message_user(request, "%s successfully marked as pending." % message_bit)

	mark_foss_completed.short_description = "Mark selected FOSS as completed"
	mark_foss_pending.short_description = "Mark selected FOSS categories as pending"
	actions = [mark_foss_completed, mark_foss_pending]

class TutorialDetailAdmin(admin.ModelAdmin):
	exclude = ('user',)
	list_display = ('foss', 'tutorial', 'level', 'order', 'updated', 'user')
	list_filter = ('foss', 'level', 'updated', 'user')
	def save_model(self, request, obj, form, change):
		obj.user = request.user
		obj.save()
		try:
			foss_dir = settings.BASE_DIR + '/static/creation/uploads/' + str(obj.id)
			os.mkdir(foss_dir)
			os.mkdir(foss_dir + '/resources')
		except:
			print "Foss directory already exists..."

class ContributorRoleAdmin(admin.ModelAdmin):
	form = ContributorRoleForm
	list_display = ('user', 'foss_category', 'language', 'status', 'created', 'updated')
	#exclude = ('created', 'updated')

	def mark_contributor_disabled(self, request, queryset):
		rows_updated = queryset.update(status=0)
		if rows_updated == 1:
			message_bit = "1 contributor role was"
		else:
			message_bit = "%s contributor roles were"
		self.message_user(request, "%s successfully disabled." % message_bit)

	def mark_contributor_active(self, request, queryset):
		rows_updated = queryset.update(status=1)
		if rows_updated == 1:
			message_bit = "1 contributor role was"
		else:
			message_bit = "%s contributor roles were"
		self.message_user(request, "%s successfully activated." % message_bit)
	mark_contributor_active.short_description = "Mark selected contributor roles as active"
	mark_contributor_disabled.short_description = "Mark selected contributor roles as disabled"
	actions = ['mark_contributor_active', 'mark_contributor_disabled']

class DomainReviewerRoleAdmin(admin.ModelAdmin):
	form = DomainReviewerRoleForm
	list_display = ('user', 'foss_category', 'language', 'status', 'created', 'updated')
	#exclude = ('created', 'updated')

	def mark_domain_reviewer_disabled(self, request, queryset):
		rows_updated = queryset.update(status=0)
		if rows_updated == 1:
			message_bit = "1 domain reviewer role was"
		else:
			message_bit = "%s domain reviewer roles were"
		self.message_user(request, "%s successfully disabled." % message_bit)

	def mark_domain_reviewer_active(self, request, queryset):
		rows_updated = queryset.update(status=1)
		if rows_updated == 1:
			message_bit = "1 domain reviewer role was"
		else:
			message_bit = "%s domain reviewer roles were"
		self.message_user(request, "%s successfully activated." % message_bit)
	mark_domain_reviewer_active.short_description = "Mark selected domain reviewer roles as active"
	mark_domain_reviewer_disabled.short_description = "Mark selected domain reviewer roles as disabled"
	actions = ['mark_domain_reviewer_active', 'mark_domain_reviewer_disabled']

class QualityReviewerRoleAdmin(admin.ModelAdmin):
	form = QualityReviewerRoleForm
	list_display = ('user', 'foss_category', 'language', 'status', 'created', 'updated')
	#exclude = ('created', 'updated')

	def mark_quality_reviewer_disabled(self, request, queryset):
		rows_updated = queryset.update(status=0)
		if rows_updated == 1:
			message_bit = "1 quality reviewer role was"
		else:
			message_bit = "%s quality reviewer roles were"
		self.message_user(request, "%s successfully disabled." % message_bit)

	def mark_quality_reviewer_active(self, request, queryset):
		rows_updated = queryset.update(status=1)
		if rows_updated == 1:
			message_bit = "1 quality reviewer role was"
		else:
			message_bit = "%s quality reviewer roles were"
		self.message_user(request, "%s successfully activated." % message_bit)
	mark_quality_reviewer_active.short_description = "Mark selected quality reviewer roles as active"
	mark_quality_reviewer_disabled.short_description = "Mark selected quality reviewer roles as disabled"
	actions = ['mark_quality_reviewer_active', 'mark_quality_reviewer_disabled']

admin.site.register(Language, LanguageAdmin)
admin.site.register(Foss_Category, FossCategoryAdmin)
admin.site.register(Tutorial_Detail, TutorialDetailAdmin)
admin.site.register(Contributor_Role, ContributorRoleAdmin)
admin.site.register(Domain_Reviewer_Role, DomainReviewerRoleAdmin)
admin.site.register(Quality_Reviewer_Role, QualityReviewerRoleAdmin)
