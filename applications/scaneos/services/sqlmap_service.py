import subprocess
import time

from django.conf import settings


BASE_DIR = settings.BASE_DIR


class SqlmapService:
    """
    Servicio encargado de ejecutar SQLMap.

    https://sqlmap.org
    """

    def __init__(self):

        self.binary = "sqlmap"

    def scan(
        self,
        target,
        crawl=2,
        level=1,
        risk=1,
    ):
        """
        Ejecuta un análisis SQL Injection.

        Parameters
        ----------
        target : str
            URL objetivo.

        crawl : int
            Profundidad de rastreo.

        level : int
            Nivel de pruebas (1-5).

        risk : int
            Nivel de riesgo (1-3).
        """

        command = [

            self.binary,

            "-u",

            target,

            "--batch",

            "--random-agent",

            "--crawl",

            str(crawl),

            "--level",

            str(level),

            "--risk",

            str(risk),

            "--answers",

            "follow=Y",

            "--flush-session",

        ]

        start = time.time()

        try:

            process = subprocess.run(

                command,

                cwd=BASE_DIR,

                capture_output=True,

                text=True,

                timeout=3600,

                shell=False,

            )

            return {

                "success": process.returncode == 0,

                "return_code": process.returncode,

                "duration": round(time.time() - start, 2),

                "output": process.stdout,

                "errors": process.stderr,

                "command": " ".join(command),

            }

        except subprocess.TimeoutExpired:

            return {

                "success": False,

                "return_code": -1,

                "duration": round(time.time() - start, 2),

                "output": "",

                "errors": "Tiempo máximo excedido.",

                "command": " ".join(command),

            }

        except Exception as ex:

            return {

                "success": False,

                "return_code": -1,

                "duration": round(time.time() - start, 2),

                "output": "",

                "errors": str(ex),

                "command": " ".join(command),

            }

    def version(self):

        try:

            process = subprocess.run(

                [

                    self.binary,

                    "--version",

                ],

                capture_output=True,

                text=True,

            )

            return process.stdout.strip()

        except Exception:

            return "SQLMap no instalado."