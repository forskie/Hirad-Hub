from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from note.models import Note
from post.models import Post
from library.models import Like, Book, Video, Podcast
from roadmap.models import UserProgress
from user.models import TeacherProfile
from .constants import NOTE_CREATE_POINTS, POST_CREATE_POINTS, LIKE_RECEIVED_POINTS, STEP_COMPLETION_POINTS, TEACHER_LEVELS, MATERIAL_UPLOAD_POINTS, MATERIAL_LIKE_RECEIVED_POINTS, MATERIAL_COMMENT_RECEIVED_POINTS
from .utils import add_score, add_teacher_score
from django.utils import timezone



"""
Сиситема начисление очков за какую-то дуйствие
"""

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
    if not content:
        return
    creator = getattr(content, 'creator', None)
    if not creator or creator == instance.user:
        return
    add_score(creator, LIKE_RECEIVED_POINTS)
    profile = get_teacher_profile(creator)
    if profile:
        profile.total_likes_received += 1
        profile.save(update_fields=['total_likes_received'])
        add_teacher_score(profile, MATERIAL_LIKE_RECEIVED_POINTS)

            
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


# _____ TEACHER SIGNALS _____

def get_teacher_profile(user):
    try:
        return TeacherProfile.objects.get(user=user)
    except TeacherProfile.DoesNotExist:
        return None
    
@receiver(post_save, sender=Book)
@receiver(post_save, sender=Video)
@receiver(post_save, sender=Podcast)
def reward_material_upload(sender, instance, created, **kwargs):
    if not created:
        return
    if not instance.creator:
        return
    profile = get_teacher_profile(instance.creator)
    if not profile:
        return
    profile.materials_uploaded += 1
    profile.save(update_fields=['materials_uploaded'])
    add_teacher_score(profile, MATERIAL_UPLOAD_POINTS)

    
