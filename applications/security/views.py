import os
import re
import sys
import time
import subprocess

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import SecurityScan


PYTHON = sys.executable
BASE_DIR = settings.BASE_DIR


TOOLS = {

    "bandit": [
        PYTHON,
        "-m",
        "bandit",
        "-r",
        "applications",
    ],

    "semgrep": [
        PYTHON,
        "-m",
        "semgrep",
        "scan",
        "--config",
        "p/python",
        "applications",
    ],

    "safety": [
        PYTHON,
        "-m",
        "safety",
        "scan",
    ],

    "pylint": [
        PYTHON,
        "-m",
        "pylint",
        "--recursive=y",
        "applications",
    ],

    "playwright": [
        PYTHON,
        "tests/e2e/playwright_smoke.py",
    ],

    "locust": [
        PYTHON,
        "-m",
        "locust",
        "-f",
        "locustfile.py",
        "--headless",
        "-u",
        "10",
        "-r",
        "2",
        "-t",
        "20s",
    ],

}


def dashboard(request):

    scans = SecurityScan.objects.order_by("-started_at")[:20]

    return render(
        request,
        "security/dashboard.html",
        {
            "tools": TOOLS.keys(),
            "scans": scans,
        },
    )


def build_recommendation(tool, output):

    if tool == "bandit":

        if "High: 0" in output:
            return "No se encontraron vulnerabilidades críticas."

        return "Revise las vulnerabilidades detectadas por Bandit."

    if tool == "semgrep":

        if "0 findings" in output:
            return "No se encontraron problemas mediante Semgrep."

        return "Revise los hallazgos reportados por Semgrep."

    if tool == "safety":

        if "0 vulnerabilities" in output.lower():
            return "No existen vulnerabilidades conocidas."

        return "Actualice las dependencias vulnerables."

    if tool == "pylint":

        return "Refactorice el código para aumentar el score."

    if tool == "playwright":

        return "Revise las pruebas funcionales fallidas."

    if tool == "locust":

        return "Revise tiempos de respuesta y errores."

    return ""


def extract_score(tool, output):

    if tool != "pylint":
        return None

    m = re.search(r"rated at ([0-9.]+)/10", output)

    if m:
        return float(m.group(1))

    return None


def extract_findings(tool, output):

    if tool == "bandit":

        m = re.search(r"Total issues.*?Low:\s*(\d+).*?Medium:\s*(\d+).*?High:\s*(\d+)", output, re.S)

        if m:
            return int(m.group(1)) + int(m.group(2)) + int(m.group(3))

    if tool == "semgrep":

        m = re.search(r"Findings:\s*(\d+)", output)

        if m:
            return int(m.group(1))

    if tool == "safety":

        m = re.search(r"(\d+) vulnerabilities found", output)

        if m:
            return int(m.group(1))

    return 0


@require_POST
def run_tool(request, tool):

    if tool not in TOOLS:

        return JsonResponse({

            "success": False,

            "message": "Herramienta no soportada"

        }, status=400)

    target_url = request.POST.get("target_url", "").strip()

    command = TOOLS[tool].copy()

    if tool == "locust" and target_url:

        command.extend(["--host", target_url])

    scan = SecurityScan.objects.create(

        tool=tool,

        target_url=target_url,

        user=request.user if request.user.is_authenticated else None,

        status="running",

    )

    start = time.time()

    try:

        process = subprocess.run(

            command,

            cwd=BASE_DIR,

            capture_output=True,

            text=True,

            timeout=600,

            shell=False,

        )

        output = (process.stdout or "") + "\n" + (process.stderr or "")

        return_code = process.returncode

        status = "success" if return_code == 0 else "warning"

    except subprocess.TimeoutExpired:

        output = "Tiempo máximo excedido."

        return_code = -1

        status = "error"

    except Exception as ex:

        output = str(ex)

        return_code = -1

        status = "error"

    duration = round(time.time() - start, 2)

    score = extract_score(tool, output)

    findings = extract_findings(tool, output)

    recommendation = build_recommendation(tool, output)

    scan.output = output

    scan.duration = duration

    scan.finished_at = timezone.now()

    scan.status = status

    scan.score = score

    scan.findings = findings

    scan.recommendations = recommendation

    scan.save()

    return JsonResponse({

        "success": True,

        "tool": tool,

        "status": status,

        "return_code": return_code,

        "duration": duration,

        "score": score,

        "findings": findings,

        "recommendation": recommendation,

        "output": output,

    })