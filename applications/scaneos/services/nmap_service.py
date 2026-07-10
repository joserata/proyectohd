import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

from urllib.parse import urlparse


class NmapService:
    """
    Servicio para ejecutar escaneos con Nmap.
    """

    def __init__(self, target):

        self.target = self.normalize_target(target)

    def normalize_target(self, target):
        """
        Convierte una URL en host para Nmap.
        """

        if target.startswith("http://") or target.startswith("https://"):

            return urlparse(target).hostname

        return target

    def scan(self):
        """
        Ejecuta el escaneo.
        """

        if shutil.which("nmap") is None:

            return {

                "status": "error",

                "duration": 0,

                "score": 0,

                "findings": 0,

                "recommendation": "Nmap no está instalado.",

                "output": "No se encontró el ejecutable nmap.",

            }

        command = [

            "nmap",

            "-Pn",

            "-sV",

            "-O",

            "--top-ports",

            "100",

            "-oX",

            "-",

            self.target,

        ]

        start = time.time()

        try:

            process = subprocess.run(

                command,

                capture_output=True,

                text=True,

                timeout=600,

                shell=False,

            )

            duration = round(

                time.time() - start,

                2,

            )

            output = process.stdout

            findings = self.extract_findings(output)

            score = self.calculate_score(findings)

            recommendation = self.build_recommendation(findings)

            return {

                "status": "success"

                if process.returncode == 0

                else "warning",

                "duration": duration,

                "score": score,

                "findings": findings,

                "recommendation": recommendation,

                "output": output,

            }

        except subprocess.TimeoutExpired:

            return {

                "status": "error",

                "duration": 600,

                "score": 0,

                "findings": 0,

                "recommendation": "Tiempo máximo excedido.",

                "output": "",

            }

        except Exception as ex:

            return {

                "status": "error",

                "duration": 0,

                "score": 0,

                "findings": 0,

                "recommendation": str(ex),

                "output": "",

            }

    def extract_findings(self, xml_output):
        """
        Cuenta los puertos abiertos.
        """

        try:

            root = ET.fromstring(xml_output)

            ports = root.findall(".//port")

            abiertos = 0

            for port in ports:

                state = port.find("state")

                if state is not None:

                    if state.attrib.get("state") == "open":

                        abiertos += 1

            return abiertos

        except Exception:

            return 0

    def calculate_score(self, findings):
        """
        Calcula un score simple.
        """

        if findings == 0:

            return 100

        if findings <= 5:

            return 80

        if findings <= 15:

            return 60

        if findings <= 30:

            return 40

        return 20

    def build_recommendation(self, findings):
        """
        Genera recomendaciones.
        """

        if findings == 0:

            return "No se detectaron puertos abiertos."

        return (

            f"Se encontraron {findings} puertos abiertos. "

            "Revise los servicios expuestos y cierre aquellos "

            "que no sean necesarios."

        )