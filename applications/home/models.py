from django.conf import settings
from django.db import models


class Status(models.Model):
    CATEGORY_CHOICES = [
        ('project', 'Proyecto'),
        ('task', 'Tarea'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='task')
    color = models.CharField(max_length=30, default='secondary')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.ForeignKey(Status, related_name='projects', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    status = models.ForeignKey(Status, related_name='tasks', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tasks', on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FollowUp(models.Model):
    task = models.ForeignKey(Task, related_name='follow_ups', on_delete=models.CASCADE)
    comment = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='follow_ups', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task.title} - {self.created_at:%Y-%m-%d}'


class DeveloperPerformance(models.Model):
    developer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='performance_records', on_delete=models.CASCADE)
    week_start = models.DateField()
    quota_services = models.PositiveIntegerField(default=0, help_text='Número de servicios esperados para la semana')
    completed_services = models.PositiveIntegerField(default=0, help_text='Número de servicios completados')
    progress_percentage = models.PositiveIntegerField(default=0, help_text='Avance porcentual estimado')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-week_start', '-created_at']

    def __str__(self):
        return f'{self.developer.username} - {self.week_start}'

    @property
    def performance_ratio(self):
        if self.quota_services <= 0:
            return 0
        return round((self.completed_services / self.quota_services) * 100, 1)


class Observation(models.Model):
    developer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='observations', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name='observations', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=[('low', 'Baja'), ('medium', 'Media'), ('high', 'Alta')], default='medium')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PriorityActivity(models.Model):
    PRIORITY_CHOICES = [
        ('critical', 'Crítica'),
        ('high', 'Alta'),
        ('medium', 'Media'),
        ('low', 'Baja'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En progreso'),
        ('done', 'Completada'),
    ]

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='high')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='priority_activities', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority', 'due_date', 'created_at']

    def __str__(self):
        return self.title
