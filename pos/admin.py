from django.contrib import admin
from .models import *

class InvoiceAdmin(admin.ModelAdmin):
    list_filter = ('company',)
    list_display = ['number','price','quanty']
    search_fields = ['number']

admin.site.register(POS,InvoiceAdmin)
admin.site.register(Payment_Form_Invoice_POS)
admin.site.register(Wallet_POS)
admin.site.register(Credit_Note_POS)
admin.site.register(History_Invoice_POS)

