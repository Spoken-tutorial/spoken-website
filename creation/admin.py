
# Standard Library
from builtins import str
import os

# Third Party Stuff
from django.conf import settings
from django.contrib import admin

# Spoken Tutorial Stuff
from creation.forms import *
from creation.models import *


class LanguageAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('name', 'created', 'updated', 'user')

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


class FossSuperCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'updated')


class FossCategoryAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('foss', 'id', 'status', 'created', 'updated', 'user')
    filter_horizontal = ['category']

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def mark_foss_completed(self, request, queryset):
        rows_updated = queryset.update(status=1)
        if rows_updated == 1:
            message_bit = "1 FOSS category was"
        else:
            message_bit = "%s FOSS categories were" % rows_updated
        self.message_user(
            request, "%s successfully marked as completed." % message_bit)

    def mark_foss_pending(self, request, queryset):
        rows_updated = queryset.update(status=0)
        if rows_updated == 1:
            message_bit = "1 FOSS category was"
        else:
            message_bit = "%s FOSS categories were" % rows_updated
        self.message_user(
            request, "%s successfully marked as pending." % message_bit)

    mark_foss_completed.short_description = "Mark selected FOSS as completed"
    mark_foss_pending.short_description = "Mark selected FOSS categories as pending"
    actions = [mark_foss_completed, mark_foss_pending]

    class Media:
        js = ('admin/js/update_tutorials.js',)

class BrochurePageInline(admin.TabularInline):
    model = BrochurePage


class BrochureDocumentAdmin(admin.ModelAdmin):
    inlines = [BrochurePageInline, ]


class TutorialDetailAdmin(admin.ModelAdmin):
    form = AvailableFossForm
    exclude = ('user',)
    list_display = ('foss', 'tutorial', 'level', 'order', 'updated', 'user')
    list_filter = ('updated', 'level', 'foss')

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.tutorial = obj.tutorial.strip()
        obj.save()
        try:
            foss_dir = settings.MEDIA_ROOT + '/videos/' + \
                str(obj.foss_id) + '/' + str(obj.id) + '/resources'
            os.makedirs(foss_dir)
        except:
            print("Tutorial directories already exists...")


class ContributorRoleAdmin(admin.ModelAdmin):
    form = ContributorRoleForm
    list_display = ('user','foss_category','tutorial_detail', 'language',
                    'status', 'created', 'updated',)
    list_filter = ('updated', 'language', 'foss_category')

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

    class Media:
        js = ('admin/js/ajax-contributor.js',)


class DomainReviewerRoleAdmin(admin.ModelAdmin):
    form = DomainReviewerRoleForm
    list_display = ('user', 'foss_category', 'language',
                    'status', 'created', 'updated')
    list_filter = ('updated', 'language', 'foss_category')

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

    class Media:

        js = ('admin/js/domain_reviewer_languages.js', )


class QualityReviewerRoleAdmin(admin.ModelAdmin):
    form = QualityReviewerRoleForm
    list_display = ('user', 'foss_category', 'language',
                    'status', 'created', 'updated')
    list_filter = ('updated', 'language', 'foss_category')

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
    actions = ['mark_quality_reviewer_active',
               'mark_quality_reviewer_disabled']

    class Media:

            js = ('admin/js/quality_reviewer_languages.js', )

class FossAvailableForTestAdmin(admin.ModelAdmin):
    form = FossAvailableForTestForm
    fields = ['foss', 'language', 'status']
    list_display = ('foss', 'language', 'status', 'created')
    list_filter = ('language',)


class FossAvailableForWorkshopAdmin(admin.ModelAdmin):
    fields = ['foss', 'language', 'status']
    list_display = ('foss', 'language', 'status', 'created')
    list_filter = ('language',)


class LanguagManagerAdmin(admin.ModelAdmin):

    form = LanguageManagerForm
    fields = ['user', 'language', 'status']
    list_display = ('user', 'language', 'status')
    list_filter = ('language', )

    class Media:

        js = ('admin/js/not_contributor_langs.js', )


class CollaborateAdmin(admin.ModelAdmin):
    list_display = ('user','foss_name','language','created',)        


admin.site.register(Language, LanguageAdmin)
admin.site.register(FossCategory, FossCategoryAdmin)
admin.site.register(FossSuperCategory, FossSuperCategoryAdmin)
admin.site.register(TutorialDetail, TutorialDetailAdmin)
admin.site.register(ContributorRole, ContributorRoleAdmin)
admin.site.register(DomainReviewerRole, DomainReviewerRoleAdmin)
admin.site.register(QualityReviewerRole, QualityReviewerRoleAdmin)
admin.site.register(FossAvailableForTest, FossAvailableForTestAdmin)
admin.site.register(FossAvailableForWorkshop, FossAvailableForWorkshopAdmin)
admin.site.register(BrochureDocument, BrochureDocumentAdmin)
admin.site.register(LanguageManager, LanguagManagerAdmin)
admin.site.register(Collaborate, CollaborateAdmin)

