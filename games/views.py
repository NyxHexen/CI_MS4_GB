from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Max
from games.models import Game, Genre, Tag, Platform, Feature


def games(request):
    games = Game.objects.order_by('name')
    paginator = Paginator(games, 4)

    page_number = request.GET.get('page')
    try:
        page  = paginator.get_page(page_number)
    except EmptyPage:
        page  = paginator.get_page(paginator.num_pages)
    paginator_iter = range(1, page.paginator.num_pages + 1)
    price_slider_ceil = float(games.aggregate(Max('final_price'))['final_price__max'])

    genres = Genre.objects.all()
    tags = Tag.objects.all()
    platforms = Platform.objects.all()
    features = Feature.objects.all()
    
    context = {
        'page': page,
        'paginator_iter': paginator_iter,
        'genres': genres,
        'tags': tags,
        'platforms': platforms,
        'features': features,
        'price_slider_ceil': price_slider_ceil,
    }
    return render(request, 'games/index.html', context)