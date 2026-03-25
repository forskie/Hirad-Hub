from django.conf import settings
from django.db import models
from library.models import ContentType, Topic
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    
    text = models.TextField(max_length=10000, blank=True)
    image = models.ImageField(upload_to='post/images/', null=True, blank=True)
    video = models.FileField(upload_to='post/videos/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topics = models.ManyToManyField(Topic, related_name='posts', blank=True)
    
    likes = GenericRelation('library.Like')
    comments = GenericRelation('library.Comment')
    favorites = GenericRelation('post.Favorite')
    
    
    def __str__(self):
        return f"{self.author} : {self.text[:30]}..."

class Favorite(models.Model):
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
    