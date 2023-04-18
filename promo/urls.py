from django.urls import path
from . import views

urlpatterns = [
    path('<promo_id>/', views.promo, name='promo'),
    path('add/', views.promo_add, name='promo_add'),
    path('<promo_id>/edit/', views.promo_edit, name='promo_edit'),
    path('<promo_id>/delete/', views.promo_delete, name='promo_delete'),
]