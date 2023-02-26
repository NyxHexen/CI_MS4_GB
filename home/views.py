from django.shortcuts import render
from games.models import Game
import requests


def index(request):
    """ A view to return the index page """

    RAWG_API_KEY = "cf516d7b06284738bf24e8af5f7e4ffc"

    # response = requests.get(f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&page_size=40&page=1")
    # print(response.status_code)

    games = Game.objects.all()

    context = {
        'games': games
    }
    return render(request, 'home/index.html', context)