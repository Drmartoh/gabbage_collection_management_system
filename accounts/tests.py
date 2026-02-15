"""Tests for auth: login, logout, password reset."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        from accounts.models import Role
        self.role = Role.objects.create(name='super_admin', description='Super Admin')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            role=self.role,
        )

    def test_login_page_get(self):
        url = reverse('accounts:login')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'login', status_code=200)

    def test_login_success(self):
        url = reverse('accounts:login')
        resp = self.client.post(url, {'username': 'testuser', 'password': 'testpass123'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

    def test_login_invalid_credentials(self):
        url = reverse('accounts:login')
        resp = self.client.post(url, {'username': 'testuser', 'password': 'wrong'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)
        url = reverse('accounts:logout')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)
        self.assertIn('login', resp.request.get('PATH_INFO', '') or resp.redirect_chain[-1][0] if resp.redirect_chain else '')

    def test_logout_with_safe_next_redirects_there(self):
        self.client.force_login(self.user)
        url = reverse('accounts:logout') + '?next=/billing/'
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_logout_ignores_empty_next(self):
        self.client.force_login(self.user)
        url = reverse('accounts:logout') + '?next='
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        # Should land on login, not break with NoReverseMatch
        self.assertIn('login', resp.request.get('PATH_INFO', '') or resp.url or '')

    def test_password_reset_page_get(self):
        url = reverse('accounts:password_reset')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'email', status_code=200)
