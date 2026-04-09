from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from statuses.models import Status
from tasks.models import Task

from .models import Label

User = get_user_model()


class LabelCRUDTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'  # NOSONAR
        )
        self.label = Label.objects.create(name='Тестовая метка')

    def test_label_creation(self):
        """Создание метки (только для залогиненных)"""
        self.client.login(username='testuser', password='testpass123')  # NOSONAR
        response = self.client.post(
            reverse('label_create'),
            {'name': 'Новая метка'}
        )
        self.assertRedirects(response, reverse('labels_index'))
        self.assertTrue(
            Label.objects.filter(name='Новая метка').exists()
        )

    def test_label_update(self):
        """Редактирование метки (только для залогиненных)"""
        self.client.login(username='testuser', password='testpass123')  # NOSONAR
        response = self.client.post(
            reverse('label_update', args=[self.label.id]),
            {'name': 'Обновленная метка'}
        )
        self.assertRedirects(response, reverse('labels_index'))
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, 'Обновленная метка')

    def test_label_delete(self):
        """Удаление метки (только для залогиненных)"""
        self.client.login(username='testuser', password='testpass123')  # NOSONAR
        response = self.client.post(
            reverse('label_delete', args=[self.label.id])
        )
        self.assertRedirects(response, reverse('labels_index'))
        self.assertFalse(
            Label.objects.filter(id=self.label.id).exists()
        )

    def test_labels_list_requires_login(self):
        """Список меток требует авторизации"""
        response = self.client.get(reverse('labels_index'))
        self.assertEqual(response.status_code, 302)

    def test_cannot_delete_label_used_in_task(self):
        """Нельзя удалить метку, если она связана с задачей"""
        self.client.login(username='testuser', password='testpass123')  # NOSONAR

        # Создаем статус
        status = Status.objects.create(name='Новый')

        # Создаем задачу
        task = Task.objects.create(
            name='Задача с меткой',
            status=status,
            author=self.user
        )

        # Добавляем метку к задаче
        task.labels.add(self.label)

        # Проверяем, что связь действительно создалась
        self.assertEqual(task.labels.count(), 1)

        # Пытаемся удалить метку
        response = self.client.post(
            reverse('label_delete', args=[self.label.id])
        )

        # Проверяем редирект на список меток
        self.assertRedirects(response, reverse('labels_index'))

        # Проверяем, что метка не удалилась
        self.assertTrue(
            Label.objects.filter(id=self.label.id).exists()
        )

        # Проверяем сообщение об ошибке (после редиректа)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any('Невозможно удалить метку' in str(msg) for msg in messages)
        )