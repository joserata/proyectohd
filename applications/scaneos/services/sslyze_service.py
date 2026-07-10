import subprocess
import time
from urllib.parse import urlparse

from django.conf import settings


BASE_DIR = settings.BASE_DIR


class SSLyzeService:
    """
    Servicio encargado de ejecutar SSLyze.

    https://github.com/nabla-c0d3/sslyze
    """

    def __init__(self):

        self.binary = "sslyze"

    def scan(self, target):
        """
        Analiza la configuración SSL/TLS de un servidor.

        Parameters
        ----------
        target : str
            URL o dominio objetivo.
        """

        parsed = urlparse(target)

        host = parsed.hostname

        port = parsed.port or 443

        if host is None:

            return {

                "success": False,

                "return_code": -1,

                "duration": 0,

                "output": "",

                "errors": "URL inválida.",

                "command": "",

            }

        command = [

            self.binary,

            f"{host}:{port}",

        ]

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

                    "--version",

                ],

                capture_output=True,

                text=True,

            )

            return process.stdout.strip()

        except Exception:

            return "SSLyze no instalado."