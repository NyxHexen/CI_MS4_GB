from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import UserProfile

# Create your views here.
@login_required
def myprofile(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.POST:
        username = request.POST.get('myprofile_username')
        email = request.POST.get('myprofile_email')
        first_name = request.POST.get('myprofile_first_name')
        last_name = request.POST.get('myprofile_last_name')
        User.objects.filter(
            username=username,
            email=email,
        ).update(first_name=first_name, last_name=last_name)

    context = {
        'profile': profile,
    }
    return render(request, 'profiles/index.html', context)