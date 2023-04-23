# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.urls import path

# Local
from . import views
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


urlpatterns = [
    path('', views.games, name='games'),
    path('platforms/<int:attr_id>/', views.game_attrs, name='game_attrs'),
    path('developers/<int:attr_id>/', views.game_attrs, name='game_attrs'),
    path('publishers/<int:attr_id>/', views.game_attrs, name='game_attrs'),
    path('add/<str:model_name>', views.game_add, name='game_add'),
    path('<str:model_name>/<int:game_id>/', views.game, name='game'),
    path('<str:model_name>/<int:game_id>/edit', views.game_edit, name='game_edit'),
    path('<str:model_name>/<int:game_id>/delete/', views.game_delete, name='game_delete'),
    path('<str:model_name>/<int:game_id>/_set_game_rating/', views.set_game_rating, name='set_game_rating'),
]