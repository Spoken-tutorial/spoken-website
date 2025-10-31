from django.contrib import admin
from .models import Payee, SchoolDonation, SchoolDonationTransactions
# Register your models here.

class SchoolDonationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact', 'state', 'city', 'amount', 'created', 'mail_status')
    search_fields = ('name', 'email', 'contact', 'state__name', 'city__name', 'reqId')
    list_filter = ('state', 'mail_status', 'created')
    ordering = ('-created',)
    # Fields to display when adding or editing a record
    fields = ('name', 'email', 'contact', 'state', 'city', 'address', 'amount', 'note', 'mail_status', 'mail_response','reqId')
    readonly_fields = ('name', 'email', 'contact', 'state', 'city', 'address', 'amount', 'note', 'mail_status', 'mail_response','reqId')

class SchoolDonationTransactionsAdmin(admin.ModelAdmin):
    list_display = (  'reqId', 'transId', 'refNo', 'provId', 'status', 'amount', 'msg', 'created')
    search_fields = ('transId', 'refNo', 'status', 'msg', 'reqId')
    list_filter = ('status', 'created')
    ordering = ('-created',)
    # Fields to display when adding or editing a record
    fields = (  'reqId', 'transId', 'refNo', 'provId', 'status', 'amount', 'msg', 'created')
    readonly_fields = (  'reqId', 'transId', 'refNo', 'provId', 'status', 'amount', 'msg', 'created')


admin.site.register(Payee)
admin.site.register(SchoolDonation, SchoolDonationAdmin)
admin.site.register(SchoolDonationTransactions, SchoolDonationTransactionsAdmin)