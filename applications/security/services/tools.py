import shutil
import sys
from django.conf import settings

PYTHON = sys.executable
BASE_DIR = settings.BASE_DIR

WAPITI = shutil.which("wapiti")

def get_command(tool, target_url=None):
    """
    Devuelve el comando que debe ejecutar cada herramienta.
    Retorna None cuando la herramienta requiere una URL y ésta no fue enviada.
    """

    commands = {

        # ==========================
        # SAST
        # ==========================

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
            "auto",
            "applications",
        ],

        "pylint": [
            PYTHON,
            "-m",
            "pylint",
            "--recursive=y",
            "applications",
        ],

        "flake8": [
            PYTHON,
            "-m",
            "flake8",
            "applications",
        ],

        "black": [
            PYTHON,
            "-m",
            "black",
            "--check",
            "applications",
        ],

        "mypy": [
            PYTHON,
            "-m",
            "mypy",
            "applications",
        ],

        "radon": [
            PYTHON,
            "-m",
            "radon",
            "cc",
            "applications",
            "-s",
            "-a",
        ],

        "xenon": [
            PYTHON,
            "-m",
            "xenon",
            "applications",
        ],

        "detect_secrets": [
            PYTHON,
            "-m",
            "detect_secrets",
            "scan",
            "applications",
        ],

        # ==========================
        # DEPENDENCIAS
        # ==========================

        "pip_audit": [
            PYTHON,
            "-m",
            "pip_audit",
        ],

        "safety": [
            PYTHON,
            "-m",
            "safety",
            "scan",
        ],

        "pip_licenses": [
            PYTHON,
            "-m",
            "piplicenses",
        ],

        "cyclonedx": [
            PYTHON,
            "-m",
            "cyclonedx_py",
            "environment",
        ],

        # ==========================
        # TESTING
        # ==========================

        "pytest": [
            PYTHON,
            "-m",
            "pytest",
        ],

        "coverage": [
            PYTHON,
            "-m",
            "coverage",
            "run",
            "manage.py",
            "test",
        ],
    }

    # Herramientas que NO necesitan URL
    if tool in commands:
        return commands[tool]

    # A partir de aquí todas requieren URL
    if not target_url:
        return None

    # ==========================
    # DAST
    # ==========================

    if tool == "wapiti":

        # ``None`` termina provocando un TypeError en subprocess. Devuelve
        # None para que la vista pueda informar claramente que falta Wapiti.
        if not WAPITI:
            return None

        return [

        WAPITI,

        "-u",

        target_url,

        "--flush-session",

    ]

    if tool == "locust":
        return [
            PYTHON,
            "-m",
            "locust",
            "-f",
            "locustfile.py",
            "--host",
            target_url,
            "--headless",
            "-u",
            "10",
            "-r",
            "2",
            "-t",
            "20s",
        ]

    if tool == "playwright":
        return [
            PYTHON,
            "tests/e2e/playwright_smoke.py",
            target_url,
        ]

    # Herramienta no soportada
    return None
