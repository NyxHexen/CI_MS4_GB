from django.shortcuts import render


def promo(request):
    context = {
    }
    return render(request, 'promo/index.html', context)