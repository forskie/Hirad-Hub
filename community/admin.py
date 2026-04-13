from django.contrib import admin
from .models import Community, CommunityMembership, CommunityPost

"""
Показ Community в админке 
"""
@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display  = ('name', 'creator', 'topic', 'is_private', 'member_count', 'created_at')
    list_filter   = ('is_private',)
    search_fields = ('name', 'creator__username')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

    def member_count(self, obj):
        return obj.memberships.filter(is_approved=True).count()
    member_count.short_description = 'Members'


@admin.register(CommunityMembership)
class CommunityMembershipAdmin(admin.ModelAdmin):
    list_display  = ('user', 'community', 'role', 'is_approved', 'joined_at')
    list_filter   = ('role', 'is_approved')
    search_fields = ('user__username', 'community__name')


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('community', 'post', 'pinned', 'created_at')
    list_filter  = ('pinned',)