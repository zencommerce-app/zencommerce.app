from django.contrib import admin

from .models import *


class EtsyCountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso_country_code', 'world_bank_country_code')


class EtsyShopAdmin(admin.ModelAdmin):
    list_display = ('title', 'pk', 'etsy_id', 'user', 'uri', 'jobs_log_tail')


class EtsyListingAdmin(admin.ModelAdmin):
    list_display = ('listing_id', 'sku', 'shop', 'title', 'state')
    list_filter = ('user', 'shop',)


class EtsyReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_id', 'order_id', 'title', 'grandtotal', 'currency_code', 'was_paid', 'was_shipped')


class EtsyTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'receipt_id', 'title', 'price', 'currency_code', 'quantity', 'shipping_cost')


class EtsyUploadJobAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'status', 'user', 'shop', 'title', 'progress')
    list_filter = ('user', 'shop',)


admin.site.register(EtsyShop, EtsyShopAdmin)
admin.site.register(EtsyListing, EtsyListingAdmin)
admin.site.register(EtsyCountry, EtsyCountryAdmin)
admin.site.register(EtsyReceipt, EtsyReceiptAdmin)
admin.site.register(EtsyTransaction, EtsyTransactionAdmin)
admin.site.register(EtsyUploadJob, EtsyUploadJobAdmin)
