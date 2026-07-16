from django.db.models import Avg, Count, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST
from urllib.parse import urlparse

from .models import SecurityScan

from .services.tools import get_command
from .services.tool_runner import execute
from .services.parsers import (
    extract_score,
    extract_findings,
    build_recommendation,
)

AVAILABLE_TOOLS = [

    "bandit",
    "semgrep",
    "safety",
    "pip_audit",
    "pylint",
    "flake8",
    "black",
    "mypy",
    "detect_secrets",
    "radon",
    "xenon",
    "coverage",
    "pytest",
    "playwright",
    "locust",
    "pip_licenses",
    "cyclonedx",
    "wapiti",

]
def dashboard(request):
    """
    Dashboard principal del Centro DevSecOps.
    """

    scans = SecurityScan.objects.order_by("-started_at")[:20]

    return render(
        request,
        "security/dashboard.html",
        {
            "tools": AVAILABLE_TOOLS,
            "scans": scans,
        },
    )


def status_overview(request):
    """Panel visual del estado de seguridad basado en los escaneos ejecutados."""
    scans = SecurityScan.objects.all()
    status_labels = {
        'success': 'Finalizados',
        'warning': 'Advertencias',
        'error': 'Errores',
        'running': 'En ejecución',
        'pending': 'Pendientes',
    }
    status_values = [scans.filter(status=status).count() for status in status_labels]
    totals = scans.aggregate(
        total_scans=Count('id'),
        total_findings=Sum('findings'),
        average_score=Avg('score'),
        average_duration=Avg('duration'),
    )
    total_findings = totals['total_findings'] or 0
    average_score = round(totals['average_score'] or 0, 1)
    tool_rows = list(
        scans.values('tool')
        .annotate(runs=Count('id'), findings=Sum('findings'))
        .order_by('-runs', 'tool')
    )
    tool_labels = dict(SecurityScan.TOOL_CHOICES)
    tool_activity = []
    for row in tool_rows:
        tool_activity.append({
            'tool': tool_labels.get(row['tool'], row['tool']),
            'runs': row['runs'],
            'findings': row['findings'] or 0,
        })

    recent_scans = list(scans.order_by('-started_at')[:12])
    recent_scans.reverse()
    trend_labels = [scan.started_at.strftime('%d/%m %H:%M') for scan in recent_scans]
    trend_scores = [scan.score if scan.score is not None else 0 for scan in recent_scans]
    trend_findings = [scan.findings for scan in recent_scans]
    latest_scans = scans.select_related('user').order_by('-started_at')[:8]

    health_label = 'Sin datos'
    if totals['total_scans']:
        health_label = 'Estable' if average_score >= 80 else 'Atención' if average_score >= 60 else 'Crítico'

    return render(request, 'security/status_overview.html', {
        'total_scans': totals['total_scans'],
        'total_findings': total_findings,
        'average_score': average_score,
        'average_duration': round(totals['average_duration'] or 0, 1),
        'health_label': health_label,
        'latest_scans': latest_scans,
        'status_chart': {'labels': list(status_labels.values()), 'values': status_values},
        'tool_chart': {
            'labels': [row['tool'] for row in tool_activity],
            'values': [row['runs'] for row in tool_activity],
        },
        'trend_chart': {
            'labels': trend_labels,
            'scores': trend_scores,
            'findings': trend_findings,
        },
    })

@require_POST
def run_tool(request, tool):
    """
    Ejecuta una herramienta de seguridad.
    """

    if tool not in AVAILABLE_TOOLS:
        return JsonResponse(
            {
                "success": False,
                "message": "Herramienta no soportada.",
            },
            status=400,
        )

    target_url = request.POST.get("target_url", "").strip()

    # Estas herramientas requieren una URL
    if tool in ["wapiti", "locust", "playwright"] and not target_url:
        return JsonResponse(
            {
                "success": False,
                "message": "Debe ingresar una URL objetivo.",
            },
            status=400,
        )

    if target_url:
        parsed = urlparse(target_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return JsonResponse(
                {"success": False, "message": "La URL debe comenzar por http:// o https://."},
                status=400,
            )

    command = get_command(tool, target_url)

    if command is None:
        return JsonResponse(
            {
                "success": False,
                "message": "La herramienta no está disponible o no fue posible construir el comando.",
            },
            status=400,
        )

    scan = SecurityScan.objects.create(
        tool=tool,
        target_url=target_url,
        user=request.user if request.user.is_authenticated else None,
        status="running",
    )

    result = execute(command)

    output = result["output"]

    score = extract_score(tool, output)
    findings = extract_findings(tool, output)
    recommendation = build_recommendation(tool, output)

    scan.status = result["status"]
    scan.output = output
    scan.duration = result["duration"]
    scan.finished_at = timezone.now()
    scan.score = score
    scan.findings = findings
    scan.recommendations = recommendation

    scan.save()

    return JsonResponse(
        {
            "success": True,
            "tool": tool,
            "status": result["status"],
            "return_code": result["return_code"],
            "duration": result["duration"],
            "score": score,
            "findings": findings,
            "recommendation": recommendation,
            "output": output,
        }
    )
