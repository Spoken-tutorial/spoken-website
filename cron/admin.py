from django.contrib import admin

from .models import AsyncCronMail



class AsyncCronMailAdmin(admin.ModelAdmin):
    exclude = ('uploaded_by',)


admin.site.register(AsyncCronMail, AsyncCronMailAdmin)