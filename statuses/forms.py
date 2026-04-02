from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Status


class StatusForm(ModelForm):
    class Meta:
        model = Status
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if not self.instance.pk:
            if Status.objects.filter(name=name).exists():
                raise ValidationError('Статус с таким именем уже существует')
        else:
            if Status.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Статус с таким именем уже существует')

        return name