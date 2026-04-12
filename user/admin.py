from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TeacherProfile, DirectorProfile, School
@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'score', 'level', 'title', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'bio', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Gamification', {'fields': ('score', 'level', 'title')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'teacher_level', 'teacher_score', 'teacher_title', 'is_verified', 'materials_uploaded')
    list_filter = ('school', 'teacher_level', 'is_verified')
    search_fields = ('user__username', 'school__name', 'user__email')
    readonly_fields = ('materials_uploaded', 'teacher_score', 'total_likes_received', 'created_at')

@admin.register(DirectorProfile)
class DirectorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'can_verify_teachers', 'created_at')
    list_filter = ('school', 'can_verify_teachers')
    search_fields = ('user__username', 'school__name', 'user__email')


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'city')
    search_fields = ('name', 'number', 'city')