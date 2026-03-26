from django.db.models.signals import post_save
from django.dispatch import receiver
from note.models import Note
from post.models import Post
from library.models import Like
from .constants import NOTE_CREATE_POINTS, POST_CREATE_POINTS, LIKE_RECEIVED_POINTS
from .utils import add_score
@receiver(post_save, sender=Note)
def reward_note(sender, instance, created, **kwargs):
    if created:
        add_score(instance.author, NOTE_CREATE_POINTS)
    
    
@receiver(post_save, sender=Post)
def reward_post(sender, instance, created, **kwargs):
    if created:
        add_score(instance.author, POST_CREATE_POINTS)


@receiver(post_save, sender=Like)
def reward_like(sender, instance, created, **kwargs):
    if created and hasattr(instance.content_object, 'author'):
        add_score(LIKE_RECEIVED_POINTS)
    