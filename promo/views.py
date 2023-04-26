# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.http import QueryDict
from django.core.paginator import Paginator, EmptyPage
from django.contrib import messages

# Third Party
from urllib.parse import urlencode

# Internal
from games.views import sort_by
from promo.models import Promo
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def promo(request, promo_id):
    """
    View to handle displaying of an individual Promo object.
    """
    promo = get_object_or_404(
        Promo,
        id=promo_id
        )
    if not promo.active and not request.user.is_staff:
        messages.error(
            request,
            'The Sale you are looking for is not currently available!\
                Please try again later or contact us for further assistance!'
                )
        return redirect("/")

    # Convert each argument to a list
    game_lists = [
        list(qset) for qset in [
            promo.apply_to_game.all(), promo.apply_to_dlc.all()
            ]
        ]
    # Flatten the list of lists into a single list
    game_list = [
        item for sublist in game_lists for item in sublist
        ]
    filter_dict = QueryDict(mutable=True)

    if "sort_by" in request.GET:
        filter_dict.update({f"sort_by": f'{request.GET.get("sort_by")}'})
        sorted_games = sort_by(
            request.GET.get("sort_by"),
            promo.apply_to_game.all(),
            promo.apply_to_dlc.all()
            )
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
