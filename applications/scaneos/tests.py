from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .analyzers.risk_score import RiskScore
from .analyzers.severity import Severity
from .tasks import run_quick_scan


###############################################################
# RISK SCORE
###############################################################

class RiskScoreTest(TestCase):

    def test_risk_score(self):

        findings = [

            {
                "tool": "zap",
                "severity": "HIGH",
                "title": "SQL Injection"
            },

            {
                "tool": "nmap",
                "severity": "LOW",
                "title": "Puerto abierto"
            }

        ]

        result = RiskScore().calculate(findings)

        self.assertIn("risk_score", result)

        self.assertIn("risk_level", result)

        self.assertGreater(result["risk_score"], 0)


###############################################################
# SEVERITY
###############################################################

class SeverityTest(TestCase):

    def test_normalize_high(self):

        self.assertEqual(

            Severity.normalize("high"),

            "HIGH"

        )

    def test_normalize_info(self):

        self.assertEqual(

            Severity.normalize("informational"),

            "INFO"

        )

    def test_weight(self):

        self.assertEqual(

            Severity.weight("HIGH"),

            8

        )


###############################################################
# DASHBOARD
###############################################################

class DashboardViewTest(TestCase):

    def test_dashboard(self):

        response = self.client.get(

            reverse("scaneos:dashboard")

        )

        self.assertEqual(

            response.status_code,

            200

        )


###############################################################
# QUICK SCAN
###############################################################

class QuickScanTest(TestCase):

    @patch("applications.scaneos.services.nmap_service.NmapService.scan")
    @patch("applications.scaneos.services.waf_service.WAFService.scan")
    @patch("applications.scaneos.services.sslyze_service.SSLyzeService.scan")

    def test_quick_scan(

        self,

        ssl_mock,

        waf_mock,

        nmap_mock,

    ):

        nmap_mock.return_value = {

            "tool": "nmap",

            "severity": "LOW",

            "title": "Nmap OK"

        }

        waf_mock.return_value = {

            "tool": "waf",

            "severity": "INFO",

            "title": "No WAF"

        }

        ssl_mock.return_value = {

            "tool": "sslyze",

            "severity": "LOW",

            "title": "TLS Correcto"

        }

        result = run_quick_scan(

            "http://127.0.0.1:8000"

        )

        self.assertIn(

            "risk",

            result

        )

        self.assertEqual(

            len(result["results"]),

            3

        )


###############################################################
# VISTA DE ESCANEO
###############################################################

class ScanViewTest(TestCase):

    @patch("applications.scaneos.tasks.run_quick_scan")

    def test_scan_view(

        self,

        quick_mock

    ):

        quick_mock.return_value = {

            "target": "http://127.0.0.1:8000",

            "risk": {

                "risk_level": "LOW",

                "risk_score": 10

            },

            "results": []

        }

        response = self.client.post(

            reverse("scaneos:start_scan"),

            {

                "target": "http://127.0.0.1:8000",

                "scan_type": "quick"

            }

        )

        self.assertEqual(

            response.status_code,

            200

        )