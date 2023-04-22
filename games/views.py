from django.shortcuts import render, redirect, get_object_or_404
from django.http import QueryDict, JsonResponse, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import EmptyResultSet
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
from django.contrib import messages

from ci_ms4_gamebox.utils import get_or_none
from games.models import (Game, Genre,
                          Tag, Platform, Feature, DLC,
                          RatingSet, Publisher, Developer,)
from .utils import sort_by
from .forms import GameForm, DLCForm, RatingForm

from decimal import Decimal
from datetime import datetime

import json


def games(request):
    try:
        games = Game.objects.all()
        if not games:
            raise EmptyResultSet
        dlcs = DLC.objects.all()
    except Exception:
        messages.error(request, "System Malfunction! Please try again later!")
        return redirect("/")

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
            ).distinct(),
            "tags_filter": lambda queryset, param: queryset.filter(
                tags__slug__in=param
            ).distinct(),
            "platforms_filter": lambda queryset, param: queryset.filter(
                platforms__slug__in=param
            ).distinct(),
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

        if "sort_by" in request.GET:
            filter_dict.update({f"sort_by": f'{request.GET.get("sort_by")}'})

        filtered_results = sort_by(
            request.GET.get("sort_by"), filtered_games, filtered_dlcs
        )
        paginator = Paginator(filtered_results, 12)
    else:
        if "sort_by" in request.GET:
            filter_dict.update({f"sort_by": f'{request.GET.get("sort_by")}'})
        sorted_games = sort_by(request.GET.get("sort_by"), games, dlcs)
        paginator = Paginator(sorted_games, 12)

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
    game = get_object_or_404(Game, id=game_id) if model_name == 'game' else get_object_or_404(DLC, id=game_id)
    
    media = game.media.exclude(name__icontains='COVER')
    rating_count = game.ratingset.userrating_set.exclude(value=0).count()

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
@require_POST
def set_game_rating(request, model_name, game_id):
    if request.user.is_authenticated:
        try:
            game = Game.objects.get(id=game_id) if model_name == 'game' else DLC.objects.get(id=game_id)
        except Exception as e:
            return HttpResponse(content=e, status=500)
        user_rating = game.ratingset.userrating_set.get_or_create(user=request.user)
        user_rating[0].value = json.loads(request.body)["rating"]
        user_rating[0].save()
        return JsonResponse({'new_game_rating': game.ratingset.user_rating_calc(), 'error': ''})
    else:
        return JsonResponse({'error': 'guest'})
    

@login_required
def game_add(request, model_name):
    if not request.user.is_staff:
        messages.info(request, '\
                      Super Secret Page of Awesomeness! Unauthorized access prohibited!')
        return redirect("/")
    
    if model_name == 'game':
        game_form = GameForm()
    else:
        game_form = DLCForm()
        
    rating_form = RatingForm()

    if request.method == 'POST':
        game_form_data = {
            'required_game': request.POST.get('required_game', {}),
            'name': request.POST.get('name', {}),
            'description': request.POST.get('description', ""),
            'storyline': request.POST.get('storyline', ""),
            'genres': request.POST.getlist('genres', {}),
            'publishers': request.POST.getlist('publishers', {}),
            'developers': request.POST.getlist('developers', {}),
            'release_date': request.POST.get('release_date', datetime.now()),
            'platforms': request.POST.getlist('platforms', {}),
            'tags': request.POST.getlist('tags', {}),
            'features': request.POST.getlist('features', {}),
            'media': request.POST.getlist('media', {}),
            'is_featured': request.POST.get('is_featured', False),
            'carousel': request.POST.get('carousel', False),
            'base_price': request.POST.get('base_price', Decimal(0.00)),
        }

        if model_name == 'game':
            game_form = GameForm(game_form_data)
        else:
            game_form = DLCForm(game_form_data)

        if game_form.is_valid():
            game = game_form.save()
            rating_form_data = {
                'game': game if game.model_name() == 'game' else {},
                'dlc': game if game.model_name() == 'dlc' else {},
                'esrb_rating': request.POST.get('esrb_rating', {}),
                'pegi_rating': request.POST.get('pegi_rating', {}),
            }
            rating_form = RatingForm(rating_form_data)
            if rating_form.is_valid():
                rating_form = rating_form.save()
                return redirect(reverse('game', kwargs={'model_name': game.model_name(),'game_id': game.id}))

    context = {
        'game_form': game_form,
        'rating_form': rating_form,
        'model_name': model_name,
    }
    return render(request, "games/game_crud.html", context)

@login_required
def game_edit(request, model_name, game_id):
    if not request.user.is_staff:
        messages.info(request, '\
                      Super Secret Page of Awesomeness! Unauthorized access prohibited!')
        return redirect("/")
    game = get_object_or_404(
        Game, id=game_id
        ) if model_name == 'game' else get_object_or_404(
        DLC, id=game_id
        )
    
    rating_set = get_object_or_404(RatingSet, id=game.ratingset.id)
    
    game_form = GameForm(
        instance=game
        ) if model_name == 'game' else DLCForm(
        instance=game
        )
    
    rating_form = RatingForm(instance=rating_set)

    if request.method == "POST":
        if model_name == 'game':
            game_form = GameForm(request.POST, instance=game)
        else:
            game_form = DLCForm(request.POST, instance=game)

        if game_form.is_valid():
            game = game_form.save(commit=False)
            discount = game.promo_percentage
            game.final_price = round(game.base_price - game.base_price * (Decimal(discount) / 100), 2)
            try:
                game.save()
                rating_form_data = {
                'game': game if game.model_name() == 'game' else {},
                'dlc': game if game.model_name() == 'dlc' else {},
                'esrb_rating': request.POST.get('esrb_rating', {}),
                'pegi_rating': request.POST.get('pegi_rating', {}),
                }
                rating_form = RatingForm(rating_form_data, instance=rating_set)
                if rating_form.is_valid():
                    rating_form = rating_form.save()
                    return redirect(reverse('game', kwargs={'model_name': game.model_name(),'game_id': game.id}))
            except Exception as e:
                messages.error(request, f'{e}')

    context = {
        'model_name': model_name,
        'game_id': game_id,
        'game_form': game_form,
        'rating_form': rating_form,
    }
    return render(request, "games/game_crud.html", context)

@login_required
def game_delete(request, model_name, game_id):
    if not request.user.is_staff:
        messages.info(request, '\
                      Super Secret Page of Awesomeness! Unauthorized access prohibited!')
        return redirect("/")
    try:
        game = (
            Game.objects.get(id=game_id) 
            if model_name == "game" else 
            DLC. objects.get(id=game_id)
            )
        game.delete()
        messages.success(request, f"{game} has been deleted successfully!")
    except Exception as e:
        messages.error(request, f'{e}')
    return redirect(reverse('games'))


def game_attrs(request, attr_id):
    game_attr = request.path.split('/')
    game_attr = [i for i in game_attr if i != ''][1]

    try:
        if game_attr == 'publishers':
            model = Publisher
            games = Game.objects.filter(publishers=attr_id)
            dlcs = DLC.objects.filter(publishers=attr_id)
        elif game_attr == 'developers':
            model = Developer
            games = Game.objects.filter(developers=attr_id)
            dlcs = DLC.objects.filter(developers=attr_id)
        elif game_attr == 'platforms':
            model = Platform
            games = Game.objects.filter(platforms=attr_id)
            dlcs = DLC.objects.filter(platforms=attr_id)

        attr = model.objects.get(id=attr_id)

    except Exception:
        messages.error(request, "System Malfunction! Please try again later!")
        return redirect('/')

    game_lists = [list(qset) for qset in [games, dlcs]]
    game_list = [item for sublist in game_lists for item in sublist]

    filter_dict = QueryDict(mutable=True)

    if "sort_by" in request.GET:
        filter_dict.update({f"sort_by": f'{request.GET.get("sort_by")}'})
        sorted_games = sort_by(request.GET.get("sort_by"), game_list)
        paginator = Paginator(sorted_games, 2)
    else:
        paginator = Paginator(game_list, 2)

    page_number = request.GET.get("page")

    try:
        page = paginator.get_page(page_number)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)

    context = {
        'attr': attr,
        'page': page,
    }

    if "sort_by" in request.GET:
        context["filter_dict"] = urlencode(filter_dict)

    return render(request, "games/game_attrs.html", context)
