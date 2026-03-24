from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.conf import settings

class Topic(models.Model):
    name = models.CharField(max_length=122, unique=True)
    def __str__(self):
        return self.name
    

class LibraryItem(models.Model):
    TYPE_CHOICES = (
        ('book', 'Book'),
        ('podcast', 'Podcast'),
        ('video', 'Video'),
        ('note', 'Note'),
    )
    
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    material_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True)
    topics = models.ManyToManyField(Topic, blank=True)
    note = models.ForeignKey('note.Note', on_delete=models.SET_NULL,
                            blank=True, null=True)
    file = models.FileField(upload_to='library/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    likes = GenericRelation('library.Like')
    comments = GenericRelation('library.Comment')
    
    def __str__(self):
        return f"{self.title} ({self.material_type})"
    
    def content_type(self):
        if self.material_type == 'book':
            if self.file:
                return self.file.name.split('.')[-1]
            return 'no_file'
        elif self.material_type == 'podcast':
            return 'audio'
        elif self.material_type == 'video':
            return 'video'
        elif self.material_type == 'note':
            return 'note'
        return 'unknown'
    
class LibraryInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(LibraryItem, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)
    
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
    
    
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    def __str__(self):
        return f"Comment by {self.user} at {self.created_at}"





















