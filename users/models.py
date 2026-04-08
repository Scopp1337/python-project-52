from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='First Name'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Last Name'
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'