from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from hirad_hub import settings

class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, validators=[phone_regex])
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, default='student', 
    choices=[('student', 'Student'), ('teacher', 'Teacher'), ('director', 'Director'), ('admin', 'Admin'  )])
    # school = models.ForeignKey('school.School', on_delete=models.SET_NULL, 
    # blank=True, null=True, related_name='users')
    username = models.CharField(max_length=150, unique=True)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='user',
    )
    
    # gamification 
    score = models.PositiveIntegerField(default=0, db_index=True)
    level = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=50, blank=True, default='Newcomer')
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='user',
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return f"{self.get_full_name() or self.username} — {self.title}"
    

class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    
    
    teacher_score = models.PositiveIntegerField(default=0, db_index=True)
    teacher_level = models.PositiveIntegerField(default=1)
    teacher_title = models.CharField(max_length=50, blank=True, default='Novice')
    
    materials_uploaded = models.PositiveIntegerField(default=0)
    total_likes_received = models.PositiveIntegerField(default=0)
    total_students_helped = models.PositiveIntegerField(default=0)

    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='verified_teachers')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Teacher Profile'
        verbose_name_plural = 'Teacher Profiles'

    def __str__(self):
        return f'Teacher Profile for {self.user.get_full_name() or self.user.username}'
    
class DirectorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='director_profile')
    
    can_verify_teachers = models.BooleanField(default=True)
    can_manage_roadmaps = models.BooleanField(default=True)
    can_manage_library = models.BooleanField(default=True)

    techers_verified = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Director Profile'
        verbose_name_plural = 'Director Profiles'

    def __str__(self):
        return f"{self.user.username} - Director Profile"