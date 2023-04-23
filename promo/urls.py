# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.urls import path

# Local
from . import views
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


urlpatterns = [
    path('add/', views.promo_add, name='promo_add'),
    path('<promo_id>/', views.promo, name='promo'),
    path('<promo_id>/edit/', views.promo_edit, name='promo_edit'),
    path('<promo_id>/delete/', views.promo_delete, name='promo_delete'),
]