from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserCRUDWithFixturesTest(TestCase):
    """Тесты CRUD с использованием фикстур"""

    fixtures = ['users.json']

    def setUp(self):
        """Дополнительная подготовка данных"""
        self.user_data = {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'password1': 'newpass123',  # NOSONAR
            'password2': 'newpass123',  # NOSONAR
        }

        self.login_data = {
            'username': 'testuser1',
            'password': 'testpass123',  # NOSONAR
        }

    def test_users_list_from_fixture(self):
        """Тест: список пользователей из фикстуры"""
        response = self.client.get(reverse('users_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 2)

    def test_user_creation(self):
        """Тест: создание нового пользователя"""
        response = self.client.post(reverse('user_create'), self.user_data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(User.objects.count(), 3)

    def test_user_update(self):
        """Тест: редактирование пользователя"""
        user = User.objects.get(username='testuser1')

        user.password = make_password('testpass123')  # NOSONAR
        user.save()

        self.client.login(username='testuser1', password='testpass123')  # NOSONAR

        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'username': 'testuser1',
        }
        response = self.client.post(
            reverse('user_update', args=[user.pk]),
            update_data
        )

        self.assertRedirects(response, reverse('users_index'))

        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.last_name, 'Name')

    def test_user_delete(self):
        """Тест: удаление пользователя"""
        user = User.objects.get(username='testuser1')

        user.password = make_password('testpass123')  # NOSONAR
        user.save()

        self.client.login(username='testuser1', password='testpass123')  # NOSONAR

        response = self.client.post(
            reverse('user_delete', args=[user.pk])
        )

        self.assertRedirects(response, reverse('users_index'))
        self.assertFalse(
            User.objects.filter(username='testuser1').exists()
        )
        self.assertEqual(User.objects.count(), 1)

    def test_user_update_permission_denied(self):
        """Тест: нельзя редактировать чужого пользователя"""
        user1 = User.objects.get(username='testuser1')
        user2 = User.objects.get(username='testuser2')

        user1.password = make_password('testpass123')  # NOSONAR
        user1.save()

        self.client.login(username='testuser1', password='testpass123')  # NOSONAR

        update_data = {
            'first_name': 'Hacked',
            'last_name': 'User',
            'username': 'testuser2',
        }
        response = self.client.post(
            reverse('user_update', args=[user2.pk]),
            update_data
        )

        self.assertRedirects(response, reverse('users_index'))

        user2.refresh_from_db()
        self.assertEqual(user2.first_name, 'Test')
        self.assertEqual(user2.last_name, 'User2')