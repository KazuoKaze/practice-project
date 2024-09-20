from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from subsrciptions.models import Subscriptions

User = get_user_model()

@login_required
def specific_profile(request, username):
    context = {
        'username': username,
    }
    return render(request, 'profiles/specific_profile.html', context)

@login_required
def profile_list_view(request):
    # print(User.has_perm(self=User, perm))
    context = {
        'object_list': User.objects.filter(is_active=True)
    }
    return render(request, 'profiles/list.html', context)
    
