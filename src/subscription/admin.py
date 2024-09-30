from django.contrib import admin
from .models import Subscription, SubscriptionPlan, Payment

admin.site.register(Subscription)
admin.site.register(SubscriptionPlan)
admin.site.register(Payment)
# Register your models here.
