from django.contrib import admin
from .models import Scripts, ScriptDetails,Comments
from reversion.admin import VersionAdmin
import reversion
    # Register your models here.

reversion.register(ScriptDetails)
class BaseReversionAdmin(VersionAdmin):
 pass


admin.site.register(Scripts)
admin.site.register(ScriptDetails,BaseReversionAdmin)
admin.site.register(Comments)

