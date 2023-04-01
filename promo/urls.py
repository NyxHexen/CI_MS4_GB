from django.urls import path
from . import views

urlpatterns = [
    path('<promo_id>', views.promo, name='promo')
]