# users/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Имя',  # Исправлено
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Фамилия',  # Исправлено
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Имя пользователя',  # Исправлено
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Пароль',  # Исправлено
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',  # Исправлено
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if len(password1) < 3:
                self.add_error('password1', 'Введенный пароль слишком короткий')
            if password1 != password2:
                self.add_error('password2', 'Введенные пароли не совпадают')
        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Имя',  # Исправлено
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Фамилия',  # Исправлено
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Имя пользователя',  # Исправлено
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Пользователь с таким именем уже существует')
        return username


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя',  # Исправлено
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    # Исправлено: поле должно называться password, а не password1
    password = forms.CharField(
        label='Пароль',  # Исправлено
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )