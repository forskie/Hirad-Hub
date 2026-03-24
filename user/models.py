from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):

    LEVELS = [
        (1000,   1, 'Newcomer'),   
        (5000,   2, 'Reader'),
        (10000,  3, 'Curious'),
        (20000,  4, 'Connoisseur'),
        (35000,  5, 'Researcher'),
        (45000,  6, 'Analyst'),
        (55000,  7, 'Erudite'),
        (70000,  8, 'Intellectual'),
        (85000,  9, 'Thinker'),
        (100000, 10, 'Hiradcore'),
    ]

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
    
    
    def update_level_and_title(self):
        score = int(self.score)
        new_level = self.LEVELS[0][1]       
        new_title = self.LEVELS[0][2]
        

        for points, level, title in self.LEVELS:
            if score >= points:
                new_level = level
                new_title = title
            else:
                break   
        self.level = new_level
        self.title = new_title
        
        return new_level, new_title
        
    def add_score(self, points: int):
        if not isinstance(points, int):
            raise ValueError("Points must be an integer.")
        if points <= 0:
            return
        self.score += points
        old_level = self.level
        old_title = self.title
        new_level, new_title =  self.update_level_and_title()

        update_fields = ['score']
        
        if old_level != new_level:
            update_fields.append('level')
        if old_title != new_title:
            update_fields.append('title')
            
        self.save(update_fields=update_fields)  



    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return f"{self.get_full_name() or self.username} — {self.title}"