import django_filters
from django import forms

from labels.models import Label
from statuses.models import Status
from users.models import User

from .models import Task


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        label='Статус',
        empty_label='---------',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label='Исполнитель',
        empty_label='---------',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(),
        label='Метка',
        empty_label='---------',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    only_self_tasks = django_filters.BooleanFilter(
        method='filter_only_self_tasks',
        label='Только свои задачи',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def filter_only_self_tasks(self, queryset, name, value):
        """Фильтр для отображения только задач текущего пользователя"""
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(author=self.request.user)
        return queryset

    class Meta:
        model = Task
        fields = ['status', 'executor', 'labels', 'only_self_tasks']