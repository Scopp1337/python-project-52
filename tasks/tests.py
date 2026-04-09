from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from labels.models import Label
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

        # Должен быть редирект на список задач
        self.assertRedirects(response, reverse('tasks_index'))

        # Проверяем, что имя не изменилось
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

        # Должен быть редирект на список задач
        self.assertRedirects(response, reverse('tasks_index'))

        # Проверяем, что задача не удалилась
        self.assertTrue(
            Task.objects.filter(id=self.task.id).exists()
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

    def test_task_filter_by_status(self):
        """Тест: фильтрация задач по статусу"""
        self.client.login(username='author', password='testpass123')

        status2 = Status.objects.create(name='В работе')

        Task.objects.create(
            name='Другая задача',
            status=status2,
            author=self.author,
            executor=self.other_user
        )

        response = self.client.get(
            reverse('tasks_index'),
            {'status': self.status.id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')
        self.assertNotContains(response, 'Другая задача')

    def test_task_filter_by_executor(self):
        """Тест: фильтрация задач по исполнителю"""
        self.client.login(username='author', password='testpass123')

        executor2 = User.objects.create_user(
            username='executor2',
            password='testpass123'
        )

        Task.objects.create(
            name='Другая задача',
            status=self.status,
            author=self.author,
            executor=executor2
        )

        response = self.client.get(
            reverse('tasks_index'),
            {'executor': self.other_user.id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')
        self.assertNotContains(response, 'Другая задача')

    def test_task_filter_by_labels(self):
        """Тест: фильтрация задач по метке"""
        self.client.login(username='author', password='testpass123')

        label1 = Label.objects.create(name='Метка 1')
        label2 = Label.objects.create(name='Метка 2')

        task1 = Task.objects.create(
            name='Задача с меткой 1',
            status=self.status,
            author=self.author,
            executor=None
        )
        task1.labels.add(label1)

        task2 = Task.objects.create(
            name='Задача с меткой 2',
            status=self.status,
            author=self.author,
            executor=None
        )
        task2.labels.add(label2)

        response = self.client.get(
            reverse('tasks_index'),
            {'labels': label1.id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Задача с меткой 1')
        self.assertNotContains(response, 'Задача с меткой 2')

    def test_task_filter_only_self_tasks(self):
        """Тест: фильтр 'Только свои задачи'"""
        self.client.login(username='author', password='testpass123')

        # Создаем задачу от другого автора
        Task.objects.create(
            name='Чужая задача',
            status=self.status,
            author=self.other_user,
            executor=None
        )

        # Фильтруем "Только свои задачи"
        response = self.client.get(
            reverse('tasks_index'),
            {'only_self_tasks': 'on'}
        )

        self.assertEqual(response.status_code, 200)
        # Проверяем, что своя задача есть
        self.assertContains(response, 'Тестовая задача')
        # Проверяем, что чужая задача не отображается
        self.assertNotContains(response, 'Чужая задача')

    def test_task_filter_combined(self):
        """Тест: комбинированная фильтрация (статус + исполнитель)"""
        self.client.login(username='author', password='testpass123')

        status2 = Status.objects.create(name='В работе')
        executor2 = User.objects.create_user(
            username='executor2',
            password='testpass123'
        )

        Task.objects.create(
            name='Неподходящая задача',
            status=status2,
            author=self.author,
            executor=executor2
        )

        response = self.client.get(
            reverse('tasks_index'),
            {
                'status': self.status.id,
                'executor': self.other_user.id
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая задача')
        self.assertNotContains(response, 'Неподходящая задача')

    def test_task_filter_reset(self):
        """Тест: сброс фильтров"""
        self.client.login(username='author', password='testpass123')

        status2 = Status.objects.create(name='В работе')
        Task.objects.create(
            name='Другая задача',
            status=status2,
            author=self.author,
            executor=None
        )

        response_filtered = self.client.get(
            reverse('tasks_index'),
            {'status': status2.id}
        )
        self.assertContains(response_filtered, 'Другая задача')
        self.assertNotContains(response_filtered, 'Тестовая задача')

        response_reset = self.client.get(reverse('tasks_index'))
        self.assertContains(response_reset, 'Тестовая задача')
        self.assertContains(response_reset, 'Другая задача')