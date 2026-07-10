import subprocess
import time

from django.conf import settings


BASE_DIR = settings.BASE_DIR


class WAFService:
    """
    Servicio encargado de detectar
    Web Application Firewalls (WAF).

    Utiliza WAFW00F.
    """

    def __init__(self):

        self.binary = "wafw00f"

    def scan(self, target):
        """
        Detecta el WAF presente en una aplicación web.

        Parameters
        ----------
        target : str
            URL objetivo.
        """

        command = [

            self.binary,

            target,

            "-a",

        ]

        start = time.time()

        try:

            process = subprocess.run(

                command,

                cwd=BASE_DIR,

                capture_output=True,

                text=True,

                timeout=900,

                shell=False,

            )

            output = process.stdout

            errors = process.stderr

            waf = self.extract_waf(output)

            return {

                "success": process.returncode == 0,

                "return_code": process.returncode,

                "duration": round(time.time() - start, 2),

                "output": output,

                "errors": errors,

                "command": " ".join(command),

                "waf_detected": waf,

            }

        except subprocess.TimeoutExpired:

            return {

                "success": False,

                "return_code": -1,

                "duration": round(time.time() - start, 2),

                "output": "",

                "errors": "Tiempo máximo excedido.",

                "command": " ".join(command),

                "waf_detected": None,

            }

        except Exception as ex:

            return {

                "success": False,

                "return_code": -1,

                "duration": round(time.time() - start, 2),

                "output": "",

                "errors": str(ex),

                "command": " ".join(command),

                "waf_detected": None,

            }

    def extract_waf(self, output):
        """
        Extrae el nombre del WAF detectado.
        """

        for line in output.splitlines():

            line = line.strip()

            if "is behind" in line:

                return line

            if "The site" in line:

                return line

            if "Firewall" in line:

                return line

        return "No detectado"

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

            return "WAFW00F no instalado."