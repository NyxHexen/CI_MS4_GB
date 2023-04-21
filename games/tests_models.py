from django.test import TestCase
from django.urls import reverse
from decimal import Decimal

from django.contrib.auth.models import User
from .models import *
from datetime import date


class TestGamesModels(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test-gamebox', 
            password='gamebox-pwd',
            first_name="Test",
            last_name="Test",
            email="test@test.com"
            )
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
        self.rating_set = RatingSet.objects.create(
            game=self.game,
            dlc=None,
        )

    def test_games_model_rels(self):
        self.game.genres.add(self.genre)
        self.game.publishers.add(self.publisher)
        self.game.developers.add(self.developer)
        self.game.platforms.add(self.platform)
        self.game.tags.add(self.tag)
        self.game.features.add(self.feature)

        self.assertEqual(self.game.genres.count(), 1)
        self.assertEqual(self.game.publishers.count(), 1)
        self.assertEqual(self.game.developers.count(), 1)
        self.assertEqual(self.game.platforms.count(), 1)
        self.assertEqual(self.game.tags.count(), 1)
        self.assertEqual(self.game.features.count(), 1)

    def test_rating_set_model(self):
        rating_set = RatingSet.objects.get(game__id=self.game.id)
        self.assertEqual(rating_set.game, self.game)
        self.assertEqual(rating_set.game.name, self.game.name)
        UserRating.objects.create(
            user=self.user,
            rating_set=rating_set,
            value=5
        )
        self.assertEqual(rating_set.user_rating_calc(), 5)
        self.assertEqual(rating_set.__str__(), self.game.name)


