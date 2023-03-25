from django.shortcuts import render
from django.http import QueryDict
from django.template.defaultfilters import urlencode
from django.core.paginator import Paginator, EmptyPage
from urllib.parse import urlencode
from games.models import Game, Genre, Tag, Platform, Feature, DLC


def games(request):
    dlcs = DLC.objects.all()
    games = Game.objects.all()

    filter_dict = QueryDict(mutable=True)

    if "filter" in request.GET:
        filter_condition = {
            'sale_only': lambda queryset, *args: queryset.filter(in_promo=True, promo__active=True),
            'hide_extras': lambda queryset, param: queryset.exclude(required_game__isnull=False) if all(hasattr(obj, 'required_game') for obj in queryset.all()) else queryset,
            'price_range': lambda queryset, param: queryset.filter(release_date__lte=param[0], release_date_gte=param[1] if param.length == 2 else print(param)),
            'genres_filter': lambda queryset, param: queryset.filter(genres__slug__in=param).distinct() if not all(hasattr(obj, 'required_game') for obj in queryset.all()) else queryset,
            'tags_filter': lambda queryset, param: queryset.filter(tags__slug__in=param).distinct(),
            'platforms_filter': lambda queryset, param: queryset.filter(platforms__slug__in=param).distinct(),
            'features_filter': lambda queryset, param: queryset.filter(features__slug__in=param).distinct(),
            'release_date': lambda x, param: param[0] <= x.release_date <= param[1] if param.length == 2 else True,
        }

        filtered_results_games = games
        filtered_results_dlcs = dlcs

        for key,value in filter_condition.items():
            if key in request.GET:
                if filter_dict.get(key) is None:
                    filter_dict.update({f'{key}': f'{request.GET.get(key)}'})
                filter_param = request.GET.getlist(key)[0].split(',') if key.endswith('_filter') else request.GET.get(key)
                filtered_results_games = value(filtered_results_games, filter_param)
                filtered_results_dlcs = value(filtered_results_dlcs, filter_param)
        
        print(filtered_results_games)
        print(filtered_results_dlcs)
        filtered_results = list(filtered_results_games) + list(filtered_results_dlcs if filtered_results_dlcs is not None else None)
        paginator = Paginator(filtered_results, 4)
        print(filter_dict)
    else:
        games = list(games) + list(dlcs)
        paginator = Paginator(games, 4)

    page_number = request.GET.get('page')
    try:
        page  = paginator.get_page(page_number)
    except EmptyPage:
        page  = paginator.get_page(paginator.num_pages)
    paginator_iter = range(1, page.paginator.num_pages + 1)
    price_slider_ceil = float(max(games, key=lambda item: item.final_price).final_price)

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
    if "filter" in request.GET:
        context['filter_dict'] = urlencode(filter_dict)
        print(filter_dict)
        return render(request, 'games/index.html', context)
    else: 
        return render(request, 'games/index.html', context)
