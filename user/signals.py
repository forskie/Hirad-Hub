from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TeacherProfile, CustomUser, DirectorProfile

@receiver(post_save, sender=CustomUser)
def create_role_profile(sender, instance, created, **kwargs):
    if instance.role == 'teacher':
        TeacherProfile.objects.create(user=instance)
    elif instance.role == 'director':
        DirectorProfile.objects.create(user=instance)
        TeacherProfile.objects.create(user=instance)