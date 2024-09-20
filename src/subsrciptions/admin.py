from django.contrib import admin
from .models import Subscriptions, UserSubrictions, SubscriptionsPrice




# Register your models here.

class SubscriptionsPrice(admin.TabularInline):
    model = SubscriptionsPrice
    readonly_fields = ["stripe_id"]
    can_delete = False
    extra = 0

class SubscriptionsAdmin(admin.ModelAdmin):
    inlines = [SubscriptionsPrice]
    list_display = ['name', 'active']
    readonly_fields = ['stripe_id']



admin.site.register(Subscriptions, SubscriptionsAdmin)
admin.site.register(UserSubrictions)