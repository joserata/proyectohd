from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ScanTarget(models.Model):

    name = models.CharField(max_length=150)

    url = models.URLField(unique=True)

    description = models.TextField(blank=True)

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ScanExecution(models.Model):

    STATUS = [

        ("pending", "Pendiente"),

        ("running", "Ejecutando"),

        ("finished", "Finalizado"),

        ("error", "Error"),

    ]

    target = models.ForeignKey(

        ScanTarget,

        on_delete=models.CASCADE

    )

    tool = models.CharField(max_length=50)

    user = models.ForeignKey(

        User,

        null=True,

        blank=True,

        on_delete=models.SET_NULL

    )

    status = models.CharField(

        max_length=20,

        choices=STATUS,

        default="pending"

    )

    started_at = models.DateTimeField(auto_now_add=True)

    finished_at = models.DateTimeField(

        null=True,

        blank=True

    )

    duration = models.FloatField(default=0)

    score = models.FloatField(default=0)

    findings = models.IntegerField(default=0)

    report = models.TextField(blank=True)

    recommendation = models.TextField(blank=True)

    def __str__(self):

        return f"{self.tool} - {self.target}"