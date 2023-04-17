from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import QueryDict
from django.core.paginator import Paginator, EmptyPage
from urllib.parse import urlencode
from django.contrib import messages
from decimal import Decimal

from ci_ms4_gamebox.utils import get_or_none
from games.views import sort_by
from games.models import Media
from games.models import Game, DLC
from promo.models import Promo
from .forms import PromoForm

import random
import datetime as dt
import pytz

def promo(request, promo_id):
    promo = get_object_or_404(Promo, id=promo_id)
    if not promo.active and not request.user.is_staff:
        messages.error(request, 'The Sale you are looking for is not currently available! Please try again later or \
                       contact us for further information!')
        return redirect("/")
    
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
    if not request.user.is_staff:
        messages.info(request, 'Super Secret Page of Awesomeness! Unauthorized access prohibited!')
        return redirect("/")
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
        media = request.POST.get('media') or None
        if form.is_valid():
            apply_to_game_list = post_copy.getlist('apply_to_game', {})
            apply_to_dlc_list = post_copy.getlist('apply_to_dlc', {})
            if submit_option == 'preview':
                try:
                    dummy_promo = {
                            'id': 1000,
                            'active': request.POST.get('active') or None,
                            'name': request.POST.get('name') or None,
                            'short_description': request.POST.get('short_description') or None,
                            'long_description': request.POST.get('long_description') or None,
                            'media': get_or_none(Media, id=media),
                        }
                    
                    for id in request.POST.getlist('apply_to_game'):
                        game = Game.objects.get(id=id)
                        discount = request.POST.get(f'game_discount-game_{id}') or game.promo_percentage                    
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
                        discount = request.POST.get(f'game_discount-dlc_{id}') or game.promo_percentage
                        if not game.in_promo:
                            game.promo_percentage = discount
                            game.final_price = round(game.base_price - game.base_price * (Decimal(discount) / 100), 2)
                            game_list.append(game)
                            real_game_list.append(game)
                        else:
                            apply_to_dlc_list.remove(id)
                    post_copy.setlist('apply_to_dlc', apply_to_dlc_list)

                    for i in range(len(game_list), 8, 1):
                        game_list.append(dummy_game)
                except Exception as e:
                    messages.error(request, f'{e}')
            elif submit_option == 'save':
                try:
                    new_promo = form.save()
                    new_promo = Promo.objects.get(id=new_promo.id)
                    for id in post_copy.getlist('apply_to_game', {}):
                        game = Game.objects.filter(id=id)
                        game.update(
                            in_promo=True, 
                            promo=new_promo, 
                            promo_percentage=post_copy.get(f'game_discount-game_{game[0].id}'))
                        new_promo.apply_to_game.add(game[0])
                    for id in post_copy.getlist('apply_to_dlc', {}):
                        dlc = DLC.objects.filter(id=id)
                        dlc.update(
                            in_promo=True, 
                            promo=new_promo, 
                            promo_percentage=post_copy.get(f'game_discount-dlc_{dlc[0].id}'))
                        new_promo.apply_to_dlc.add(dlc[0])
                    new_promo.save()
                    return redirect(reverse('promo', kwargs={'promo_id': new_promo.id}))
                except Exception as e:
                    messages.error(request, f'{e}')
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


def promo_edit(request, promo_id):
    if not request.user.is_staff:
        messages.info(request, 'Super Secret Page of Awesomeness! Unauthorized access prohibited!')
        return redirect("/")
    promo = get_object_or_404(Promo, id=promo_id)
    promo.active = False
    promo.save()

    submit_option = request.POST.get('submit_option')

    game_lists = [list(qset) for qset in [promo.apply_to_game.all(), promo.apply_to_dlc.all()]]
    game_list = [item for sublist in game_lists for item in sublist]

    form = PromoForm(instance=promo)

    if request.method == "POST":
        f = PromoForm(request.POST, instance=promo)
        if f.is_valid():
            if submit_option in ['save', 'cont', 'activate']:
                promo = f.save()
                promo = Promo.objects.get(id=promo.id)
                if f.has_changed():
                    for data in f.changed_data:
                        if data == 'media':
                            if data in ['start_date', 'end_date']:
                                setattr(
                                    promo,
                                    data,
                                    pytz.utc.localize(dt.datetime.strptime(request.POST[data], "%Y-%m-%d %H:%M:%S"))
                                    )
                for id in request.POST.getlist('apply_to_game', {}):
                    game = Game.objects.filter(id=id)
                    game.update(
                        in_promo=True, 
                        promo=promo, 
                        promo_percentage=request.POST.get(f'game_discount-game_{game[0].id}', 0)
                    )

                for id in request.POST.getlist('apply_to_dlc', {}):
                    dlc = DLC.objects.filter(id=id)
                    dlc.update(
                        in_promo=True, 
                        promo=promo, 
                        promo_percentage=request.POST.get(f'game_discount-dlc_{dlc[0].id}', 0)
                    )
            else:
                post_copy = request.POST.copy()
                game_list = list()
                apply_to_game_list = post_copy.getlist('apply_to_game', {})
                apply_to_dlc_list = post_copy.getlist('apply_to_dlc', {})
                form = PromoForm(post_copy, instance=promo)

                for id in request.POST.getlist('apply_to_game'):
                    game = Game.objects.get(id=id)
                    discount = request.POST.get(f'game_discount-game_{id}') or game.promo_percentage                    
                    if not game.in_promo:
                        game.promo_percentage = discount
                        game.final_price = round(game.base_price - game.base_price * (Decimal(discount) / 100), 2)
                        game_list.append(game)
                    else:
                        apply_to_game_list.remove(id)
                post_copy.setlist('apply_to_game', apply_to_game_list)

                for id in request.POST.getlist('apply_to_dlc'):
                    game = DLC.objects.get(id=id)
                    discount = request.POST.get(f'game_discount-dlc_{id}') or game.promo_percentage
                    if not game.in_promo:
                        game.promo_percentage = discount
                        game.final_price = round(game.base_price - game.base_price * (Decimal(discount) / 100), 2)
                        game_list.append(game)
                    else:
                        apply_to_dlc_list.remove(id)
                post_copy.setlist('apply_to_dlc', apply_to_dlc_list)

        # Remove time zone information from start_date and end_date
        start_date = promo.start_date.replace(tzinfo=None)
        end_date = promo.end_date.replace(tzinfo=None)
        now = dt.datetime.now().replace(microsecond=0)

        
        if (start_date.__le__(now) and now.__lt__(end_date)
            ) and (
            submit_option.__eq__('activate')
            ) and (
            promo.apply_to_game.count().__ne__(0) or promo.apply_to_dlc.count().__ne__(0)
            ):
            promo.active = True
            # promo.save()
            return redirect(reverse('promo', kwargs={'promo_id': promo_id}))
        elif submit_option.__eq__('cont'):
            return redirect(reverse('promo_edit', kwargs={'promo_id': promo_id}))
        elif submit_option.__eq__('save'):
            return redirect(reverse('promo', kwargs={'promo_id': promo_id}))
        
    paginator = Paginator(game_list, 8)

    page_number = request.GET.get("page")

    try:
        page = paginator.get_page(page_number)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)


    context = {
        'promo': promo,
        'game_list': game_list,
        'form': form,
        'page': page,
    }
    return render(request, 'promo/index.html', context)
