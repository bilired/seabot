import logging
import os
import sys

from django.apps import AppConfig


logger = logging.getLogger(__name__)


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'

    def ready(self) -> None:
        auto_start = os.getenv('SHIP_GATEWAY_AUTO_START', '1').lower() not in {'0', 'false', 'no'}
        if not auto_start:
            return

        argv = [arg.lower() for arg in sys.argv]
        skip_commands = {'makemigrations', 'migrate', 'collectstatic', 'shell', 'check', 'test'}
        if any(cmd in argv for cmd in skip_commands):
            return

        is_runserver = 'runserver' in argv
        if is_runserver and os.environ.get('RUN_MAIN') != 'true':
            return

        try:
            from .ship_gateway import gateway_service
            gateway_service.start()
            logger.info('Auto-started ship gateway on app ready')
        except Exception as exc:
            logger.warning('Auto-start ship gateway failed: %s', exc)
