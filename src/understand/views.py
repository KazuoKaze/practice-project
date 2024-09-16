from django.shortcuts import render
from views.models import PageVisit

def home_page(request):
    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)
    template_name = 'home.html'
    context = {
        'title_name': 'Home',
        'qs': qs.count(),
        'page_qs': page_qs.count(),
    }
    PageVisit.objects.create(path=request.path)
    return render(request, template_name, context)

