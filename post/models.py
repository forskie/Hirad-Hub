from django.conf import settings
from django.db import models
from library.models import ContentType, Topic
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class Post(models.Model):
    POST_TYPES_CHOICES = [
        ('post', 'Post'),
        ('question', 'Question'),
        ('article', 'Article'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=20, choices=POST_TYPES_CHOICES, default='post', db_index=True)


    text = models.TextField(max_length=10000, blank=True)
    image = models.ImageField(upload_to='post/images/', null=True, blank=True)
    video = models.FileField(upload_to='post/videos/', null=True, blank=True)
    
    is_answered = models.BooleanField(default=False, db_index=True)
    accepted_comment = models.OneToOneField('library.Comment', null=True, blank=True, on_delete=models.SET_NULL, related_name='accepted_for')

    view_count = models.PositiveIntegerField(default=0, db_index=True)
    step = models.PositiveIntegerField(default=0, db_index=True) 


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topics = models.ManyToManyField(Topic, related_name='posts', blank=True)
    
    likes = GenericRelation('library.Like')
    comments = GenericRelation('library.Comment')
    favorites = GenericRelation('post.Favorite')

    
    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['post_type']),
            models.Index(fields=['author', 'post_type']),
        ]

    @property
    def count_likes(self):
        return self.likes.count()

    @property
    def count_comments(self):
        return self.comments.count()

    def increment_views(self):
        Post.objects.filter(pk=self.pk).update(view_count=models.F('view_count') + 1)

    def __str__(self):
        return f"[{self.get_post_type_display()}] {self.author} : {self.text[:30]}..."


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
    