from django.contrib import admin
from .models import Topic, LibraryItem, LibraryInteraction, Like, Comment

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    

@admin.register(LibraryItem)
class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'material_type', 'level', 'date_added')
    list_filter = ('material_type', 'level', 'topics')
    search_fields = ('title', 'author', 'description')
    filter_horizontal = ('topics',)
    
@admin.register(LibraryInteraction)
class LibraryInteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__username', 'item__title')
    
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'created_at')
    search_fields = ('user__username',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'created_at', 'parent')
    search_fields = ('user__username', 'text')