from django.shortcuts import render
import requests


def games(request):
    context = {
    }
    return render(request, 'games/index.html', context)