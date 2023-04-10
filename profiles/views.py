from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import UserProfile
from .forms import BillingAddressForm

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


@login_required
def billing_address(request):
    profile = UserProfile.objects.get(user=request.user)
    form = BillingAddressForm(instance=profile)

    if request.method == "POST":
        form_data = {
            "default_phone_number": request.POST["default_phone_number"],
            "default_country": request.POST["default_country"],
            "default_postcode": request.POST["default_postcode"],
            "default_town_or_city": request.POST["default_town_or_city"],
            "default_street_address1": request.POST["default_street_address1"],
            "default_street_address2": request.POST["default_street_address2"],
            "default_county": request.POST["default_county"],
        }
        
        f = BillingAddressForm(form_data, initial=form.initial)

        if f.is_valid():
            if f.has_changed():
                for data in f.changed_data:
                    setattr(profile, data, form_data[data])
                    profile.save()
                return redirect(reverse("billing_address"))

    context = {
        'user_profile': profile,
        'form': form,
    }
    return render(request, 'profiles/default_address.html', context)