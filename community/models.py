"""
Community models:
1. Community - базовая модел принимаюшая главных данных
2. CommunityMembership - рол юзера в Community
3. CommunityPost - посты отправшийся в Community от юзера
"""
from django.db import models
from django.conf import settings
from django.db import models
from library.models import Topic


class Community(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True)
    description = models.TextField(blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='communities')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_communities')
    avatar = models.ImageField(upload_to='community/avatars/', blank=True, null=True)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'communities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['creator']),
        ]

    def __str__(self):
        return self.name

    def member_count(self):
        return self.memberships.filter(is_approved=True).count()

    def is_member(self, user):
        if not user.is_authenticated:
            return False
        return self.memberships.filter(user=user, is_approved=True).exists()

    def is_admin(self, user):
        if not user.is_authenticated:
            return False
        return self.memberships.filter(user=user, role__in=('admin', 'moderator'), is_approved=True).exists()


class CommunityMembership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_approved = models.BooleanField(default=True)  
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'user')
        indexes = [
            models.Index(fields=['community', 'is_approved']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.user.username} → {self.community.name} ({self.role})'


class CommunityPost(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_posts')
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE, related_name='community_reposts')
    pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'post')
        ordering = ['-pinned', '-created_at']