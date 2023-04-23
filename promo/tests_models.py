# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

# Internal
from games.models import Game, DLC
from home.models import Media

# Local
from .models import Promo

# Included
from decimal import Decimal
from datetime import date, timedelta
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PromoTestCase(TestCase):
    def setUp(self):
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
            base_price=round(Decimal(29.99), 2),
        )
        self.dlc_1 = DLC.objects.create(
            required_game=self.game_1,
            name="Bassassin's Creed DLC",
            description="An action-adventure game DLC",
            storyline="A story about assassins DLC",
            release_date=date(2011, 5, 13),
            base_price=round(Decimal(19.99), 2),
        )
        self.dlc_2 = DLC.objects.create(
            required_game=self.game_2,
            name="Greed's Bassassin DLC",
            description="An action-horror game DLC",
            storyline="A story about bad assassins DLC",
            release_date=date(2011, 9, 12),
            base_price=round(Decimal(39.99), 2),
        )

    def test_clean_method_invalid(self):
        start_date = timezone.now().replace(microsecond=0, second=0)
        end_date = timezone.now().replace(microsecond=0, second=0) - timedelta(days=1)

        promo = Promo(
            active=True,
            start_date=start_date,
            end_date=end_date,
            name="TEST PROMO",
            landing_page=True,
            is_featured=False,
            carousel=False,
            short_description="TEST",
            long_description="TESTTESTTEST",
        )

        with self.assertRaises(ValidationError):
            promo.clean()

    def test_clean_method_valid(self):
        start_date = timezone.now().replace(microsecond=0, second=0)
        end_date = timezone.now().replace(microsecond=0, second=0) + timedelta(days=1)

        promo = Promo(
            active=True,
            start_date=start_date,
            end_date=end_date,
            name="TEST PROMO",
            landing_page=True,
            is_featured=False,
            carousel=False,
            short_description="TEST",
            long_description="TESTTESTTEST",
        )
        promo.clean()

    def test_save_method_promo_active(self):
        promo = Promo.objects.create(
            active=True,
            name="TEST PROMO",
            landing_page=True,
            is_featured=False,
            carousel=False,
            short_description="TEST",
            long_description="TESTTESTTEST",
        )
        self.assertEquals(promo.media, self.media_1)
        promo.apply_to_game.add(self.game_1)
        game = Game.objects.get(id=self.game_1.id)
        self.assertTrue(game.in_promo)
        self.assertEqual(game.promo, promo)

        promo.active = False
        promo.save()
        game = Game.objects.get(id=self.game_1.id)
        self.assertFalse(game.in_promo)
        self.assertNotEqual(game.promo, promo)

    def test_check_dupe_method_add(self):
        """
        This test applies to both check_dupe() and
        _update_promo_items()
        """
        promo_1 = Promo.objects.create(
            active=True,
            name="TEST PROMO",
            landing_page=True,
            is_featured=False,
            carousel=False,
            short_description="TEST",
            long_description="TESTTESTTEST",
        )

        promo_2 = Promo.objects.create(
            active=True,
            name="TEST PROMO 2",
            landing_page=True,
            is_featured=False,
            carousel=False,
            short_description="TEST 2",
            long_description="TESTTESTTEST 2",
        )

        promo_1.apply_to_game.add(self.game_1)
        promo_2.apply_to_game.add(self.game_2)
        promo_1.apply_to_game.add(self.game_1)
        game_1 = Game.objects.get(id=self.game_1.id)
        game_2 = Game.objects.get(id=self.game_2.id)
        self.assertEqual(list(promo_1.apply_to_game.all()), [game_1])
        self.assertEqual(list(promo_2.apply_to_game.all()), [game_2])

    def test_check_dupe_method_delete(self):
        """
        This test applies to both check_dupe() and
        _update_promo_items()
        """
        promo_1 = Promo.objects.create(
            active=True,
            name="TEST PROMO",
            landing_page=True,
            is_featured=False,
            carousel=False,
            short_description="TEST",
            long_description="TESTTESTTEST",
        )

        promo_1.apply_to_game.add(self.game_1)
        self.game_1.promo_percentage = 30
        self.game_1.save()
        promo_1.save()
        game_1 = Game.objects.get(id=self.game_1.id)
        self.assertEqual(list(promo_1.apply_to_game.all()), [game_1])
        self.assertEqual(game_1.promo_percentage, 30)
        self.assertTrue(game_1.in_promo)
        self.assertEqual(game_1.promo, promo_1)

        promo_1.apply_to_game.remove(self.game_1)
        promo_1.apply_to_game.remove(self.game_2)
        promo_1.save()
        
        game_1 = Game.objects.get(id=self.game_1.id)
        self.assertEqual(game_1.promo_percentage, 0)
        self.assertFalse(game_1.in_promo)
        self.assertEqual(game_1.promo, None)

    def test_max_promo_percentage_method(self):
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
        self.game_1.promo_percentage = 30
        self.game_2.promo_percentage = 60
        self.game_1.save()
        self.game_2.save()
        self.assertEqual(promo.max_promo_percentage(), 60)
