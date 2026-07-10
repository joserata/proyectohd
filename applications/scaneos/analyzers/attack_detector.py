"""
applications/scaneos/analyzers/attack_detector.py

Detecta posibles ataques sobre la aplicación
correlacionando los resultados obtenidos por
los diferentes motores de escaneo.
"""

from collections import Counter


class AttackDetector:

    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self):
        """
        Reglas simples de correlación.
        Posteriormente pueden almacenarse
        en base de datos.
        """
        return {

            "sql_injection": [
                "sql injection",
                "union select",
                "mysql",
                "postgres",
                "syntax error",
                "database error",
            ],

            "xss": [
                "cross site scripting",
                "xss",
                "<script>",
                "javascript:",
            ],

            "csrf": [
                "csrf",
                "cross site request forgery",
            ],

            "directory_traversal": [
                "../",
                "..\\",
                "directory traversal",
                "path traversal",
            ],

            "file_upload": [
                "unsafe upload",
                "file upload",
                "arbitrary upload",
            ],

            "rce": [
                "remote code execution",
                "command injection",
                "os command",
                "shell",
            ],

            "lfi": [
                "local file inclusion",
                "lfi",
            ],

            "rfi": [
                "remote file inclusion",
                "rfi",
            ],

            "xxe": [
                "xml external entity",
                "xxe",
            ],

            "idor": [
                "idor",
                "insecure direct object reference",
            ],

            "open_redirect": [
                "open redirect",
                "redirect",
            ],

            "ssrf": [
                "ssrf",
                "server side request forgery",
            ],

            "weak_tls": [
                "tls 1.0",
                "tls 1.1",
                "weak cipher",
                "obsolete protocol",
            ],

            "security_headers": [
                "missing csp",
                "missing x-frame-options",
                "missing x-content-type-options",
                "missing hsts",
            ],

        }

    def analyze(self, findings):
        """
        findings puede ser una lista de textos
        provenientes de ZAP, Nuclei, Wapiti,
        Nmap, etc.
        """

        attacks = []

        for finding in findings:

            text = str(finding).lower()

            for attack, keywords in self.rules.items():

                if any(word in text for word in keywords):

                    attacks.append(attack)

        counter = Counter(attacks)

        results = []

        for attack, total in counter.items():

            results.append({

                "attack": attack,

                "occurrences": total,

                "risk": self.calculate_risk(total),

            })

        return sorted(
            results,
            key=lambda x: x["occurrences"],
            reverse=True,
        )

    def calculate_risk(self, occurrences):

        if occurrences >= 10:
            return "CRITICAL"

        if occurrences >= 6:
            return "HIGH"

        if occurrences >= 3:
            return "MEDIUM"

        return "LOW"

    def summary(self, findings):

        attacks = self.analyze(findings)

        return {

            "total_findings": len(findings),

            "total_attack_types": len(attacks),

            "critical": sum(
                1 for a in attacks
                if a["risk"] == "CRITICAL"
            ),

            "high": sum(
                1 for a in attacks
                if a["risk"] == "HIGH"
            ),

            "medium": sum(
                1 for a in attacks
                if a["risk"] == "MEDIUM"
            ),

            "low": sum(
                1 for a in attacks
                if a["risk"] == "LOW"
            ),

            "attacks": attacks,

        }