from django.db import models

class Label(models.Model):
    name = models.CharField(
        max_length=150, 
        unique=True,
        blank=False,
        verbose_name='Имя'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Метка'
        verbose_name_plural = 'Метки'