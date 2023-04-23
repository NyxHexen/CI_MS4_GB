# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 3rd party:
from decimal import Decimal
from datetime import date

# Django:
from django.test import TestCase

# Internal:
from .forms import DLCForm, GameForm, RatingForm
from .models import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TestGamesForms(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name='RPG')
        self.tag = Tag.objects.create(name='First Person')
        self.feature = Feature.objects.create(name='Open World')
        self.developer = Developer.objects.create(
            name="Test Dev 1",
            country='GB'
        )
        self.platform = Platform.objects.create(
            name="PC",
            country='GB'
        )
        self.publisher = Publisher.objects.create(
            name="Test Pub 1",
            country='GB'
        )
        self.game = Game.objects.create(
            name="Assassin's Creed",
            description="An action-adventure game",
            storyline="A story about assassins",
            release_date=date(2007, 11, 13),
            base_price=round(Decimal(49.99), 2),
        )
        self.dlc = DLC.objects.create(
            required_game=self.game,
            name="Assassin's Creed DLC",
            description="An action-adventure game DLC",
            storyline="A story about assassins DLC",
            release_date=date(2007, 11, 16),
            base_price=round(Decimal(29.99), 2),
        )
        self.media = Media.objects.create(
            name="Test Media",
            media_type="image",
            media_use="cover",
            description="Test Image",
        )
        self.esrb_rating = EsrbRating.objects.create(
            name="Teen",
        )
        self.pegi_rating = PegiRating.objects.create(
            name="17",
        )

    def test_game_form_valid(self):
        form_data = {
            'name': 'Test Game',
            'description': 'Test Description',
            'storyline': 'Test Storyline',
            'genres': [self.genre,],
            'publishers': [self.publisher,],
            'developers': [self.developer,],
            'release_date': date(2007, 5, 13),
            'platforms': [self.platform,],
            'tags': [self.tag,],
            'features': [self.feature,],
            'media': [self.media,],
            'is_featured': True,
            'carousel': True,
            'base_price': round(Decimal(49.99), 2),
        }
        form = GameForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_dlc_form_valid(self):
        form_data = {
            'required_game': self.game,
            'name': 'Test DLC',
            'description': 'Test Description',
            'storyline': 'Test Storyline',
            'genres': [self.genre,],
            'publishers': [self.publisher,],
            'developers': [self.developer,],
            'release_date': date(2007, 11, 13),
            'platforms': [self.platform,],
            'tags': [self.tag,],
            'features': [self.feature,],
            'media': [self.media,],
            'is_featured': True,
            'carousel': True,
            'base_price': round(Decimal(49.99), 2),
        }
        form = DLCForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_rating_set_form_valid(self):
        form_data = {
            'game': self.game,
            'dlc': self.dlc,
            'esrb_rating': self.esrb_rating,
            'pegi_rating': self.pegi_rating,
        }
        form = RatingForm(data=form_data)
        self.assertTrue(form.is_valid())
