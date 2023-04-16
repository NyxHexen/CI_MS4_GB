from django.shortcuts import render, redirect
from django.http import QueryDict, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
from django.contrib import messages

from ci_ms4_gamebox.utils import get_or_none
from games.models import (Game, Genre,
                          Tag, Platform, Feature, DLC)
from .utils import sort_by

from decimal import Decimal
from datetime import datetime

import json


def games(request):
    games = Game.objects.all()
    dlcs = DLC.objects.all()

    filter_dict = QueryDict(mutable=True)

    if "filter" in request.GET:
        """
        Lambda is an anonymous function, by defining a dictionary which holds a query key as a key received via request.GET
        passed on from the filter form and a value which is a function, it allows us to easily filter sets
        by running them through a for loop and using value(queryset, param) to apply the filter.
        The dictionary structure of the filter also improves readability, so long lambda functions are kept simple,
        and maintainability.
        """
        filter_condition = {
            "sale_only": lambda queryset, *args: queryset.filter(
                in_promo=True, promo__active=True
            ),
            "hide_extras": lambda queryset, *args: queryset.exclude(
                required_game__isnull=False
            )
            if all(hasattr(obj, "required_game") for obj in queryset.all())
            else queryset,
            "price_range": lambda queryset, param: queryset.filter(
                final_price__gte=Decimal(param[0]), final_price__lte=Decimal(param[1])
            )
            if len(param) == 2
            else queryset,
            "genres_filter": lambda queryset, param: queryset.filter(
                genres__slug__in=param
            ).distinct()
            if not all(hasattr(obj, "required_game") for obj in queryset.all())
            else queryset.filter(required_game__genres__slug__in=param).distinct(),
            "tags_filter": lambda queryset, param: queryset.filter(
                tags__slug__in=param
            ).distinct(),
            "platforms_filter": lambda queryset, param: queryset.filter(
                platforms__slug__in=param
            ).distinct()
            if not all(hasattr(obj, "required_game") for obj in queryset.all())
            else queryset.filter(required_game__platforms__slug__in=param).distinct(),
            "features_filter": lambda queryset, param: queryset.filter(
                features__slug__in=param
            ).distinct(),
            "date_range": lambda queryset, param: queryset.filter(
                release_date__gte=datetime(int(param[0]), 1, 1),
                release_date__lte=datetime(int(param[1]), 12, 31),
            )
            if len(param) == 2
            else queryset,
        }

        filtered_games = games
        filtered_dlcs = dlcs

        for key, value in filter_condition.items():
            if key in request.GET:
                if filter_dict.get(key) is None:
                    filter_dict.update({f"{key}": f"{request.GET.get(key)}"})
                filter_param = (
                    request.GET.getlist(key)[0].split(",")
                    if key.endswith("_filter") or key.endswith("_range")
                    else request.GET.get(key)
                )

                filtered_games = (
                    value(filtered_games, filter_param) if len(games) > 0 else list()
                )
                filtered_dlcs = value(filtered_dlcs, filter_param) if len(dlcs) > 0 else list()
                print(filtered_games)

        if "sort_by" in request.GET:
            filter_dict.update({f"sort_by": f'{request.GET.get("sort_by")}'})

        filtered_results = sort_by(
            request.GET.get("sort_by"), filtered_games, filtered_dlcs
        )
        paginator = Paginator(filtered_results, 20)
    else:
        if "sort_by" in request.GET:
            filter_dict.update({f"sort_by": f'{request.GET.get("sort_by")}'})
        sorted_games = sort_by(request.GET.get("sort_by"), games, dlcs)
        paginator = Paginator(sorted_games, 20)

    page_number = request.GET.get("page")

    try:
        page = paginator.get_page(page_number)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)

    paginator_iter = range(1, page.paginator.num_pages + 1)

    genres = Genre.objects.all()
    tags = Tag.objects.all()
    platforms = Platform.objects.all()
    features = Feature.objects.all()

    context = {
        "page": page,
        "paginator_iter": paginator_iter,
        "genres": genres,
        "tags": tags,
        "platforms": platforms,
        "features": features,
    }

    if "filter" in request.GET:
        items = filtered_results or list(games) + list(dlcs)
    else:
        items = sorted_games or list(games) + list(dlcs)

    context["price_slider_ceil"] = float(
        max(items, key=lambda item: item.final_price).final_price
    )

    if "filter" in request.GET or "sort_by" in request.GET:
        context["filter_dict"] = urlencode(filter_dict)
    
    return render(request, "games/index.html", context)


def game(request, model_name, game_id):
    game = Game.objects.get(id=game_id) if model_name == 'game' else DLC.objects.get(id=game_id)
    media = game.media.exclude(name__icontains='COVER')
    rating_count = game.ratingset.userrating_set.exclude(value=0).count

    context = {
        'game': game,
        'media': media,
        'rating_count': rating_count,
    }

    if request.user.is_authenticated:
        user_rating = get_or_none(game.ratingset.userrating_set, user=request.user)
        context['user_rating'] = user_rating.value if user_rating is not None else None
    return render(request, "games/game.html", context)

@csrf_exempt
@login_required
@require_POST
def set_game_rating(request, model_name, game_id):
    if request.user.is_authenticated:
        game = Game.objects.get(id=game_id) if model_name == 'game' else DLC.objects.get(id=game_id)
        user_rating = game.ratingset.userrating_set.get_or_create(user=request.user)
        user_rating[0].value = json.loads(request.body)["rating"]
        user_rating[0].save()
        return JsonResponse({'new_game_rating': game.ratingset.user_rating_calc(), 'error': ''})
    else:
        return JsonResponse({'error': 'guest'})