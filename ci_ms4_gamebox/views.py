# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from django.shortcuts import render
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def handler400(request, exception):
    return render(request, 'custom_errors/400.html', status=400)

def handler403(request, exception):
    return render(request, 'custom_errors/403.html', status=403)

def handler404(request, exception):
    return render(request, 'custom_errors/404.html', status=404)

def handler500(request):
    return render(request, status=500, template_name='custom_errors/500.html')