from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from statuses.models import Status

from .models import Task

User = get_user_model()


class TaskCRUDTest(TestCase):
    """Тесты для CRUD операций с задачами"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.author = User.objects.create_user(
            username='author',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='testpass123'
        )

        self.status = Status.objects.create(name='Новый')

        self.task_data = {
            'name': 'Новая задача',
            'description': 'Описание',
            'status': self.status.id,
            'executor': self.other_user.id
        }

        self.task = Task.objects.create(
            name='Тестовая задача',
            status=self.status,
            author=self.author,
            executor=self.other_user
        )

    def test_task_creation(self):
        """Тест: создание задачи"""
        self.client.login(username='author', password='testpass123')

        response = self.client.post(
            reverse('task_create'),
            self.task_data
        )

        self.assertRedirects(response, reverse('tasks_index'))
        self.assertTrue(
            Task.objects.filter(name='Новая задача').exists()
        )
        task = Task.objects.get(name='Новая задача')
        self.assertEqual(task.author, self.author)

    def test_task_creation_requires_login(self):
        """Тест: создание задачи требует авторизации"""
        response = self.client.post(
            reverse('task_create'),
            self.task_data
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Task.objects.filter(name='Новая задача').exists()
        )

    def test_task_update_by_author(self):
        """Тест: автор может обновить свою задачу"""
        self.client.login(username='author', password='testpass123')

        response = self.client.post(
            reverse('task_update', args=[self.task.id]),
            {
                'name': 'Обновленная задача',
                'status': self.status.id,
                'executor': self.other_user.id
            }
        )

        self.assertRedirects(response, reverse('tasks_index'))
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Обновленная задача')

    def test_task_update_by_non_author(self):
        """Тест: другой пользователь НЕ может обновить чужую задачу"""
        self.client.login(username='other', password='testpass123')

        original_name = self.task.name

        response = self.client.post(
            reverse('task_update', args=[self.task.id]),
            {
                'name': 'Попытка взлома',
                'status': self.status.id,
                'executor': self.author.id
            }
        )

        self.assertRedirects(response, reverse('tasks_index'))

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                'может редактировать только ее автор' in str(msg)
                for msg in messages
            )
        )

        self.task.refresh_from_db()
        self.assertEqual(self.task.name, original_name)

    def test_task_delete_by_author(self):
        """Тест: автор может удалить свою задачу"""
        self.client.login(username='author', password='testpass123')

        response = self.client.post(
            reverse('task_delete', args=[self.task.id])
        )

        self.assertRedirects(response, reverse('tasks_index'))
        self.assertFalse(
            Task.objects.filter(id=self.task.id).exists()
        )

    def test_task_delete_by_non_author(self):
        """Тест: другой пользователь НЕ может удалить чужую задачу"""
        self.client.login(username='other', password='testpass123')

        response = self.client.post(
            reverse('task_delete', args=[self.task.id])
        )

        self.assertTrue(
            Task.objects.filter(id=self.task.id).exists()
        )

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any('только ее автор' in str(msg) for msg in messages)
        )

    def test_cannot_delete_user_with_tasks(self):
        """Тест: нельзя удалить пользователя, если у него есть задачи"""
        with self.assertRaises(Exception):
            self.author.delete()

        self.assertTrue(
            User.objects.filter(username='author').exists()
        )

    def test_task_list_requires_login(self):
        """Тест: список задач требует авторизации"""
        response = self.client.get(reverse('tasks_index'))
        self.assertEqual(response.status_code, 302)