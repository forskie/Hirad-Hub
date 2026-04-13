from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

"""
Модели заметок notes.

1. папки заметок пользователя (NoteFolder)
2. основную модель заметки (Note)
3. связь заметок с пользователем, шагами роадмапа и материалами
4. универсальную привязку к объектам через GenericForeignKey (resource)
5. систему лайков и комментариев через GenericRelation
6. индексы для оптимизации фильтрации и сортировки
7. метод проверки доступа к заметке (can_view)
"""


class NoteFolder(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, 
                              on_delete=models.CASCADE,
                              related_name='note_folders')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ('owner', 'name')

    def __str__(self):
        return f"{self.owner.username} / {self.name}" 

class Note(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_public = models.BooleanField(default=False)
    topics = models.ManyToManyField('library.Topic', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    img = models.ImageField(upload_to='notes/', blank=True, null=True)
    
    step = models.ForeignKey('roadmap.Step', on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')

    resource_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='notes'
    )
    resource_object_id = models.PositiveIntegerField(null=True, blank=True)
    resource = GenericForeignKey('resource_content_type', 'resource_object_id')

    folder = models.ForeignKey(
        NoteFolder,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notes'
    )

    likes = GenericRelation('library.Like')
    comments = GenericRelation('library.Comment')
    materials = models.ManyToManyField('library.Book', blank=True)        
    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', 'is_public']),
            models.Index(fields=['author', 'step']),
            models.Index(fields=['folder']),
        ]

    @staticmethod
    def can_view(user, note):
        return note.is_public or note.author == user

    @property
    def count_likes(self):
        return self.likes.count()

    @property
    def count_comments(self):
        return self.comments.count()

    def __str__(self):
        return self.title