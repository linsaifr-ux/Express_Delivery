from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import activate

class LanguageSwitchTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_language_switch_preserves_page(self):
        # Test 1: Register page
        current_url = '/en/register/'
        target_lang = 'zh-hant'
        response = self.client.post(reverse('set_language'), {
            'language': target_lang,
            'next': current_url
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/zh-hant/register/')

    def test_language_switch_dashboard(self):
        # Test 2: Dashboard page (even if not logged in, URL translation should work)
        current_url = '/en/dashboard/'
        target_lang = 'zh-hant'
        response = self.client.post(reverse('set_language'), {
            'language': target_lang,
            'next': current_url
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/zh-hant/dashboard/')

    def test_language_switch_home_explicit(self):
        # Test 4: Explicit home page /en/
        current_url = '/en/'
        target_lang = 'zh-hant'
        response = self.client.post(reverse('set_language'), {
            'language': target_lang,
            'next': current_url
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/zh-hant/')

    def test_language_switch_no_next(self):
        # Test 3: No next parameter -> should go to home (translated)
        target_lang = 'zh-hant'
        response = self.client.post(reverse('set_language'), {
            'language': target_lang
        })
        self.assertEqual(response.status_code, 302)
        # Default redirect is usually / or settings.LOGIN_REDIRECT_URL if set?
        # Django's set_language redirects to request.META.get('HTTP_REFERER') if next is not set.
        # If referer is also missing, it falls back to /.
        self.assertEqual(response.url, '/zh-hant/')


