from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.db.models.signals import post_save
import helpers.billing
# Create your models here.

User = settings.AUTH_USER_MODEL
ALLOW_CUSTOM_GROUPS = True

 
SUBSCRIPTION_PERMISSIONS = [
    ("advanced", "Advanced Perm"),
    ("pro", "Pro Prem"),
    ("basic", "Basic Prem")
]

class Subscriptions(models.Model):
    name = models.CharField(max_length=255) 
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group) 
    permisssions = models.ManyToManyField(Permission, limit_choices_to = {"content_type__app_label": "subsrciptions", "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]})
    stripe_id = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(default=-1, help_text="Ordeing for frontend")
    featured = models.BooleanField(default=True, help_text="Featured for frontend")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['order', 'featured', '-updated']
        permissions = SUBSCRIPTION_PERMISSIONS

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_id = helpers.billing.create_product(name=self.name, metadata={"subscription_planId": self.id}, raw=False)
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)

class SubscriptionsPrice(models.Model):
    class IntervalChoices(models.TextChoices):
        MONTHLY = 'month', "Monthly"
        YEARLY = 'year', "YEARLY"

    subscriptions = models.ForeignKey(Subscriptions, on_delete=models.SET_NULL, null=True)
    stripe_id = models.CharField(max_length=255, null=True, blank=True)
    interval = models.CharField(max_length=255, default=IntervalChoices.MONTHLY, choices=IntervalChoices.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    order = models.IntegerField(default=-1, help_text="Ordeing for frontend")
    featured = models.BooleanField(default=True, help_text="Featured for frontend")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subscriptions__order', 'order', 'featured', '-updated']

    @property
    def stripe_currency(self):
        return "usd"
    
    @property
    def stripe_price(self):
        return int(self.price * 100)
    
    @property
    def product_stripe_id(self):
        if not self.subscriptions:
            return None
        return self.subscriptions.stripe_id
    
    def save(self, *args, **kwargs):
        if not self.stripe_id and self.product_stripe_id is not None:
            stripe_id = helpers.billing.create_price(
                currency=self.stripe_currency,
                unit_amount=self.stripe_price,
                interval=self.interval,
                product=self.product_stripe_id,
                metadata={
                    "subscription_plan_price_id": self.id
                },
                raw=False
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)
        if self.featured and self.subscriptions:
            qs = SubscriptionsPrice.objects.filter(
                subscriptions = self.subscriptions,
                interval = self.interval
            ).exclude(id=self.id)
            qs.update(featured=False)


class UserSubrictions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscriptions = models.ForeignKey(Subscriptions, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)


def user_sub_post_save(sender, instance, *args, **kaargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription_obj = user_sub_instance.subscriptions
    groups_id = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list('id', flat=True)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)
    else:
        subs_qs = Subscriptions.objects.filter(active=True)
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id=subscription_obj.id)
        subs_groups = subs_qs.values_list('groups__id', flat=True)
        subs_groups_set = set(subs_groups)
        current_grp = user.groups.all().values_list('id', flat=True)
        groups_ids_set = set(groups_ids)
        current_grp_set = set(current_grp) - subs_groups_set
        final_grp_set = list(groups_ids_set | current_grp_set )
        user.groups.set(final_grp_set)

post_save.connect(user_sub_post_save, sender=UserSubrictions)