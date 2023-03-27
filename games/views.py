from django.shortcuts import render
from django.http import QueryDict
from django.template.defaultfilters import urlencode
from django.core.paginator import Paginator, EmptyPage
from urllib.parse import urlencode
from games.models import Game, Genre, Tag, Platform, Feature, DLC

from decimal import Decimal
from datetime import datetime


def games(request):
    games = Game.objects.all()
    dlcs = DLC.objects.all()

    filter_dict = QueryDict(mutable=True)

    if "filter" in request.GET:
        filter_condition = {
            'sale_only': lambda queryset, *args: queryset.filter(in_promo=True, promo__active=True),
            'hide_extras': lambda queryset, param: queryset.exclude(required_game__isnull=False) if all(hasattr(obj, 'required_game') for obj in queryset.all()) else queryset,
            'price_range': lambda queryset, param: queryset.filter(final_price__gte=Decimal(param[0]),final_price__lte=Decimal(param[1])) if len(param) == 2 else queryset,
            'genres_filter': lambda queryset, param: queryset.filter(genres__slug__in=param).distinct() if not all(hasattr(obj, 'required_game') for obj in queryset.all()) else queryset.filter(required_game__genres__slug__in=param).distinct(),
            'tags_filter': lambda queryset, param: queryset.filter(tags__slug__in=param).distinct(),
            'platforms_filter': lambda queryset, param: queryset.filter(platforms__slug__in=param).distinct() if not all(hasattr(obj, 'required_game') for obj in queryset.all()) else queryset.filter(required_game__platforms__slug__in=param).distinct(),
            'features_filter': lambda queryset, param: queryset.filter(features__slug__in=param).distinct(),
            'date_range': lambda queryset, param: queryset.filter(release_date__gte=datetime(int(param[0]), 1, 1), release_date__lte=datetime(int(param[1]), 12, 31)) if len(param) == 2 else queryset,
        }

        filtered_results_games = games
        filtered_results_dlcs = dlcs

        for key,value in filter_condition.items():
            if key in request.GET:
                if filter_dict.get(key) is None:
                    filter_dict.update({f'{key}': f'{request.GET.get(key)}'})
                filter_param = request.GET.getlist(key)[0].split(',') if key.endswith('_filter') or key.endswith('_range') else request.GET.get(key)
                filtered_results_games = value(filtered_results_games, filter_param)
                filtered_results_dlcs = value(filtered_results_dlcs, filter_param)

        if "sort_by" in request.GET:
            filter_dict.update({f'sort_by': f'{request.GET.get("sort_by")}'})

        filtered_results = sort_by(request.GET.get("sort_by"), filtered_results_games, filtered_results_dlcs)

        paginator = Paginator(filtered_results, 4)
    else:
        if "sort_by" in request.GET:
            filter_dict.update({f'sort_by': f'{request.GET.get("sort_by")}'})
        games = sort_by(request.GET.get("sort_by"), games, dlcs)
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
    if "filter" in request.GET or "sort_by" in request.GET:
        context['filter_dict'] = urlencode(filter_dict)
        return render(request, 'games/index.html', context)
    else: 
        return render(request, 'games/index.html', context)


def sort_by(sort_value, *args):
    sorted_args = [list(arg) for arg in args] if len(args) != 0 else list()
    sorted_args = [item for sublist in sorted_args for item in sublist]
    match sort_value:
        case "price_desc":
            sorted_args.sort(key=lambda x: x.final_price)
        case "price_asc":
            sorted_args.sort(key=lambda x: x.final_price, reverse=True)
        case "discount_desc":
            sorted_args.sort(key=lambda x: x.promo_percentage, reverse=True)
        case "title_asc":
            sorted_args.sort(key=lambda x: x.name, reverse=True)
        case "title_desc":
            sorted_args.sort(key=lambda x: x.name)
        case "date_desc":
            sorted_args.sort(key=lambda x: x.release_date)
        case "date_asc":
            sorted_args.sort(key=lambda x: x.release_date, reverse=True)
        case "rating_desc":
            sorted_args.sort(key=lambda x: x.rating, reverse=True)
        case _:
            print("Wooops!")
    return sorted_args