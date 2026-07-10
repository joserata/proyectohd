import subprocess
import time

from django.conf import settings


BASE_DIR = settings.BASE_DIR


class NucleiService:
    """
    Servicio encargado de ejecutar Nuclei.

    https://github.com/projectdiscovery/nuclei
    """

    def __init__(self):

        self.binary = "nuclei"

    def scan(
        self,
        target,
        severity=None,
        templates=None,
    ):
        """
        Ejecuta un escaneo sobre un objetivo.

        Parameters
        ----------
        target : str
            URL o IP objetivo.

        severity : str
            low,medium,high,critical

        templates : str
            Ruta de templates personalizada.
        """

        command = [

            self.binary,

            "-u",

            target,

            "-silent",

            "-stats",

            "-json",

        ]

        if severity:

            command.extend([

                "-severity",

                severity,

            ])

        if templates:

            command.extend([

                "-t",

                templates,

            ])

        start = time.time()

        try:

            process = subprocess.run(

                command,

                cwd=BASE_DIR,

                capture_output=True,

                text=True,

                timeout=1800,

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

                    "-version",

                ],

                capture_output=True,

                text=True,

            )

            return process.stdout.strip()

        except Exception:

            return "Nuclei no instalado."