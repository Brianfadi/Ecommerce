from django.contrib import admin
from . models import *

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Feature)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CheckoutDetail)
admin.site.register(UpdateOrder)
admin.site.register(Contact)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'phone_number','amount','status','mpesa_receipt_number','date_created','transaction_date')
    list_filter = ('status', 'date_created','transaction_date')
    search_fields = ('transaction_id','phone_number','mpesa_receipt_number')