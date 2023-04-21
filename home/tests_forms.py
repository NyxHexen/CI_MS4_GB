from django.test import TestCase
from .forms import MediaForm
# Create your tests here.

class MediaFormTest(TestCase):
    def setUp(self):
        self.form_data = {
            'name': 'Test Media',
            'url': 'http://youtube.com/test-media/',
            'file': None,
            'media_type': 'video',
            'media_use': 'PREVIEW',
            'description': 'This is a test media file ALT.',
        }

        self.bad_data = {
            'name': '',
            'url': 'invalid-url',
            'file': None,
            'media_type': 'invalid-type',
            'media_use': 'invalid-use',
            'description': '',
        }

    def test_form(self):
        form = MediaForm(data=self.form_data)
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_bad_form(self):
        form = MediaForm(data=self.bad_data)
        self.assertFalse(form.is_valid())
        self.assertNotEqual(len(form.errors), 0)

