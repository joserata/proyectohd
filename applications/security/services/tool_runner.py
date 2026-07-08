import subprocess
import time

from django.utils import timezone

from .tools import BASE_DIR


def execute(command):

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

        output = (process.stdout or "") + "\n" + (process.stderr or "")

        status = "success" if process.returncode == 0 else "warning"

        return_code = process.returncode

    except subprocess.TimeoutExpired:

        output = "Tiempo máximo excedido."

        status = "error"

        return_code = -1

    except Exception as ex:

        output = str(ex)

        status = "error"

        return_code = -1

    duration = round(time.time() - start, 2)

    return {

        "status": status,

        "output": output,

        "duration": duration,

        "return_code": return_code,

        "finished_at": timezone.now(),

    }