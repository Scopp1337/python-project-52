from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from django_filters.views import FilterView

from .filters import TaskFilter
from .forms import TaskForm
from .models import Task


class TasksIndexView(LoginRequiredMixin, FilterView):
    model = Task
    template_name = 'tasks/index.html'
    context_object_name = 'tasks'
    filterset_class = TaskFilter
    paginate_by = 10
    filterset_context_name = 'filter'

    def get_filterset_kwargs(self, *args, **kwargs):
        kwargs = super().get_filterset_kwargs(*args, **kwargs)
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        # Получаем queryset от фильтра
        queryset = super().get_queryset()

        # Применяем фильтр "Только свои задачи" напрямую
        if self.request.GET.get('only_self_tasks') == 'on':
            queryset = queryset.filter(author=self.request.user)

        return queryset.order_by('-id')


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/detail.html'
    context_object_name = 'task'


class TaskCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/create.html'
    success_url = reverse_lazy('tasks_index')
    success_message = 'Задача успешно создана'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin,
                     SuccessMessageMixin, UpdateView):

    model = Task
    form_class = TaskForm
    template_name = 'tasks/update.html'
    success_url = reverse_lazy('tasks_index')
    success_message = 'Задача успешно изменена'

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'Вы не можете редактировать эту задачу')
        return redirect('tasks_index')


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin,
                     SuccessMessageMixin, DeleteView):
    model = Task
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks_index')
    success_message = 'Задача успешно удалена'

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'Задачу может удалить только ее автор')
        return redirect('tasks_index')