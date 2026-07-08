import re


def extract_score(tool, output):

    if tool == "pylint":

        m = re.search(r"rated at ([0-9.]+)/10", output)

        if m:
            return float(m.group(1))

    return None


def extract_findings(tool, output):

    output = output.lower()

    if tool == "bandit":

        low = re.search(r"low:\s*(\d+)", output)
        medium = re.search(r"medium:\s*(\d+)", output)
        high = re.search(r"high:\s*(\d+)", output)

        return sum([
            int(low.group(1)) if low else 0,
            int(medium.group(1)) if medium else 0,
            int(high.group(1)) if high else 0
        ])

    elif tool == "semgrep":

        m = re.search(r"findings:\s*(\d+)", output)

        if m:
            return int(m.group(1))

    elif tool in ["safety", "pip_audit"]:

        m = re.search(r"(\d+)\s+vulnerab", output)

        if m:
            return int(m.group(1))

    elif tool == "flake8":

        return len(output.splitlines())

    elif tool == "pylint":

        return len(re.findall(r":[0-9]+:[0-9]+:", output))

    elif tool == "black":

        if "would reformat" in output:
            return output.count("would reformat")
        return 0

    elif tool == "mypy":

        m = re.search(r"Found (\d+) error", output)

        if m:
            return int(m.group(1))

    elif tool == "detect_secrets":

        return output.count("type")

    elif tool == "radon":

        return len(re.findall(r"[A-F] \(", output))

    elif tool == "xenon":

        return output.count("ERROR")

    elif tool == "coverage":

        m = re.search(r"TOTAL.*?(\d+)%", output)

        if m:
            return 100 - int(m.group(1))

    elif tool == "pytest":

        m = re.search(r"(\d+) failed", output)

        if m:
            return int(m.group(1))

    elif tool == "playwright":

        return output.lower().count("failed")

    elif tool == "locust":

        return output.lower().count("error")

    elif tool == "wapiti":

        return output.lower().count("vulnerability")

    return 0


def build_recommendation(tool, output):

    findings = extract_findings(tool, output)

    recommendations = {

        "bandit": (
            "No se encontraron vulnerabilidades críticas."
            if findings == 0
            else "Corregir funciones inseguras, eliminar eval(), revisar subprocess, credenciales y manejo de archivos."
        ),

        "semgrep": (
            "No se detectaron patrones inseguros."
            if findings == 0
            else "Corregir los patrones inseguros detectados por Semgrep."
        ),

        "safety": (
            "Las dependencias no presentan vulnerabilidades conocidas."
            if findings == 0
            else "Actualizar los paquetes vulnerables mediante pip."
        ),

        "pip_audit": (
            "No existen paquetes vulnerables."
            if findings == 0
            else "Actualizar inmediatamente las dependencias vulnerables."
        ),

        "pylint": (
            "El código presenta una buena calidad."
            if findings < 5
            else "Refactorizar módulos, mejorar nombres, documentación y estructura."
        ),

        "flake8": (
            "El código cumple el estándar PEP8."
            if findings == 0
            else "Corregir problemas de estilo y calidad detectados."
        ),

        "black": (
            "Todo el proyecto ya está correctamente formateado."
            if findings == 0
            else "Ejecutar Black para normalizar el formato."
        ),

        "mypy": (
            "No existen errores de tipado."
            if findings == 0
            else "Agregar anotaciones de tipos y corregir incompatibilidades."
        ),

        "detect_secrets": (
            "No se encontraron secretos expuestos."
            if findings == 0
            else "Eliminar credenciales, API Keys o Tokens encontrados."
        ),

        "radon": (
            "La complejidad ciclomática es adecuada."
            if findings < 10
            else "Reducir funciones complejas dividiendo responsabilidades."
        ),

        "xenon": (
            "La complejidad del proyecto es aceptable."
            if findings == 0
            else "Reducir la complejidad para cumplir los límites establecidos."
        ),

        "coverage": (
            "La cobertura de pruebas es adecuada."
            if findings < 20
            else "Incrementar las pruebas unitarias del proyecto."
        ),

        "pytest": (
            "Todas las pruebas pasaron."
            if findings == 0
            else "Corregir las pruebas que están fallando."
        ),

        "playwright": (
            "Las pruebas funcionales fueron exitosas."
            if findings == 0
            else "Corregir los errores encontrados en la interfaz web."
        ),

        "locust": (
            "El rendimiento es estable."
            if findings == 0
            else "Optimizar tiempos de respuesta, consultas SQL y uso de memoria."
        ),

        "pip_licenses": (
            "No se detectaron conflictos de licencias."
        ),

        "cyclonedx": (
            "SBOM generado correctamente."
        ),

        "wapiti": (
            "No se detectaron vulnerabilidades web."
            if findings == 0
            else "Corregir vulnerabilidades OWASP detectadas por Wapiti."
        ),

    }

    return recommendations.get(tool, "")