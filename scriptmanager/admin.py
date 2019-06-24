from .models import Scripts, ScriptDetails,Comments
from django.contrib import admin
from django.contrib import admin
from reversion.admin import VersionAdmin

admin.site.register(Scripts)
admin.site.register(Comments)

@admin.register(ScriptDetails)
class ScriptsDetailsAdmin(VersionAdmin):
    pass
