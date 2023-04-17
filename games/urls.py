from django.urls import path
from . import views

urlpatterns = [
    path('', views.games, name='games'),
    path('<model_name>/<game_id>/', views.game, name='game'),
    path('add/<model_name>', views.game_add, name='game_add'),
    path('<model_name>/<game_id>/_set_game_rating/', views.set_game_rating, name='set_game_rating'),
]