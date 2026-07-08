from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import SecurityScan

from .services.tools import TOOLS
from .services.tool_runner import execute
from .services.parsers import (
    extract_score,
    extract_findings,
    build_recommendation,
)


def dashboard(request):
    """
    Dashboard principal del Centro DevSecOps.
    """

    scans = SecurityScan.objects.order_by("-started_at")[:20]

    return render(
        request,
        "security/dashboard.html",
        {
            "tools": TOOLS.keys(),
            "scans": scans,
        },
    )


@require_POST
def run_tool(request, tool):
    """
    Ejecuta una herramienta de seguridad.
    """

    if tool not in TOOLS:

        return JsonResponse(
            {
                "success": False,
                "message": "Herramienta no soportada.",
            },
            status=400,
        )

    target_url = request.POST.get("target_url", "").strip()

    command = TOOLS[tool].copy()

    # Herramientas que requieren URL
    if tool in ["locust", "wapiti"] and target_url:

        if tool == "locust":
            command.extend(["--host", target_url])

        elif tool == "wapiti":
            command.append(target_url)

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