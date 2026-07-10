import time

import requests


class ZAPService:
    """
    Servicio para ejecutar escaneos mediante
    OWASP ZAP API.
    """

    def __init__(self):

        self.base = "http://127.0.0.1:8090"

        self.api = self.base + "/JSON"

        self.key = ""

    def scan(self, target):

        start = time.time()

        try:

            ######################################################
            # 1. Spider
            ######################################################

            spider = requests.get(

                self.api + "/spider/action/scan/",

                params={

                    "url": target,

                    "apikey": self.key,

                },

                timeout=30,

            )

            spider_id = spider.json()["scan"]

            while True:

                status = requests.get(

                    self.api + "/spider/view/status/",

                    params={

                        "scanId": spider_id,

                        "apikey": self.key,

                    },

                    timeout=30,

                ).json()["status"]

                if int(status) >= 100:

                    break

                time.sleep(2)

            ######################################################
            # 2. Active Scan
            ######################################################

            active = requests.get(

                self.api + "/ascan/action/scan/",

                params={

                    "url": target,

                    "apikey": self.key,

                },

                timeout=30,

            )

            scan_id = active.json()["scan"]

            while True:

                status = requests.get(

                    self.api + "/ascan/view/status/",

                    params={

                        "scanId": scan_id,

                        "apikey": self.key,

                    },

                    timeout=30,

                ).json()["status"]

                if int(status) >= 100:

                    break

                time.sleep(5)

            ######################################################
            # 3. Alertas
            ######################################################

            alerts = requests.get(

                self.api + "/core/view/alerts/",

                params={

                    "baseurl": target,

                    "apikey": self.key,

                },

                timeout=30,

            ).json()["alerts"]

            return {

                "success": True,

                "duration": round(time.time() - start, 2),

                "findings": len(alerts),

                "alerts": alerts,

            }

        except Exception as ex:

            return {

                "success": False,

                "duration": round(time.time() - start, 2),

                "errors": str(ex),

            }

    def version(self):

        try:

            version = requests.get(

                self.api + "/core/view/version/",

                timeout=20,

            ).json()["version"]

            return version

        except Exception:

            return "OWASP ZAP no iniciado."