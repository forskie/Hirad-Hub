from django.contrib import admin
from .models import Roadmap, Step, UserProgress, StepResource
from django.contrib.contenttypes.models import ContentType


class StepResourceInline(admin.TabularInline):
    model = StepResource
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "content_type":
            kwargs["queryset"] = ContentType.objects.filter(
                model__in=['book', 'video', 'podcast']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class StepInline(admin.TabularInline):
    model = Step
    extra = 1
    ordering = ('order',)


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'creator', 'is_public', 'created_at')
    list_filter = ('is_public', 'topic', 'created_at')
    search_fields = ('title', 'description')
    inlines = [StepInline]


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ('title', 'roadmap', 'order')
    list_filter = ('roadmap',)
    ordering = ('roadmap', 'order')
    inlines = [StepResourceInline]


@admin.register(StepResource)
class StepResourceAdmin(admin.ModelAdmin):
    list_display = ('step', 'content_type', 'object_id', 'is_primary')
    list_filter = ('content_type', 'is_primary')


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'step', 'completed', 'completed_at')
    list_filter = ('completed', 'step__roadmap')
    search_fields = ('user__username',)