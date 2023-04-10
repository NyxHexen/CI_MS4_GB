from django.shortcuts import render
from promo.models import Promo
from django.http import QueryDict
from django.core.paginator import Paginator, EmptyPage
from urllib.parse import urlencode

from games.views import sort_by

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
