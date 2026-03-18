import logging
import os
import sys

from django.apps import AppConfig


logger = logging.getLogger(__name__)


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'

    def ready(self) -> None:
        argv = [arg.lower() for arg in sys.argv]
        skip_commands = {'makemigrations', 'migrate', 'collectstatic', 'shell', 'check', 'test'}
        if any(cmd in argv for cmd in skip_commands):
            return

        is_runserver = 'runserver' in argv
        is_gunicorn = 'gunicorn' in argv
        if not is_runserver and not is_gunicorn:
            return

        if is_runserver and os.environ.get('RUN_MAIN') != 'true':
            return

        ship_gateway_auto_start = os.getenv('SHIP_GATEWAY_AUTO_START', '1').lower() not in {'0', 'false', 'no'}
        ship_gateway_allow_gunicorn = os.getenv('SHIP_GATEWAY_ALLOW_GUNICORN_AUTOSTART', '0').lower() in {'1', 'true', 'yes'}
        if ship_gateway_auto_start and (not is_gunicorn or ship_gateway_allow_gunicorn):
            try:
                from .ship_gateway import gateway_service
                gateway_service.start()
                logger.info('Auto-started ship gateway on app ready')
            except Exception as exc:
                logger.warning('Auto-start ship gateway failed: %s', exc)

        video_monitor_auto_start = os.getenv('VIDEO_STREAM_MONITOR_AUTO_START', '1').lower() not in {'0', 'false', 'no'}
        video_monitor_allow_gunicorn = os.getenv('VIDEO_STREAM_MONITOR_ALLOW_GUNICORN_AUTOSTART', '0').lower() in {'1', 'true', 'yes'}
        if video_monitor_auto_start and (not is_gunicorn or video_monitor_allow_gunicorn):
            try:
                from .video_stream_monitor import video_stream_monitor_service
                video_stream_monitor_service.start()
                logger.info('Auto-started video stream monitor on app ready')
            except Exception as exc:
                logger.warning('Auto-start video stream monitor failed: %s', exc)
