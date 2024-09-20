from django.shortcuts import render

# Create your views here.

def login_view(request):
    return render(request, 'auth/login.html')

# def register_login(request):
#     return render(request, 'auth/register.html')