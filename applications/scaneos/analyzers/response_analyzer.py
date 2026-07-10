"""
=========================================================
RESPONSE ANALYZER
Especialización en Ciberseguridad
Autor: José Caballero

Analiza respuestas HTTP y genera indicadores
de riesgo para el motor de correlación.
=========================================================
"""

import re


class ResponseAnalyzer:

    def __init__(self):

        self.score = 0
        self.findings = []
        self.level = "LOW"

    ###########################################################
    # ANALIZAR RESPUESTA
    ###########################################################

    def analyze(self, response):

        if response is None:

            self.findings.append(
                "No se obtuvo respuesta del servidor."
            )

            self.score += 50

            self.calculate_level()

            return self.build()

        self.check_status(response)
        self.check_headers(response)
        self.check_server(response)
        self.check_body(response)
        self.check_security_headers(response)

        self.calculate_level()

        return self.build()

    ###########################################################
    # STATUS HTTP
    ###########################################################

    def check_status(self, response):

        code = response.status_code

        if code >= 500:

            self.findings.append(
                f"Servidor respondió con error {code}"
            )

            self.score += 25

        elif code == 403:

            self.findings.append(
                "Acceso restringido (403)"
            )

        elif code == 401:

            self.findings.append(
                "Autenticación requerida."
            )

        elif code == 404:

            self.findings.append(
                "Recurso inexistente."
            )

    ###########################################################
    # HEADERS
    ###########################################################

    def check_headers(self, response):

        headers = response.headers

        if "Server" in headers:

            self.findings.append(
                f"Servidor identificado: {headers['Server']}"
            )

        if "X-Powered-By" in headers:

            self.findings.append(
                "Header X-Powered-By expuesto."
            )

            self.score += 5

    ###########################################################
    # CABECERAS DE SEGURIDAD
    ###########################################################

    def check_security_headers(self, response):

        headers = response.headers

        required = {

            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Referrer-Policy",
            "Permissions-Policy"

        }

        for header in required:

            if header not in headers:

                self.findings.append(
                    f"Falta cabecera de seguridad: {header}"
                )

                self.score += 4

    ###########################################################
    # SERVIDOR
    ###########################################################

    def check_server(self, response):

        server = response.headers.get("Server", "")

        if not server:

            return

        server = server.lower()

        weak = [

            "apache/2.2",
            "apache/2.4.1",
            "iis/6",
            "iis/7",
            "nginx/1.10",
            "nginx/1.12"

        ]

        for item in weak:

            if item in server:

                self.findings.append(
                    "Versión antigua del servidor detectada."
                )

                self.score += 15

    ###########################################################
    # CUERPO HTML
    ###########################################################

    def check_body(self, response):

        body = response.text.lower()

        patterns = [

            r"sql syntax",
            r"mysql_fetch",
            r"traceback",
            r"exception",
            r"stack trace",
            r"fatal error",
            r"warning:",
            r"undefined index",
            r"notice:",
            r"ora-",
            r"postgresql",
            r"sqlite"

        ]

        for pattern in patterns:

            if re.search(pattern, body):

                self.findings.append(
                    f"Posible fuga de información ({pattern})"
                )

                self.score += 10

    ###########################################################
    # NIVEL DE RIESGO
    ###########################################################

    def calculate_level(self):

        if self.score >= 80:

            self.level = "CRITICAL"

        elif self.score >= 60:

            self.level = "HIGH"

        elif self.score >= 30:

            self.level = "MEDIUM"

        else:

            self.level = "LOW"

    ###########################################################
    # RESULTADO
    ###########################################################

    def build(self):

        return {

            "risk_level": self.level,

            "risk_score": self.score,

            "findings": self.findings,

            "total_findings": len(self.findings)

        }