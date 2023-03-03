from django.shortcuts import render
from games.models import Game


def games(request):
    games = Game.objects.all()

    context = {
        'games': games
    }
    return render(request, 'games/index.html', context)