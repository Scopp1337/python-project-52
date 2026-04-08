from django.contrib.auth import get_user_model
from django.db import models

from labels.models import Label

User = get_user_model()


class Task(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    status = models.ForeignKey(
        'statuses.Status',
        on_delete=models.PROTECT,
        verbose_name='Статус'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='author_tasks',
        verbose_name='Автор'
    )
    executor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='executor_tasks',
        verbose_name='Исполнитель'
    )

    labels = models.ManyToManyField(
        Label,
        blank=True,
        verbose_name='Метки'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'