from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation

from django.db import models
from django.conf import settings


class Category(models.Model):
    CATEGORY_TYPES = [
        ('school', 'School Materials'),
        ('national', 'National Literature'),
        ('olympiad', 'Olympiad Prep'),
        ('general', 'Genaral'), 
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, 
                               on_delete=models.SET_NULL, related_name='children')
    order = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=50, blank=True) 

    category_type = models.CharField(choices=CATEGORY_TYPES, max_length=20, default='general' )
    
    description = models.TextField(blank=True)


    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Categories'
    

    def __str__(self):
        return self.name


class Topic(models.Model):
    name = models.CharField(max_length=122, unique=True)
    slug = models.SlugField(max_length=122, unique=True, auto_created=True)
    def __str__(self):
        return self.name
    
class BaseMaterial(models.Model):
    LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, blank=True, db_index=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    likes = GenericRelation('Like', related_query_name='materials')
    comments = GenericRelation('Comment', related_query_name='materials')
    created_at = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    grade = models.PositiveSmallIntegerField(null=True, blank=True)
    subject = models.CharField(max_length=100, blank=True)

    @property
    def count_likes(self):
        return self.likes.count()  
    
    @property
    def count_comments(self):
        return self.comments.count()
    
    
    class Meta:
        abstract = True
    def __str__(self):
        return f"{self.title} ({self.get_level_display()})"
    
class Book(BaseMaterial):
    file = models.FileField(upload_to='library/books/')
    pages = models.PositiveIntegerField(null=True, blank=True)
    author = models.CharField(max_length=255, blank=True, db_index=True)
    topics = models.ManyToManyField(Topic, related_name='books', blank=True)


class Video(BaseMaterial):
    video_file = models.FileField(upload_to='library/videos/')
    duration = models.DurationField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='library/videos/thumbnails/', null=True, blank=True)
    author = models.CharField(max_length=255, blank=True, db_index=True)
    topics = models.ManyToManyField(Topic, related_name='videos', blank=True)
    

class Podcast(BaseMaterial):
    audio_file = models.FileField(upload_to='library/podcasts/')
    duration = models.DurationField(null=True, blank=True)
    author = models.CharField(max_length=255, blank=True, db_index=True)
    thumbnail = models.ImageField(upload_to='library/podcasts/thumbnails/', null=True, blank=True)
    topics = models.ManyToManyField(Topic, related_name='podcasts', blank=True)


class LibraryInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = GenericForeignKey('content_type', 'object_id')   
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    
    progress = models.FloatField(default=0.0)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)

    
    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
    

    def __str__(self):
        return f"{self.user} - {self.item}"
    
    
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        indexes = [
            models.indexes.Index(fields=['content_type', 'object_id']),
        ]
    

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.indexes.Index(fields=['content_type', 'object_id']),
        ]


    def __str__(self):
        return f"Comment by {self.user} at {self.created_at}"





















