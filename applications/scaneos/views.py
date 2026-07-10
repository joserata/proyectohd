from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import ScanExecution
from .models import ScanTarget

from .services.scanner import Scanner


AVAILABLE_TOOLS = [

    "nmap",
    "nuclei",
    "zap",
    "sqlmap",
    "sslyze",
    "waf",
    "wapiti",

]


def dashboard(request):
    """
    Dashboard principal del Centro de Escaneo.
    """

    targets = ScanTarget.objects.all().order_by("-id")

    executions = ScanExecution.objects.order_by(
        "-started_at"
    )[:20]

    return render(

        request,

        "scaneos/dashboard.html",

        {

            "targets": targets,

            "executions": executions,

            "tools": AVAILABLE_TOOLS,

        }

    )


def history(request):
    """
    Historial de escaneos.
    """

    scans = ScanExecution.objects.order_by(
        "-started_at"
    )

    return render(

        request,

        "scaneos/history.html",

        {

            "scans": scans,

        }

    )


def detail(request, pk):
    """
    Detalle de un escaneo.
    """

    scan = get_object_or_404(

        ScanExecution,

        pk=pk,

    )

    return render(

        request,

        "scaneos/detail.html",

        {

            "scan": scan,

        }

    )


@require_POST
def run_scan(request):
    """
    Ejecuta uno o varios escaneos.
    """

    target = request.POST.get(
        "target",
        ""
    ).strip()

    selected_tools = request.POST.getlist(
        "tools"
    )

    if not target:

        return JsonResponse(

            {

                "success": False,

                "message": "Debe indicar una URL o dirección IP.",

            },

            status=400,

        )

    scan_target, created = ScanTarget.objects.get_or_create(

        target=target

    )

    scanner = Scanner()

    if selected_tools:

        results = scanner.run_selected(

            target,

            selected_tools,

        )

    else:

        results = scanner.run_all(

            target

        )

    for result in results:

        ScanExecution.objects.create(

            target=scan_target,

            tool=result.get("tool"),

            status=result.get("status", "error"),

            score=result.get("score", 0),

            findings=result.get("findings", 0),

            recommendation=result.get(

                "recommendation",

                ""

            ),

            output=result.get(

                "output",

                ""

            ),

            duration=result.get(

                "duration",

                0

            ),

            started_at=timezone.now(),

            finished_at=timezone.now(),

        )

    return JsonResponse(

        {

            "success": True,

            "results": results,

        }

    )


def available_tools(request):
    """
    Devuelve las herramientas disponibles.
    """

    scanner = Scanner()

    return JsonResponse(

        {

            "tools": scanner.available_tools(),

        }

    )