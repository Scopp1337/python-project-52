from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Status


class StatusForm(ModelForm):
    class Meta:
        model = Status
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            return name

        # Проверяем уникальность
        exists = Status.objects.filter(name=name)
        if self.instance.pk:
            exists = exists.exclude(pk=self.instance.pk)

        if exists.exists():
            raise ValidationError(
                'Статус с таким именем уже существует'
            )

        return name