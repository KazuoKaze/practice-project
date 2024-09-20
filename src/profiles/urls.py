from django.urls import path
from .views import profile_list_view, specific_profile

urlpatterns = [
    path('profiles/', profile_list_view, name='profile_list_view'),
    path('profiles/<str:username>/', specific_profile, name='specific_profile')
]