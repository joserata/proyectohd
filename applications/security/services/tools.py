import sys
from django.conf import settings

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
        "auto",
        "applications",
    ],

    "safety": [
        PYTHON,
        "-m",
        "safety",
        "scan",
    ],

    "pip_audit": [
        PYTHON,
        "-m",
        "pip_audit",
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

    "detect_secrets": [
        PYTHON,
        "-m",
        "detect_secrets",
        "scan",
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

    "coverage": [
        PYTHON,
        "-m",
        "coverage",
        "run",
        "manage.py",
        "test",
    ],

    "pytest": [
        PYTHON,
        "-m",
        "pytest",
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

    "wapiti": [
        PYTHON,
        "-m",
        "wapiti",
    ],

}