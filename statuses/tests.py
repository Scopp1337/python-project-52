from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from statuses.models import Status
from tasks.models import Task

User = get_user_model()


class StatusCRUDTest(TestCase):
    """Тесты для CRUD операций со статусами"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        self.status_data = {
            'name': 'Новый статус'
        }

        self.status = Status.objects.create(name='Тестовый статус')

    def test_status_list_requires_login(self):
        """Тест: список статусов требует авторизации"""
        response = self.client.get(reverse('statuses_index'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("statuses_index")}'
        )

    def test_status_list_accessible_for_logged_in(self):
        """Тест: список статусов доступен для залогиненных"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('statuses_index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый статус')

    def test_status_creation(self):
        """Тест: создание нового статуса (C - Create)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('status_create'),
            self.status_data
        )

        self.assertRedirects(response, reverse('statuses_index'))
        self.assertTrue(
            Status.objects.filter(name='Новый статус').exists()
        )
        self.assertEqual(Status.objects.count(), 2)

    def test_status_creation_requires_login(self):
        """Тест: создание статуса требует авторизации"""
        response = self.client.post(
            reverse('status_create'),
            self.status_data
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Status.objects.filter(name='Новый статус').exists()
        )

    def test_status_creation_duplicate_name(self):
        """Тест: нельзя создать статус с существующим именем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('status_create'),
            {'name': 'Тестовый статус'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'уже существует')
        self.assertEqual(Status.objects.count(), 1)

    def test_status_update(self):
        """Тест: обновление статуса (U - Update)"""
        self.client.login(username='testuser', password='testpass123')
        update_data = {'name': 'Обновленный статус'}
        response = self.client.post(
            reverse('status_update', args=[self.status.id]),
            update_data
        )

        self.assertRedirects(response, reverse('statuses_index'))
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Обновленный статус')

    def test_status_update_requires_login(self):
        """Тест: обновление статуса требует авторизации"""
        response = self.client.post(
            reverse('status_update', args=[self.status.id]),
            {'name': 'Обновленный статус'}
        )

        self.assertEqual(response.status_code, 302)
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Тестовый статус')

    def test_status_update_duplicate_name(self):
        """Тест: нельзя обновить статус на уже существующее имя"""
        Status.objects.create(name='Другой статус')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('status_update', args=[self.status.id]),
            {'name': 'Другой статус'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'уже существует')
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Тестовый статус')

    def test_status_delete(self):
        """Тест: удаление статуса (D - Delete)"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('status_delete', args=[self.status.id])
        )

        self.assertRedirects(response, reverse('statuses_index'))
        self.assertFalse(
            Status.objects.filter(id=self.status.id).exists()
        )
        self.assertEqual(Status.objects.count(), 0)

    def test_status_delete_requires_login(self):
        """Тест: удаление статуса требует авторизации"""
        response = self.client.post(
            reverse('status_delete', args=[self.status.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Status.objects.filter(id=self.status.id).exists()
        )

    def test_status_delete_with_tasks(self):
        """Тест: нельзя удалить статус, связанный с задачей"""
        self.client.login(username='testuser', password='testpass123')

        Task.objects.create(
            name='Тестовая задача',
            description='Описание задачи',
            status=self.status,
            author=self.user
        )

        # Убираем присваивание переменной, так как она не используется
        self.client.post(
            reverse('status_delete', args=[self.status.id])
        )

        self.assertTrue(
            Status.objects.filter(id=self.status.id).exists()
        )
        self.assertEqual(Status.objects.count(), 1)

    def test_status_create_page_requires_login(self):
        """Тест: страница создания статуса требует авторизации"""
        response = self.client.get(reverse('status_create'))
        self.assertEqual(response.status_code, 302)

    def test_status_create_page_accessible_for_logged_in(self):
        """Тест: страница создания статуса доступна для залогиненных"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('status_create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')
        self.assertContains(response, 'method="post"')

    def test_status_update_page_requires_login(self):
        """Тест: страница редактирования статуса требует авторизации"""
        response = self.client.get(
            reverse('status_update', args=[self.status.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_status_update_page_accessible_for_logged_in(self):
        """Тест: страница редактирования статуса доступна для залогиненных"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('status_update', args=[self.status.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.status.name)

    def test_status_delete_page_requires_login(self):
        """Тест: страница удаления статуса требует авторизации"""
        response = self.client.get(
            reverse('status_delete', args=[self.status.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_status_delete_page_accessible_for_logged_in(self):
        """Тест: страница удаления статуса доступна для залогиненных"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('status_delete', args=[self.status.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вы уверены')
        self.assertContains(response, self.status.name)