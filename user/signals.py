from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TeacherProfile, CustomUser, DirectorProfile

@receiver(post_save, sender=CustomUser)
def create_role_profile(sender, instance, created, **kwargs):
    if instance.role == 'teacher':
        TeacherProfile.objects.get_or_create(user=instance)
    elif instance.role == 'director':
        DirectorProfile.objects.get_or_create(user=instance)
        TeacherProfile.objects.get_or_create(user=instance)