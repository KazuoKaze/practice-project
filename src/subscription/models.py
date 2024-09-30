from django.db import models
from django.conf import settings
import razorpay
from django.urls import reverse

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def calculate_credit_worth():
    price_per_credit = (99 + (169 / 3) + (299 / 7)) / 3
    return price_per_credit

def calculate_credits_by_price(price):
    if price == 99:
        return 1
    elif price == 169:
        return 3
    elif price == 299:
        return 7
    else:
        return int(price // calculate_credit_worth()) 


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    credits = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.credits} pics for ${self.price}"
    
    @property
    def display_sub_name(self):
        return self.name
    
    @property
    def display_credits(self):
        return self.credits
    
    def get_checkout_url(self):
        return reverse('create_order', kwargs={'plan_id': self.id})

    def save(self, *args, **kwargs):
        # Calculate credits automatically based on the price
        self.credits = calculate_credits_by_price(self.price)
        super().save(*args, **kwargs)

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)    
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=False)
    credits = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.plan:
            return f"{self.user.username} - {self.plan.name}"
        else:
            return f"{self.user.username} - No plan"

    def deduct_credit(self):
        if self.credits > 0:
            self.credits -= 1
            if self.credits == 0:
                self.active = False
            self.save()
        else:
            raise ValueError('Not enough credit')

    def add_credit(self, credit_amount):
        self.credits += credit_amount
        if self.credits > 0:
            self.active = True
        self.save()

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        plan_name = self.subscription_plan.name if self.subscription_plan else "No Plan"
        return f"Payment {self.id} by {self.user.username} for {plan_name}"