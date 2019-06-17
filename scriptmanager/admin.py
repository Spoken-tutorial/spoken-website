from django.contrib import admin
from .models import Scripts, ScriptDetails,Comments
# Register your models here.
admin.site.register(Scripts)
admin.site.register(ScriptDetails)
admin.site.register(Comments)