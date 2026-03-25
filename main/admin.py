from django.contrib import admin
from .models import Dashboard

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_score', 'level', 'post_count', 'note_count', 'rank')
    search_fields = ('user__username', 'level',)
    list_filter = ('level',)
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    
    def rank(self, obj):
        rank = Dashboard.objects.filter(
            total_score__gt=obj.total_score
        ).count() + 1
        return rank
    rank.short_description = 'Rank'
        
    
    def post_count(self, obj):
        return obj.user.posts.count()
    
    def note_count(self, obj):
        return obj.user.note_set.count()