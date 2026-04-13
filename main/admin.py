from django.contrib import admin

from main.views import User
from .models import Dashboard
from django.contrib.auth import get_user_model


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_score', 'level', 'post_count', 'note_count', 'rank', 'last_update')
    search_fields = ('user__username',)
    list_filter = ('user__level',)
    readonly_fields = ('last_update',)

    def level(self, obj):
        return obj.user.level
    level.short_description = 'Level'

    def total_score(self, obj):
        return obj.user.score
    total_score.short_description = 'Score'
    
    def rank(self, obj):
        User = get_user_model()
        return User.objects.filter(score__gt=obj.user.score).count() + 1
    rank.short_description = 'Rank'
    
    def post_count(self, obj):
        return obj.user.posts.count()
    post_count.short_description = 'Posts'
    
    def notes_count(self, obj):
        return obj.user.notes.count()
    notes_count.short_description = 'Notes Count'