from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


class UserCRUDWithFixturesTest(TestCase):

    fixtures = ['users.json']

    def setUp(self):
        self.user_data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
        }

        self.login_data = {
            'username': 'testuser1',
            'password': 'testpass123',
        }

    def test_users_list_from_fixture(self):
        response = self.client.get(reverse('users_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 2)

    def test_user_creation(self):
        response = self.client.post(reverse('user_create'), self.user_data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(User.objects.count(), 3)

    def test_user_update(self):
        user = User.objects.get(username='testuser1')

        user.password = make_password('testpass123')
        user.save()

        self.client.login(username='testuser1', password='testpass123')

        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'username': 'testuser1',
        }
        response = self.client.post(reverse('user_update', args=[user.pk]), update_data)

        self.assertRedirects(response, reverse('users_index'))

        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'Name')

    def test_user_delete(self):
        user = User.objects.get(username='testuser1')

        user.password = make_password('testpass123')
        user.save()

        self.client.login(username='testuser1', password='testpass123')

        response = self.client.post(reverse('user_delete', args=[user.pk]))

        self.assertRedirects(response, reverse('users_index'))
        self.assertFalse(User.objects.filter(username='testuser1').exists())
        self.assertEqual(User.objects.count(), 1)

    def test_user_update_permission_denied(self):
        user1 = User.objects.get(username='testuser1')
        user2 = User.objects.get(username='testuser2')

        user1.password = make_password('testpass123')
        user1.save()

        self.client.login(username='testuser1', password='testpass123')

        update_data = {
            'first_name': 'Hacked',
            'last_name': 'User',
            'username': 'testuser2',
        }
        response = self.client.post(reverse('user_update', args=[user2.pk]), update_data)

        self.assertRedirects(response, reverse('users_index'))

        user2.refresh_from_db()
        self.assertEqual(user2.first_name, 'Test')
        self.assertEqual(user2.last_name, 'User2')