from django.shortcuts import render

# Create your views here.
def myprofile(request):
    context = {
    }
    return render(request, 'profiles/index.html', context)