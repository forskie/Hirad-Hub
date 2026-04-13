from django.contrib import admin
from .models import Note
"""
Базовые отоьражение админки
"""
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_author', 'is_public', 'created_at', 'updated_at')
    list_filter = ('is_public', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__username')
    filter_horizontal = ('topics',)
    
    def get_author(self, obj):
        return obj.author
    get_author.short_description = 'Author'