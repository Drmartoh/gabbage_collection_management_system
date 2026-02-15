"""Tests for notifications: create, mark read, mark all read."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from accounts.models import Role
from notifications.models import Notification

User = get_user_model()


class NotificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.role = Role.objects.create(name='landlord', description='Landlord')
        self.user = User.objects.create_user(username='landlord1', password='testpass123', role=self.role)

    def test_notification_list_requires_login(self):
        url = reverse('notifications:notification_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)

    def test_notification_list_shows_user_notifications(self):
        Notification.objects.create(
            user=self.user,
            title='Test',
            message='Body',
            is_read=False,
        )
        self.client.force_login(self.user)
        resp = self.client.get(reverse('notifications:notification_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Test')

    def test_mark_read(self):
        n = Notification.objects.create(user=self.user, title='T', message='M', is_read=False)
        self.client.force_login(self.user)
        url = reverse('notifications:notification_mark_read', kwargs={'pk': n.pk})
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_mark_all_read(self):
        Notification.objects.create(user=self.user, title='T1', message='M1', is_read=False)
        Notification.objects.create(user=self.user, title='T2', message='M2', is_read=False)
        self.client.force_login(self.user)
        resp = self.client.get(reverse('notifications:notification_mark_all_read'), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Notification.objects.filter(user=self.user, is_read=False).count(), 0)
