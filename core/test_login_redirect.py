from django.test import TestCase, Client
from django.urls import reverse
from core.models import User

class LoginRedirectTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'password123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_redirects_to_home(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        # Should redirect
        self.assertEqual(response.status_code, 302)
        # Should redirect to home (or locale prefixed home)
        # Since we have i18n patterns, it might redirect to /en/ or /zh-hant/
        # But the setting LOGIN_REDIRECT_URL = 'home' should resolve to the URL name 'home'
        
        # Check that it redirects to something that isn't the login page
        self.assertNotEqual(response.url, reverse('login'))
        
        # Ideally it should be /en/ or /zh-hant/ depending on default language
        # Let's check if it ends with /
        self.assertTrue(response.url.endswith('/'))
        
        # We can also check if it follows to home
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        }, follow=True)
        self.assertContains(response, "Express Delivery") # Assuming home page has this text
