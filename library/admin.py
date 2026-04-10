from django.contrib import admin
from .models import Topic, Book, Video, Podcast, LibraryInteraction, Like, Comment, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'parent', 'order')
    list_filter = ('category_type',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('user', 'text', 'created_at')
    can_delete = True
    
class LikeInline(admin.TabularInline):
    model = Like
    extra = 0
    readonly_fields = ('user', 'created_at')
    can_delete = True    
    
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'level', 'created_at', 'count_likes', 'count_comments', 'author')
    filter_horizontal = ('topics',) 
    search_fields = ('title', 'author', 'description')
    list_filter = ('level', 'topics')
    
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'level', 'created_at', 'count_likes', 'count_comments', 'author')
    filter_horizontal = ('topics',) 
    search_fields = ('title', 'author', 'description')
    list_filter = ('level', 'topics')
    

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'level', 'created_at', 'count_likes', 'count_comments', 'author')
    filter_horizontal = ('topics',) 
    search_fields = ('title', 'author', 'description')
    list_filter = ('level', 'topics')
    
    
@admin.register(LibraryInteraction)
class LibraryInteractionAdmin(admin.ModelAdmin):    
    list_display = ('id', 'user', 'item', 'progress', 'rating', 'completed', 'date_completed')
    search_fields = ('user__username', 'item__title')
    list_filter = ('completed','rating')
    
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_object', 'created_at')
    search_fields = ('user__username',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'created_at', 'parent')
    search_fields = ('user__username', 'text')
    list_filter = ('content_type',)