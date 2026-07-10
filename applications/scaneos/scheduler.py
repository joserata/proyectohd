"""
scheduler.py

Programador de tareas del módulo Scaneos.

Permite ejecutar escaneos automáticos sobre los objetivos
registrados utilizando APScheduler.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from django.utils import timezone

from .models import ScanTarget

from .services.scanner import execute_scan


logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def scheduled_scan():
    """
    Ejecuta un escaneo sobre todos los objetivos activos.
    """

    logger.info("Iniciando escaneo automático...")

    targets = ScanTarget.objects.filter(

        active=True

    )

    for target in targets:

        logger.info(

            "Escaneando %s",

            target.url

        )

        try:

            execute_scan(

                tool="zap",

                target_url=target.url

            )

        except Exception as ex:

            logger.exception(

                "Error escaneando %s",

                target.url

            )

    logger.info(

        "Escaneo finalizado %s",

        timezone.now()

    )


def start_scheduler():
    """
    Inicia el scheduler únicamente una vez.
    """

    if scheduler.running:

        return

    scheduler.add_job(

        scheduled_scan,

        trigger="interval",

        minutes=30,

        id="automatic_scan",

        replace_existing=True,

    )

    scheduler.start()

    logger.info("Scheduler iniciado correctamente.")