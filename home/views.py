from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from games.models import Game, DLC
from promo.models import Promo
from .models import Media
from .forms import MediaForm

import random


def index(request):
    """A view to return the index page"""
    carousel = list(Game.objects.filter(carousel=True))
    carousel += list(DLC.objects.filter(carousel=True))

    is_featured = carousel
    if len(is_featured) > 4:
        cards_num = 5 if request.user_agent.is_pc else 4
        is_featured = random.sample(is_featured, cards_num)

    carousel += list(Promo.objects.filter(carousel=True))

    dotd = list(Promo.objects.filter(active=True, landing_page=True))

    if len(dotd) < 4:
        dotd_topup = list(
            Game.objects.filter(
                in_promo=True, promo__active=True, promo__landing_page=False
            )
        )
        dotd_topup += list(
            DLC.objects.filter(
                in_promo=True, promo__active=True, promo__landing_page=False
            )
        )
        dotd_topup = sorted(dotd_topup, key=lambda x: x.promo.end_date)
        dotd = dotd + dotd_topup[: 4 - len(dotd)]

    context = {"carousel": carousel, "is_featured": is_featured, "dotd": dotd}
    return render(request, "home/index.html", context)


@login_required
def media(request):
    game_lists = [list(qset) for qset in [Game.objects.all(), DLC.objects.all()]]
    game_list = [item for sublist in game_lists for item in sublist]
    filtered_game_list = [i for i in game_list if i.media.all().count() != 0]

    assigned_media_list = [
        item.id for sublist in [i.media.all() for i in filtered_game_list] for item in sublist]
    
    unassigned_media = Media.objects.exclude(id__in=assigned_media_list)

    context = {
        'filtered_game_list': filtered_game_list,
        'unassigned_media': unassigned_media,
    }
    return render(request, "media/media_list.html", context)


@login_required
def media_add(request):
    form = MediaForm()

    if request.method == "POST":
        f = MediaForm(request.POST)
        if f.is_valid():
            try:
                media = f.save()
                messages.success(request, f"{ media } has been saved successfully!")
                return redirect(reverse('home'))
            except Exception as e:
                messages.error(request, f'{e}')
    context = {
        'form': form, 
    }
    return render(request, "media/media_crud.html", context)


@login_required
def media_edit(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    form = MediaForm(instance=media)

    if request.method == "POST":
        f = MediaForm(request.POST, request.FILES, instance=media)
        if f.is_valid():
            if f.has_changed():
                try:
                    media = f.save()
                    messages.success(request, f"{ media } has been edited successfully!")
                    return redirect(reverse('media'))
                except Exception as e:
                    messages.error(request, f'{e}')

    context = {
        'form': form,
        'media': media,
    }
    return render(request, "media/media_crud.html", context)


@login_required
def media_delete(request, media_id):
    try:
        media = Media.objects.get(id=media_id)
        media.delete()
        messages.success(request, f"{media} has been deleted successfully!")
    except Exception as e:
        messages.error(request, f"{e}")
    return redirect(reverse('media'))