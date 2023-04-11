from django.urls import path
from . import views

urlpatterns = [
    path('', views.games, name='games'),
    path('<model_name>/<game_id>/', views.game, name='game'),
]