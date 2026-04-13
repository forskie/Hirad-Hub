from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.html import strip_tags
from django.core.validators import RegexValidator

from .models import School, TeacherProfile

"""
Формы аутентификации и профиля пользователей.

1. регистрация обычного пользователя (CustomUserCreationForm)
2. вход по email с кастомной аутентификацией (CustomUserLoginForm)
3. обновление профиля пользователя (CustomUserUpdateForm)
4. регистрация преподавателя с привязкой к школе (TeacherRegistrationForm)

Дополнительно:
1. валидация email на уникальность
2. проверка телефона по формату +992XXXXXXXXX
3. назначение ролей пользователей (student, teacher)
4. создание TeacherProfile при регистрации преподавателя
5. очистка входных данных (strip_tags для phone_number)
"""

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your email'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'Last name'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'input-register form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'input-register form-control', 'placeholder': 'Confirm password'})
    )
    phone_number = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+992\d{9}$', "Enter phone number in +992 format")],
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'Phone number'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email 
        user.role = 'student'
        if commit:
            user.save()
        return user

class CustomUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Email',
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'input-register form-control', 'placeholder': 'Your email'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your password'})
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Invalid email or password.')
            elif not self.user_cache.is_active:
                raise forms.ValidationError('This account is inactive.')
        return self.cleaned_data

class CustomUserUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+992\d{9}$', "Enter phone number in +992 format")],
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'Phone number'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your email'})
    )
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Teacher'), ('director', 'Director'), ('admin', 'Admin')],
        required=False,
        widget=forms.Select(attrs={'class': 'input-register form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'bio', 'role')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('phone_number'):
            cleaned_data['phone_number'] = strip_tags(cleaned_data['phone_number'])
        return cleaned_data
    

class TeacherRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        required=True,
        max_length=50,)
    last_name = forms.CharField(
        required=True,
        max_length=50,)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+992\d{9}$', "Enter phone number in +992 format")])
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        required=True,
        empty_label="-select school-"
    )
    subject = forms.CharField(required=True, max_length=100, 
    widget=forms.TextInput(attrs={'placeholder': 'e.g. Philosophy, Math'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2', 'school', 'subject')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use :(')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.role = 'teacher'
        if commit:
            user.save()
            profile, _ = TeacherProfile.objects.get_or_create(user=user)
            profile.school = self.cleaned_data.get('school')
            profile.save(update_fields=['school'])
        return user
    