from django.shortcuts import render, redirect
from django.urls import reverse
from games.models import Game, DLC
from promo.models import Promo
from django.http import QueryDict
from django.core.paginator import Paginator, EmptyPage
from urllib.parse import urlencode

from games.views import sort_by
from games.models import Media
from .forms import PromoForm
from decimal import Decimal

import random

def promo(request, promo_id):
    promo = Promo.objects.get(id=promo_id)
    # Convert each argument to a list
    game_lists = [list(qset) for qset in [promo.apply_to_game.all(), promo.apply_to_dlc.all()]]
    # Flatten the list of lists into a single list
    game_list = [item for sublist in game_lists for item in sublist]
    filter_dict = QueryDict(mutable=True)

    if "sort_by" in request.GET:
        filter_dict.update({f"sort_by": f'{request.GET.get("sort_by")}'})
        sorted_games = sort_by(request.GET.get("sort_by"), promo.apply_to_game.all(), promo.apply_to_dlc.all())
        paginator = Paginator(sorted_games, 4)
    else:
        paginator = Paginator(game_list, 4)

    page_number = request.GET.get("page")

    try:
        page = paginator.get_page(page_number)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)

    context = {
        "game_list": game_list,
        "page": page,
        'promo': promo,
    }

    if "sort_by" in request.GET:
        context["filter_dict"] = urlencode(filter_dict)
    
    return render(request, 'promo/index.html', context)


def promo_add(request):
    game_list = list()
    real_game_list = list()

    dummy_game = {
        'name': 'Dummy Game',
        'promo_percentage': lambda: random.randint(1, 90),
        'base_price': lambda: f'{(random.uniform(0.00, 49.99)):.2f}',
        'final_price': lambda: f'{(random.uniform(0.00, 49.99)):.2f}',
        'model_name': 'game',
        'id': 1,
    }

    dummy_promo = {
        'id': 1000,
    }

    form = PromoForm()

    if request.method == "POST":
        post_copy = request.POST.copy()
        form = PromoForm(post_copy)
        submit_option = request.POST.get('submit_option')
        if form.is_valid():
            apply_to_game_list = post_copy.getlist('apply_to_game', {})
            if submit_option == 'preview':
                dummy_promo = {
                        'id': 1000,
                        'active': request.POST.get('active'),
                        'name': request.POST.get('name'),
                        'short_description': request.POST.get('short_description'),
                        'long_description': request.POST.get('long_description'),
                        'media': Media.objects.get(id=request.POST['media']),
                    }
                
                for id in request.POST.getlist('apply_to_game'):
                    game = Game.objects.get(id=id)
                    discount = request.POST.get(f'game_discount-{id}') or game.promo_percentage                    
                    if not game.in_promo:
                        game.promo_percentage = discount
                        game.final_price = round(game.base_price - game.base_price * (Decimal(discount) / 100), 2)
                        game_list.append(game)
                        real_game_list.append(game)
                    else:
                        apply_to_game_list.remove(id)
                post_copy.setlist('apply_to_game', apply_to_game_list)

                for id in request.POST.getlist('apply_to_dlc'):
                    game = DLC.objects.get(id=id)
                    if not game.in_promo:
                        game.promo_percentage = discount
                        game.final_price = round(game.base_price - game.base_price * (Decimal(discount) / 100), 2)
                        game_list.append(game)
                        real_game_list.append(game)
                    else:
                        apply_to_game_list.remove(id)
                post_copy.setlist('apply_to_game', apply_to_game_list)

                for i in range(len(game_list), 8, 1):
                    game_list.append(dummy_game)
            elif submit_option == 'save':
                pass
    else:
        for i in range(len(game_list), 8, 1):
            game_list.append(dummy_game)

    paginator = Paginator(game_list, 8)

    page_number = request.GET.get("page")

    try:
        dummy_page = paginator.get_page(page_number)
    except EmptyPage:
        dummy_page = paginator.get_page(paginator.num_pages)


    context = {
        'game_list': game_list,
        'real_game_list': real_game_list,
        'promo': dummy_promo,
        'page': dummy_page,
        'form': form,
    }
    return render(request, 'promo/index.html', context)
