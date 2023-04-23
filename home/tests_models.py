# Imports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Django
from django.test import TestCase
# Local
from .models import Media
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class MediaModelTest(TestCase):
    
    def setUp(self):
        Media.objects.create(
            name='Test Media',
            url='',
            media_type='image',
            media_use='COVER',
            media_ext='png',
            description='Test media description'
        )

    def test_media_name(self):
        media = Media.objects.get(name='Test Media')
        self.assertEqual(media.__str__(), media.name)
    
    def test_media_slug(self):
        media = Media.objects.get(name='Test Media')
        self.assertEqual(media.slug, 'test-media')