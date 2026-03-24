from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'score', 'level', 'title', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Gamification', {'fields': ('score', 'level', 'title')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )