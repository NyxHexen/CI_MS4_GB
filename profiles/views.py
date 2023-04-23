# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

# Internal
from ci_ms4_gamebox.utils import get_or_none

# Local
from .models import UserProfile
from .forms import BillingAddressForm, NewsletterForm
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@login_required
def myprofile(request):
    profile = UserProfile.objects.get(
        user=request.user
        )

    if request.POST:
        username = request.user.username
        email = request.user.email
        first_name = request.POST.get('myprofile_first_name')
        last_name = request.POST.get('myprofile_last_name')
        User.objects.filter(
            username=username,
            email=email,
        ).update(
            first_name=first_name,
            last_name=last_name
            )

    context = {
        'profile': profile,
    }
    return render(request, 'profiles/index.html', context)


@login_required
def billing_address(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except Exception:
        messages.error(
            request,
            "System Malfunction! Please try again later."
            )
        return redirect('profile')
    
    form = BillingAddressForm(instance=profile)

    if request.method == "POST":
        form_data = {
            "default_phone_number": request.POST.get("default_phone_number", ""),
            "default_country": request.POST.get("default_country", ""),
            "default_postcode": request.POST.get("default_postcode", ""),
            "default_town_or_city": request.POST.get("default_town_or_city", ""),
            "default_street_address1": request.POST.get("default_street_address1", ""),
            "default_street_address2": request.POST.get("default_street_address2", ""),
            "default_county": request.POST.get("default_county", ""),
        }
        
        f = BillingAddressForm(
            form_data,
            initial=form.initial
            )

        if f.is_valid():
            if f.has_changed():
                for data in f.changed_data:
                    try:
                        setattr(profile,
                                data,
                                form_data[data]
                                )
                        profile.save()
                    except Exception:
                        messages.error(
                            request,
                            'System Malfunction! Please try again later!'
                            )
                        break
                messages.success(
                    request,
                    "Your billing address has been updated!"
                    )
                return redirect(reverse("billing_address"))

    context = {
        'user_profile': profile,
        'form': form,
    }
    return render(request, 'profiles/default_address.html', context)

@require_POST
def newsletter_sub(request):
    if not request.user.is_authenticated:
        messages.error(
            request,
            "You must login to subscribe to our newsletter. Don't have \
            an account? Why not sign up!")
        return redirect(reverse('account_login'))
    form = NewsletterForm(request.POST)

    if form.is_valid():
        user = get_or_none(
            User,
            email=form.cleaned_data['subscription_email']
            )
        if (user is not None
            and request.user == user
            ):
            if request.user.userprofile.newsletter_sub:
                messages.info(
                    request,
                    "You are already subscribed!\
                        If you are not receiving our emails, please reach out to us!")
            else:
                user.userprofile.newsletter_sub = True
                user.userprofile.save()
                messages.success(
                    request,
                    "Thank you for subscribing to our newsletter.\
                        Our welcome letter will be with you shortly!")
        elif user is not None and request.user != user:
            messages.error(
                request,
                'This e-mail address is already associated with another account.'
                )
        elif user is None:
            # https://stackoverflow.com/questions/2053258/how-do-i-output-html-in-a-message-in-the-new-django-messages-framework
            messages.info(
                request,
                "Newsletter can only be sent to your primary e-mail address.\
                    If you wish to change your primary address, click\
                    <a class=\"text-light\" href=\"{% url \'accounts:email\'%}\">here</a>.",
                    extra_tags='safe'
                    )

    redirect_url = request.POST.get('newsletter_redirect')
    return redirect(redirect_url)