from django import forms
from .models import Task
from labels.models import Label


class TaskForm(forms.ModelForm):
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'multiple': 'multiple',
            'size': 5
        }),
        label='Метки'
    )

    class Meta:
        model = Task
        fields = ['name', 'description', 'status', 'executor', 'labels']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }