from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from statuses.models import Status
from tasks.models import Task


User = get_user_model()


class StatusCRUDTest(TestCase):
    """Тесты для CRUD операций со статусами"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Данные для создания статуса
        self.status_data = {
            'name': 'Новый статус'
        }

        # Создаем тестовый статус для тестов обновления и удаления
        self.status = Status.objects.create(name='Тестовый статус')

    def test_status_list_requires_login(self):
        """Тест: список статусов требует авторизации"""
        # Пытаемся открыть список статусов без логина
        response = self.client.get(reverse('statuses_index'))

        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("statuses_index")}')

    def test_status_list_accessible_for_logged_in(self):
        """Тест: список статусов доступен для залогиненных пользователей"""
        # Логинимся
        self.client.login(username='testuser', password='testpass123')

        # Открываем список статусов
        response = self.client.get(reverse('statuses_index'))

        # Проверяем успешный ответ
        self.assertEqual(response.status_code, 200)

        # Проверяем, что статус отображается в списке
        self.assertContains(response, 'Тестовый статус')

    def test_status_creation(self):
        """Тест: создание нового статуса (C - Create)"""
        # Логинимся
        self.client.login(username='testuser', password='testpass123')

        # Отправляем POST запрос на создание статуса
        response = self.client.post(
            reverse('status_create'),
            self.status_data
        )

        # Проверяем редирект на список статусов
        self.assertRedirects(response, reverse('statuses_index'))

        # Проверяем, что статус создался в базе данных
        self.assertTrue(Status.objects.filter(name='Новый статус').exists())

        # Проверяем количество статусов (был 1 тестовый + 1 новый = 2)
        self.assertEqual(Status.objects.count(), 2)

    def test_status_creation_requires_login(self):
        """Тест: создание статуса требует авторизации"""
        # Пытаемся создать статус без логина
        response = self.client.post(
            reverse('status_create'),
            self.status_data
        )

        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)

        # Проверяем, что статус не создался
        self.assertFalse(Status.objects.filter(name='Новый статус').exists())

    def test_status_creation_duplicate_name(self):
        """Тест: нельзя создать статус с существующим именем"""
        # Логинимся
        self.client.login(username='testuser', password='testpass123')

        # Пытаемся создать статус с именем, которое уже существует
        response = self.client.post(
            reverse('status_create'),
            {'name': 'Тестовый статус'}  # Это имя уже есть
        )

        # Проверяем, что форма не прошла валидацию (код 200 - форма с ошибкой)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что в ответе есть сообщение об ошибке
        self.assertContains(response, 'уже существует')

        # Проверяем, что дубликат не создался (всего 1 статус)
        self.assertEqual(Status.objects.count(), 1)

    def test_status_update(self):
        """Тест: обновление статуса (U - Update)"""
        # Логинимся
        self.client.login(username='testuser', password='testpass123')

        # Данные для обновления
        update_data = {'name': 'Обновленный статус'}

        # Отправляем POST запрос на обновление
        response = self.client.post(
            reverse('status_update', args=[self.status.id]),
            update_data
        )

        # Проверяем редирект на список статусов
        self.assertRedirects(response, reverse('statuses_index'))

        # Обновляем данные статуса из базы
        self.status.refresh_from_db()

        # Проверяем, что имя изменилось
        self.assertEqual(self.status.name, 'Обновленный статус')

    def test_status_update_requires_login(self):
        """Тест: обновление статуса требует авторизации"""
        # Пытаемся обновить статус без логина
        response = self.client.post(
            reverse('status_update', args=[self.status.id]),
            {'name': 'Обновленный статус'}
        )

        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)

        # Проверяем, что статус не изменился
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Тестовый статус')

    def test_status_update_duplicate_name(self):
        """Тест: нельзя обновить статус на уже существующее имя"""
        # Создаем еще один статус
        Status.objects.create(name='Другой статус')

        # Логинимся
        self.client.login(username='testuser', password='testpass123')

        # Пытаемся обновить первый статус на имя второго
        response = self.client.post(
            reverse('status_update', args=[self.status.id]),
            {'name': 'Другой статус'}
        )

        # Проверяем, что форма не прошла валидацию
        self.assertEqual(response.status_code, 200)

        # Проверяем, что есть сообщение об ошибке
        self.assertContains(response, 'уже существует')

        # Проверяем, что имя не изменилось
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'Тестовый статус')

    def test_status_delete(self):
        """Тест: удаление статуса (D - Delete)"""
        # Логинимся
        self.client.login(username='testuser', password='testpass123')

        # Отправляем POST запрос на удаление
        response = self.client.post(
            reverse('status_delete', args=[self.status.id])
        )

        # Проверяем редирект на список статусов
        self.assertRedirects(response, reverse('statuses_index'))

        # Проверяем, что статус удален из базы
        self.assertFalse(Status.objects.filter(id=self.status.id).exists())

        # Проверяем, что статусов больше нет
        self.assertEqual(Status.objects.count(), 0)

    def test_status_delete_requires_login(self):
        """Тест: удаление статуса требует авторизации"""
        # Пытаемся удалить статус без логина
        response = self.client.post(
            reverse('status_delete', args=[self.status.id])
        )

        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)

        # Проверяем, что статус не удалился
        self.assertTrue(Status.objects.filter(id=self.status.id).exists())

    def test_status_delete_with_tasks(self):
        """Тест: нельзя удалить статус, связанный с задачей"""
        self.client.login(username='testuser', password='testpass123')

        # Создаем задачу, связанную со статусом
        Task.objects.create(
            name='Тестовая задача',
            description='Описание задачи',
            status=self.status,
            author=self.user
        )

        # Пытаемся удалить статус
        response = self.client.post(
            reverse('status_delete', args=[self.status.id])
        )

        # Статус не должен удалиться
        self.assertTrue(Status.objects.filter(id=self.status.id).exists())
        self.assertEqual(Status.objects.count(), 1)


    def test_status_create_page_requires_login(self):
        """Тест: страница создания статуса требует авторизации"""
        # Пытаемся открыть страницу создания без логина
        response = self.client.get(reverse('status_create'))

        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)

    def test_status_create_page_accessible_for_logged_in(self):
        """Тест: страница создания статуса доступна для залогиненных"""
        # Логинимся
        self.client.login(username='testuser', password='testpass123')

        # Открываем страницу создания
        response = self.client.get(reverse('status_create'))

        # Проверяем успешный ответ
        self.assertEqual(response.status_code, 200)

        # Проверяем, что есть форма
        self.assertContains(response, '<form')
        self.assertContains(response, 'method="post"')

    def test_status_update_page_requires_login(self):
        """Тест: страница редактирования статуса требует авторизации"""
        # Пытаемся открыть страницу редактирования без логина
        response = self.client.get(reverse('status_update', args=[self.status.id]))

        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)

    def test_status_update_page_accessible_for_logged_in(self):
        """Тест: страница редактирования статуса доступна для залогиненных"""
        # Логинимся
        self.client.login(username='testuser', password='testpass123')

        # Открываем страницу редактирования
        response = self.client.get(reverse('status_update', args=[self.status.id]))

        # Проверяем успешный ответ
        self.assertEqual(response.status_code, 200)

        # Проверяем, что форма содержит текущее имя
        self.assertContains(response, self.status.name)

    def test_status_delete_page_requires_login(self):
        """Тест: страница удаления статуса требует авторизации"""
        # Пытаемся открыть страницу удаления без логина
        response = self.client.get(reverse('status_delete', args=[self.status.id]))

        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)

    def test_status_delete_page_accessible_for_logged_in(self):
        """Тест: страница удаления статуса доступна для залогиненных"""
        # Логинимся
        self.client.login(username='testuser', password='testpass123')

        # Открываем страницу удаления
        response = self.client.get(reverse('status_delete', args=[self.status.id]))

        # Проверяем успешный ответ
        self.assertEqual(response.status_code, 200)

        # Проверяем, что есть подтверждение удаления
        self.assertContains(response, 'Вы уверены')
        self.assertContains(response, self.status.name)