from django.shortcuts import render

from .models import UserProfile

# Create your views here.
def myprofile(request):
    profile = UserProfile.objects.get(user=request.user)
    context = {
        'profile': profile,
    }
    return render(request, 'profiles/index.html', context)