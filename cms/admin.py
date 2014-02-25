from django.contrib import admin

from cms.models import *

class SubNavInline(admin.TabularInline):
	model = SubNav
	extra = 0

class NavAdmin(admin.ModelAdmin):
	list_display = ('nav_title', 'permalink', 'position', 'target_new', 'visible', 'created')
	inlines = [SubNavInline]

class BlockAdmin(admin.ModelAdmin):
	list_display = ('title', 'block_location', 'position', 'visible', 'created')

class PageAdmin(admin.ModelAdmin):
	list_display = ('title', 'permalink', 'target_new', 'visible', 'created')

admin.site.register(Block, BlockAdmin)
admin.site.register(Nav, NavAdmin)
admin.site.register(Page, PageAdmin)

