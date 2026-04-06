from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.conf import settings
class Dashboard(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Dashboard" 

    @property
    def total_score(self):
        return self.user.score

    @property
    def level(self):
        return self.user.level

    @property
    def post_count(self):
        return self.user.posts.count()

    def note_count(self):
        return self.user.notes.count()    
