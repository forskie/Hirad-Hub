from django.db import models
from hirad_hub import settings
from library.models import Topic
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Q, UniqueConstraint

class Roadmap(models.Model):
    title = models.CharField(max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    is_public = models.BooleanField(default=True)       
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        indexes = [
            models.Index(fields=['topic']),
            models.Index(fields=['is_public']),
        ]
    
class Step(models.Model):
    roadmap = models.ForeignKey(Roadmap, related_name='steps', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    resource_url = models.URLField(blank=True, help_text='Optional direct link to material for this step')
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
        unique_together = ('roadmap', 'order')

class StepResource(models.Model):
    step = models.ForeignKey(Step, related_name='resources', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return str(self.content_object) if self.content_object else "No Title"
    
    def clean(self):
        allowed_models = ['book', 'video', 'podcast']
        if self.content_type.model not in allowed_models:
            raise ValidationError("Invalid resource type")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['step'],
                condition=Q(is_primary=True),
                name='unique_primary_resource_per_step'
            )
        ]

class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        
        unique_together = ('user', 'step')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['step']),
            models.Index(fields=['user', 'completed'])
        ]