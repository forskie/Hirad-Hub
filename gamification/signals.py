from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from note.models import Note
from post.models import Post
from library.models import Like
from roadmap.models import UserProgress

from .constants import NOTE_CREATE_POINTS, POST_CREATE_POINTS, LIKE_RECEIVED_POINTS, STEP_COMPLETION_POINTS
from .utils import add_score
from django.utils import timezone


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
    if not created:
        return
    content = instance.content_object
    if not hasattr(content, 'uploaded_by'):
        return
    uploader = content.uploaded_by
    if uploader == instance.user:
        return
    add_score(uploader, LIKE_RECEIVED_POINTS)

@receiver(pre_save, sender=UserProgress)
def reward_step_completion(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = UserProgress.objects.get(pk=instance.pk)
    except UserProgress.DoesNotExist:
        return
    if not previous.completed and instance.completed:
        instance.completed_at = timezone.now()
        add_score(instance.user, STEP_COMPLETION_POINTS)
