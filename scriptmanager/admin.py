from .models import Script, ScriptDetail, Comment
from django.contrib import admin
from django.contrib import admin
from reversion.admin import VersionAdmin

admin.site.register(Script)
admin.site.register(Comment)

@admin.register(ScriptDetail)
class ScriptsDetailsAdmin(VersionAdmin):
    pass
