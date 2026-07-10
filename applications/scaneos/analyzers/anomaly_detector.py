from collections import Counter
from statistics import mean


class AnomalyDetector:
    """
    Detector de anomalías para el Centro DevSecOps.

    Analiza los resultados obtenidos por las
    diferentes herramientas y determina si
    existen comportamientos fuera de lo normal.
    """

    def analyze(self, results):

        analysis = {

            "status": "normal",

            "score": 0,

            "anomalies": [],

            "summary": {}

        }

        if not results:

            analysis["status"] = "error"

            analysis["anomalies"].append(

                "No existen resultados para analizar."

            )

            return analysis

        durations = []

        findings = []

        failed_tools = []

        critical_tools = []

        for result in results:

            duration = result.get("duration", 0)

            durations.append(duration)

            findings.append(

                result.get("findings", 0)

            )

            if not result.get("success", False):

                failed_tools.append(

                    result.get("tool", "desconocido")

                )

            if result.get("severity") == "critical":

                critical_tools.append(

                    result.get("tool")

                )

        ####################################################
        # Herramientas fallidas
        ####################################################

        if failed_tools:

            analysis["anomalies"].append(

                {

                    "type": "tool_failure",

                    "count": len(failed_tools),

                    "tools": failed_tools

                }

            )

        ####################################################
        # Duraciones anormales
        ####################################################

        avg_duration = mean(durations)

        slow = [

            d

            for d in durations

            if d > avg_duration * 2

        ]

        if slow:

            analysis["anomalies"].append(

                {

                    "type": "slow_scan",

                    "average": round(avg_duration, 2),

                    "detected": len(slow)

                }

            )

        ####################################################
        # Muchas vulnerabilidades
        ####################################################

        total_findings = sum(findings)

        if total_findings > 50:

            analysis["anomalies"].append(

                {

                    "type": "high_findings",

                    "value": total_findings

                }

            )

        ####################################################
        # Vulnerabilidades críticas
        ####################################################

        if critical_tools:

            analysis["anomalies"].append(

                {

                    "type": "critical",

                    "tools": critical_tools

                }

            )

        ####################################################
        # Calificación
        ####################################################

        score = 100

        score -= len(failed_tools) * 10

        score -= len(slow) * 5

        score -= total_findings

        if score < 0:

            score = 0

        analysis["score"] = score

        if score >= 90:

            analysis["status"] = "excellent"

        elif score >= 70:

            analysis["status"] = "good"

        elif score >= 50:

            analysis["status"] = "warning"

        else:

            analysis["status"] = "critical"

        ####################################################
        # Resumen
        ####################################################

        analysis["summary"] = {

            "tools": len(results),

            "average_duration": round(

                avg_duration,

                2

            ),

            "total_findings": total_findings,

            "failed_tools": len(

                failed_tools

            ),

            "critical_tools": len(

                critical_tools

            ),

            "distribution":

                Counter(

                    [

                        r.get(

                            "tool",

                            "unknown"

                        )

                        for r in results

                    ]

                )

        }

        return analysis