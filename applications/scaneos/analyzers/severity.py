"""
=========================================================
SEVERITY NORMALIZER
Especialización en Ciberseguridad

Normaliza la severidad proveniente de distintas
herramientas de seguridad.
=========================================================
"""


class Severity:

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"
    UNKNOWN = "UNKNOWN"

    ##############################################################
    # MAPEO GENERAL
    ##############################################################

    MAP = {

        # ZAP
        "critical": CRITICAL,
        "high": HIGH,
        "medium": MEDIUM,
        "low": LOW,
        "informational": INFO,
        "info": INFO,

        # NUCLEI
        "critical severity": CRITICAL,

        # WAPITI
        "1": CRITICAL,
        "2": HIGH,
        "3": MEDIUM,
        "4": LOW,

        # SQLMAP
        "injectable": CRITICAL,
        "possible": MEDIUM,
        "warning": LOW,

        # SSLYZE
        "secure": INFO,
        "insecure": HIGH,
        "weak": MEDIUM,

        # NMAP
        "open": LOW,
        "filtered": INFO,
        "closed": INFO,
        "vulnerable": HIGH,

    }

    ##############################################################
    # NORMALIZAR
    ##############################################################

    @classmethod
    def normalize(cls, value):

        if value is None:

            return cls.UNKNOWN

        value = str(value).strip().lower()

        return cls.MAP.get(

            value,

            cls.UNKNOWN

        )

    ##############################################################
    # PESO
    ##############################################################

    @classmethod
    def weight(cls, severity):

        severity = severity.upper()

        weights = {

            cls.CRITICAL: 10,

            cls.HIGH: 8,

            cls.MEDIUM: 5,

            cls.LOW: 2,

            cls.INFO: 1,

            cls.UNKNOWN: 0,

        }

        return weights.get(

            severity,

            0

        )

    ##############################################################
    # COLOR PARA DASHBOARD
    ##############################################################

    @classmethod
    def color(cls, severity):

        severity = severity.upper()

        colors = {

            cls.CRITICAL: "#7f0000",

            cls.HIGH: "#d32f2f",

            cls.MEDIUM: "#f57c00",

            cls.LOW: "#fbc02d",

            cls.INFO: "#1976d2",

            cls.UNKNOWN: "#757575",

        }

        return colors.get(

            severity,

            "#757575"

        )

    ##############################################################
    # ICONO
    ##############################################################

    @classmethod
    def icon(cls, severity):

        severity = severity.upper()

        icons = {

            cls.CRITICAL: "bi bi-radioactive",

            cls.HIGH: "bi bi-exclamation-octagon-fill",

            cls.MEDIUM: "bi bi-exclamation-triangle-fill",

            cls.LOW: "bi bi-info-circle-fill",

            cls.INFO: "bi bi-shield-check",

            cls.UNKNOWN: "bi bi-question-circle",

        }

        return icons.get(

            severity,

            "bi bi-question-circle"

        )

    ##############################################################
    # PRIORIDAD
    ##############################################################

    @classmethod
    def priority(cls, severity):

        severity = severity.upper()

        priorities = {

            cls.CRITICAL: 1,

            cls.HIGH: 2,

            cls.MEDIUM: 3,

            cls.LOW: 4,

            cls.INFO: 5,

            cls.UNKNOWN: 6,

        }

        return priorities.get(

            severity,

            6

        )

    ##############################################################
    # COMPARAR DOS SEVERIDADES
    ##############################################################

    @classmethod
    def highest(cls, first, second):

        p1 = cls.priority(first)

        p2 = cls.priority(second)

        return first if p1 < p2 else second