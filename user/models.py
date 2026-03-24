from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    email = models.EmailField(unique=True)
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
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='user',
    )
    
    # gamification 
    score = models.PositiveIntegerField(default=0)
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