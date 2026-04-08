from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from .models import Label
from .forms import LabelForm
from tasks.models import Task  # Добавляем импорт


class LabelsIndexView(LoginRequiredMixin, ListView):
    model = Label
    template_name = 'labels/index.html'
    context_object_name = 'labels'


class LabelCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Label
    form_class = LabelForm
    template_name = 'labels/create.html'
    success_url = reverse_lazy('labels_index')
    success_message = 'Метка успешно создана'


class LabelUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = 'labels/update.html'
    success_url = reverse_lazy('labels_index')
    success_message = 'Метка успешно изменена'


class LabelDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Label
    template_name = 'labels/delete.html'
    success_url = reverse_lazy('labels_index')
    success_message = 'Метка успешно удалена'

    def post(self, request, *args, **kwargs):
        label = self.get_object()

        # Проверяем, есть ли задачи с этой меткой
        if Task.objects.filter(labels=label).exists():
            messages.error(request, 'Невозможно удалить метку')
            return redirect(self.success_url)

        label.delete()
        messages.success(request, self.success_message)
        return redirect(self.success_url)