from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'text', 'created_at',
    'updated_at', 'image', 'video', 'count_likes', 'count_comments')
    list_filter = ('created_at', 'updated_at', 'author')
    search_fields = ('text', 'author__username')
    filter_horizontal = ('topics',)
    
    def count_likes(self, obj):
        return obj.likes.count()
    count_likes.short_description = 'Likes'
    
    def count_comments(self, obj):
        return obj.comments.count()
    count_comments.short_description = 'Comments'