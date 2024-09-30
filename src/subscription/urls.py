from django.urls import path
from .views import pricing_page, create_order, verify_payment

urlpatterns = [
    path('pricing/', pricing_page, name='pricing'),
    path('create_order/<int:plan_id>/', create_order, name='create_order'),
    path('verify_payment/', verify_payment, name='verify_payment'),
]