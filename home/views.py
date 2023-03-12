from django.shortcuts import render
from games.models import Game, DLC
from promo.models import Promo
import datetime as dt

import random


def index(request):
    """ A view to return the index page """
    carousel = list(Game.objects.filter(carousel=True))
    carousel += list(Promo.objects.filter(carousel=True))
    carousel += list(DLC.objects.filter(carousel=True))

    featured = list(Game.objects.filter(featured=True))
    if len(featured) > 4:
        featured = random.sample(featured, 4)
    
    dotd_queryset = Game.objects.filter(in_promo=True)
    target_date = dt.date.today() + dt.timedelta(days=2)
    dotd_nearest = list()
    iter_count = 0
    while len(dotd_nearest) < 4:
        iter_count += 1

        for value in dotd_queryset:
            if value.promo.end_date.date() <= target_date:
                if value not in featured and value not in dotd_nearest:
                    dotd_nearest.append(value)

        if iter_count == 13:
            break
        elif iter_count == 8:
            target_date = target_date + dt.timedelta(days=2)
        elif iter_count == 4:
            target_date = target_date + dt.timedelta(days=2)


    context = {
        'carousel': carousel,
        'featured': featured,
        'dotd': dotd_nearest
    }
    return render(request, 'home/index.html', context)