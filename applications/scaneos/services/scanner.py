from concurrent.futures import ThreadPoolExecutor, as_completed

from .nmap_service import NmapService
from .nuclei_service import NucleiService


class Scanner:

    def run_tool(self, tool_name, target):

        if tool_name == "nmap":

            return NmapService(target).scan()

        elif tool_name == "nuclei":

            return NucleiService(target).scan()

        else:

            return {

                "success": False,

                "tool": tool_name,

                "message": "Herramienta no soportada.",

            }

    def run_selected(self, target, tools):

        return [

            self.run_tool(tool, target)

            for tool in tools

        ]

    def run_all(self, target):

        return [

            self.run_tool(tool, target)

            for tool in [

                "nmap",

                "nuclei",

            ]

        ]

    def run_parallel(self, target):

        results = []

        tools = [

            "nmap",

            "nuclei",

        ]

        with ThreadPoolExecutor(max_workers=5) as executor:

            futures = {

                executor.submit(

                    self.run_tool,

                    tool,

                    target

                ): tool

                for tool in tools

            }

            for future in as_completed(futures):

                results.append(

                    future.result()

                )

        return results

    def available_tools(self):

        return [

            "nmap",

            "nuclei",

        ]