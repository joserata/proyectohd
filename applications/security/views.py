from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

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

    command = get_command(tool, target_url)

    if command is None:
        return JsonResponse(
            {
                "success": False,
                "message": "No fue posible construir el comando.",
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