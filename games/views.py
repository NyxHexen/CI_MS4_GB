from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from games.models import Game


def games(request):
    games = Game.objects.order_by('name')
    paginator = Paginator(games, 4)

    page_number = request.GET.get('page')
    try:
        page  = paginator.get_page(page_number)
    except EmptyPage:
        page  = paginator.get_page(paginator.num_pages)
    paginator_iter = range(1, page.paginator.num_pages + 1)

    context = {
        'page': page,
        'paginator_iter': paginator_iter
    }
    return render(request, 'games/index.html', context)