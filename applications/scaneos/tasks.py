"""
=========================================================
TASKS
Centro DevSecOps

Orquestador de tareas de escaneo.

Autor:
Especialización en Ciberseguridad
=========================================================
"""

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from .services.nmap_service import NmapService
from .services.nuclei_service import NucleiService
from .services.sqlmap_service import SQLMapService
from .services.sslyze_service import SSLyzeService
from .services.waf_service import WAFService
from .services.zap_service import ZapService

from .analyzers.risk_score import RiskScore


##########################################################################
# EJECUTAR UNA HERRAMIENTA
##########################################################################

def execute_tool(service, target):

    try:

        return service.scan(target)

    except Exception as ex:

        return {

            "tool": service.__class__.__name__,

            "status": "ERROR",

            "severity": "HIGH",

            "title": str(ex),

            "findings": []

        }


##########################################################################
# ESCANEO COMPLETO
##########################################################################

def run_full_scan(target):

    """
    Ejecuta todas las herramientas de manera paralela.
    """

    services = [

        NmapService(),

        NucleiService(),

        SQLMapService(),

        SSLyzeService(),

        WAFService(),

        ZapService(),

    ]

    results = []

    with ThreadPoolExecutor(max_workers=6) as executor:

        futures = [

            executor.submit(

                execute_tool,

                service,

                target

            )

            for service in services

        ]

        for future in as_completed(futures):

            results.append(

                future.result()

            )

    findings = []

    for result in results:

        severity = result.get(

            "severity",

            "INFO"

        )

        title = result.get(

            "title",

            result.get(

                "tool",

                "Resultado"

            )

        )

        findings.append(

            {

                "tool": result.get(

                    "tool"

                ),

                "severity": severity,

                "title": title,

            }

        )

    risk = RiskScore().calculate(

        findings

    )

    return {

        "target": target,

        "results": results,

        "risk": risk,

    }


##########################################################################
# ESCANEO RÁPIDO
##########################################################################

def run_quick_scan(target):

    """
    Escaneo liviano.
    """

    services = [

        NmapService(),

        WAFService(),

        SSLyzeService(),

    ]

    results = []

    for service in services:

        results.append(

            execute_tool(

                service,

                target

            )

        )

    findings = []

    for result in results:

        findings.append(

            {

                "tool": result.get(

                    "tool"

                ),

                "severity": result.get(

                    "severity",

                    "INFO"

                ),

                "title": result.get(

                    "title",

                    result.get(

                        "tool"

                    )

                ),

            }

        )

    risk = RiskScore().calculate(

        findings

    )

    return {

        "target": target,

        "results": results,

        "risk": risk,

    }


##########################################################################
# ESCANEO PERSONALIZADO
##########################################################################

def run_selected_scan(target, selected_services):

    """
    Ejecuta únicamente las herramientas seleccionadas.
    """

    available = {

        "nmap": NmapService,

        "nuclei": NucleiService,

        "sqlmap": SQLMapService,

        "sslyze": SSLyzeService,

        "waf": WAFService,

        "zap": ZapService,

    }

    results = []

    for name in selected_services:

        service_class = available.get(name)

        if service_class is None:

            continue

        service = service_class()

        results.append(

            execute_tool(

                service,

                target

            )

        )

    findings = []

    for result in results:

        findings.append(

            {

                "tool": result.get(

                    "tool"

                ),

                "severity": result.get(

                    "severity",

                    "INFO"

                ),

                "title": result.get(

                    "title",

                    result.get(

                        "tool"

                    )

                ),

            }

        )

    risk = RiskScore().calculate(

        findings

    )

    return {

        "target": target,

        "results": results,

        "risk": risk,

    }