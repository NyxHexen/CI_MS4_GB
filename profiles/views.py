from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import UserProfile

# Create your views here.
@login_required
def myprofile(request):
    profile = UserProfile.objects.get(user=request.user)
    context = {
        'profile': profile,
    }
    return render(request, 'profiles/index.html', context)