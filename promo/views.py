from django.shortcuts import render
from promo.models import Promo


def promo(request, promo_id):
    promo = Promo.objects.get(id=promo_id)
    context = {
        'promo': promo,
    }
    return render(request, 'promo/index.html', context)