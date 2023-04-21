from django.test import TestCase
from django.contrib.auth.models import User

class ProfilesModelsTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test-gamebox', 
            password='gamebox-pwd',
            first_name="Test",
            last_name="Test",
            email="test@test.com"
            )

    def test_string_method(self):
        self.assertEqual(self.user.userprofile.__str__(), 'test-gamebox')

    