from django.contrib import admin

from .models import DeveloperPerformance, FollowUp, Observation, PriorityActivity, Project, Status, Task


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'color', 'created_at')
    search_fields = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('status',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'assigned_to', 'priority', 'due_date')
    search_fields = ('title', 'description')
    list_filter = ('status', 'priority', 'project')


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ('task', 'created_by', 'created_at')
    search_fields = ('comment',)
    list_filter = ('task',)


@admin.register(DeveloperPerformance)
class DeveloperPerformanceAdmin(admin.ModelAdmin):
    list_display = ('developer', 'week_start', 'quota_services', 'completed_services', 'progress_percentage', 'performance_ratio')
    list_filter = ('week_start', 'developer')
    search_fields = ('developer__username', 'notes')


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ('developer', 'task', 'title', 'severity', 'created_at')
    list_filter = ('severity', 'developer')
    search_fields = ('title', 'description')
