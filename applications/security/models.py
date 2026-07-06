from django.db import models
from django.contrib.auth.models import User


class SecurityScan(models.Model):
    """
    Registro de una ejecución de una herramienta de seguridad/calidad.
    """

    TOOL_CHOICES = [
        ("bandit", "Bandit"),
        ("semgrep", "Semgrep"),
        ("safety", "Safety"),
        ("pylint", "Pylint"),
        ("playwright", "Playwright"),
        ("locust", "Locust"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("running", "Ejecutando"),
        ("success", "Finalizado"),
        ("warning", "Advertencia"),
        ("error", "Error"),
    ]

    tool = models.CharField(
        max_length=30,
        choices=TOOL_CHOICES
    )

    target_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL Analizada"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    started_at = models.DateTimeField(auto_now_add=True)

    finished_at = models.DateTimeField(
        blank=True,
        null=True
    )

    duration = models.FloatField(
        default=0,
        help_text="Duración en segundos"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    score = models.FloatField(
        blank=True,
        null=True
    )

    findings = models.IntegerField(
        default=0
    )

    recommendations = models.TextField(
        blank=True
    )

    output = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Escaneo"
        verbose_name_plural = "Escaneos"

    def __str__(self):
        return f"{self.get_tool_display()} - {self.started_at:%Y-%m-%d %H:%M}"