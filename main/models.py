from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.conf import settings
class Dashboard(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_score = models.PositiveIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=1)
    post_count = models.PositiveIntegerField(default=0)
    notes_count = models.PositiveIntegerField(default=0)
    
    last_update = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} Dashboard" 
    
