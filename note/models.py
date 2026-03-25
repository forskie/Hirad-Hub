from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation


class Note(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_public = models.BooleanField(default=False)
    topics = models.ManyToManyField('library.Topic', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    img = models.ImageField(upload_to='notes/', blank=True, null=True)
    
    likes = GenericRelation('library.Like')
    comments = GenericRelation('library.Comment')
    
    
    @staticmethod
    def can_view(user, note):
        return note.is_public or note.author == user
    
    materials = models.ManyToManyField('library.Book', blank=True)
    
    def __str__(self):
        return self.title