from django.core.management.base import BaseCommand
from time import sleep

from monitoring.ship_gateway import gateway_service


class Command(BaseCommand):
    help = '启动无人船 TCP 网关服务（端口默认 9001-9004）'

    def handle(self, *args, **options):
        gateway_service.start()
        self.stdout.write(self.style.SUCCESS('Ship gateway started. Press Ctrl+C to stop.'))
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            gateway_service.stop()
            self.stdout.write(self.style.WARNING('Ship gateway stopped.'))
