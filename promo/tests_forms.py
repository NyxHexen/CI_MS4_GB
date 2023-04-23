from django.test import TestCase
from django.utils import timezone

from games.models import Game
from home.models import Media
from .models import Promo
from .forms import PromoForm

from decimal import Decimal
from datetime import date, timedelta


class PromoFormTest(TestCase):
    def setUp(self):
        self.game_1 = Game.objects.create(
            name="Assassin's Creed",
            description="An action-adventure game",
            storyline="A story about assassins",
            release_date=date(2007, 11, 13),
            base_price=round(Decimal(49.99), 2),
        )
        self.game_2 = Game.objects.create(
            name="Creed's Assassin",
            description="An adventure-action game",
            storyline="A story about Creed",
            release_date=date(2012, 11, 13),
            base_price=round(Decimal(49.99), 2),
        )
        self.media_1 = Media.objects.create(
            name='No Image LANDING',
            description='No Image LANDING',
            media_type='image',
        )
        self.media_2 = Media.objects.create(
            name='No Image COVER',
            description='No Image COVER',
            media_type='image'
        )

    def test_promo_form_without_instance(self):
        form_data = {
            'active': True,
            'name': "TEST PROMO",
            'start_date': timezone.now().replace(microsecond=0, second=0),
            'end_date': timezone.now().replace(microsecond=0, second=0) + timedelta(days=1),
            'landing_page': True,
            'is_featured': False,
            'carousel': False,
            'short_description': 'TEST',
            'long_description': 'TESTTESTTEST',
        }

        form = PromoForm(data=form_data)
        self.assertTrue(form.is_valid())
        promo = form.save()
        self.assertEquals(timezone.now().replace(microsecond=0, second=0), promo.start_date)
        self.assertEquals(timezone.now().replace(microsecond=0, second=0) + timedelta(days=1), promo.end_date)


    def test_promo_form_with_instance(self):
        promo = Promo.objects.create(
            active=True,
            name="TEST PROMO",
            landing_page=True,
            is_featured=False,
            carousel=False,
            short_description="TEST",
            long_description="TESTTESTTEST",
        )
        promo.apply_to_game.add(self.game_1)
        promo.apply_to_game.add(self.game_2)
        promo = Promo.objects.get(name=promo.name)
        form = PromoForm(instance=promo)
        self.assertQuerysetEqual(
            form.fields['apply_to_game'].queryset, 
            promo.apply_to_game.all(),
            ordered=False
            )
        