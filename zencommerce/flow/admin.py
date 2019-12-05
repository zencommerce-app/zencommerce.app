from django.contrib import admin

from .models import *


class BusinessProcessStepAdmin(admin.ModelAdmin):
    list_display = ('step', 'title', 'query')


admin.site.register(BusinessProcessStep, BusinessProcessStepAdmin)
