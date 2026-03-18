import signal
from threading import Event
from time import sleep, time

from django.core.management.base import BaseCommand, CommandError

from monitoring.ship_gateway import gateway_service


class Command(BaseCommand):
    help = '启动无人船 TCP 网关服务（端口默认 9001-9004）'

    def add_arguments(self, parser):
        parser.add_argument('--host', default=None, help='监听地址，默认保持当前配置')
        parser.add_argument('--port-start', type=int, default=None, help='起始端口，默认保持当前配置')
        parser.add_argument('--ship-count', type=int, default=None, help='船舶数量，每船占用两个端口')
        parser.add_argument('--status-interval', type=int, default=30, help='状态输出间隔（秒），0 表示关闭')

    def _build_target_config(self, options):
        status = gateway_service.status()
        host = options['host'] if options['host'] is not None else status['host']
        port_start = options['port_start'] if options['port_start'] is not None else status['port_start']
        ship_count = options['ship_count'] if options['ship_count'] is not None else status['ship_count']

        if port_start <= 0:
            raise CommandError('--port-start 必须大于 0')
        if ship_count <= 0:
            raise CommandError('--ship-count 必须大于 0')

        return {
            'host': host,
            'port_start': port_start,
            'ship_count': ship_count,
        }

    def _print_status(self, prefix='status'):
        status = gateway_service.status()
        port_end = status['port_start'] + status['ship_count'] * 2 - 1
        self.stdout.write(
            f"[{prefix}] running={status['running']} host={status['host']} "
            f"ports={status['port_start']}-{port_end} online={status['online_ports']}"
        )

    def handle(self, *args, **options):
        target = self._build_target_config(options)
        status_interval = max(0, int(options['status_interval']))

        status = gateway_service.status()
        if status['running']:
            if (
                status['host'] != target['host']
                or status['port_start'] != target['port_start']
                or status['ship_count'] != target['ship_count']
            ):
                raise CommandError(
                    '网关已在运行，且当前配置与参数不一致。请先停止现有进程，或设置 SHIP_GATEWAY_AUTO_START=0 后再启动。'
                )
            self.stdout.write(self.style.WARNING('Ship gateway already running, attach monitor mode.'))
        else:
            gateway_service.host = target['host']
            gateway_service.port_start = target['port_start']
            gateway_service.ship_count = target['ship_count']
            gateway_service.start()
            self.stdout.write(self.style.SUCCESS('Ship gateway started. Press Ctrl+C to stop.'))

        stop_event = Event()

        def _request_stop(_signum, _frame):
            stop_event.set()

        signal.signal(signal.SIGTERM, _request_stop)
        signal.signal(signal.SIGINT, _request_stop)

        self._print_status(prefix='startup')
        next_status_time = time() + status_interval if status_interval > 0 else 0

        try:
            while not stop_event.is_set():
                sleep(1)
                if status_interval > 0 and time() >= next_status_time:
                    self._print_status()
                    next_status_time = time() + status_interval
        finally:
            gateway_service.stop()
            self.stdout.write(self.style.WARNING('Ship gateway stopped.'))
