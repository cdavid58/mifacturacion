from django.contrib import admin
from .models import *


class InvoiceAdmin(admin.ModelAdmin):
    list_filter = ('company',)
    list_display = ['number','description','price','quanty']
    search_fields = ['number','date','description']


admin.site.register(Invoice,InvoiceAdmin)
admin.site.register(Payment_Form_Invoice)
admin.site.register(Consecutive_POS)
admin.site.register(Consecutive_Elec)
admin.site.register(Wallet)
admin.site.register(Consecutive_CreditNote)
admin.site.register(Credit_Note)
admin.site.register(History_Invoice)
