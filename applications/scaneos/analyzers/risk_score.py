"""
=========================================================
RISK SCORE ENGINE
Especialización en Ciberseguridad

Calcula el riesgo general del activo a partir de
todos los hallazgos encontrados durante el escaneo.
=========================================================
"""

from collections import Counter


class RiskScore:

    ###########################################################
    # PUNTAJE BASE POR SEVERIDAD
    ###########################################################

    WEIGHTS = {

        "CRITICAL": 40,
        "HIGH": 25,
        "MEDIUM": 15,
        "LOW": 5,
        "INFO": 1,

    }

    ###########################################################
    # CALCULAR RIESGO
    ###########################################################

    def calculate(self, findings):

        """
        findings:

        [

            {
                "tool":"zap",
                "severity":"HIGH",
                "title":"SQL Injection"
            },

            {
                "tool":"nuclei",
                "severity":"MEDIUM",
                "title":"Directory Listing"
            }

        ]
        """

        score = 0

        severities = Counter()

        tools = Counter()

        details = []

        for item in findings:

            severity = item.get(

                "severity",

                "INFO"

            ).upper()

            tool = item.get(

                "tool",

                "unknown"

            )

            title = item.get(

                "title",

                ""

            )

            weight = self.WEIGHTS.get(

                severity,

                0

            )

            score += weight

            severities[severity] += 1

            tools[tool] += 1

            details.append(

                {

                    "tool": tool,

                    "severity": severity,

                    "title": title,

                    "weight": weight,

                }

            )

        score = min(score, 100)

        return {

            "risk_score": score,

            "risk_level": self.level(score),

            "summary": dict(severities),

            "tools": dict(tools),

            "details": details,

            "recommendation": self.recommend(score),

        }

    ###########################################################
    # NIVEL
    ###########################################################

    def level(self, score):

        if score >= 90:

            return "CRITICAL"

        if score >= 70:

            return "HIGH"

        if score >= 40:

            return "MEDIUM"

        if score >= 15:

            return "LOW"

        return "INFO"

    ###########################################################
    # RECOMENDACIONES
    ###########################################################

    def recommend(self, score):

        if score >= 90:

            return (

                "El activo presenta vulnerabilidades críticas. "

                "Se recomienda aislar el sistema, aplicar "

                "parches inmediatamente y realizar un análisis "

                "forense."

            )

        if score >= 70:

            return (

                "Se identificaron vulnerabilidades de alto riesgo. "

                "Corregir antes de poner el sistema en producción."

            )

        if score >= 40:

            return (

                "Existen vulnerabilidades de riesgo medio. "

                "Programar actividades de remediación."

            )

        if score >= 15:

            return (

                "Se detectaron configuraciones inseguras "

                "que deben corregirse."

            )

        return (

            "No se encontraron vulnerabilidades relevantes."

        )