from django.shortcuts import render
from games.models import Game


def index(request):
    """ A view to return the index page """
    context = {
    }
    return render(request, 'home/index.html', context)