import signal
from threading import Event
from time import sleep, time

from django.core.management.base import BaseCommand

from monitoring.video_stream_monitor import video_stream_monitor_service


class Command(BaseCommand):
    help = '启动视频流监控服务，持续轮询无人船设备中的拉流地址并写入视频流监测记录'

    def add_arguments(self, parser):
        parser.add_argument('--status-interval', type=int, default=30, help='状态输出间隔（秒），0 表示关闭')

    def _print_status(self, prefix='status'):
        status = video_stream_monitor_service.status()
        self.stdout.write(
            f"[{prefix}] running={status['running']} ffprobe_available={status['ffprobe_available']} "
            f"devices={status['last_device_count']} active={status['last_active_count']} "
            f"tracked={status['tracked_streams']} last_error={status['last_error'] or '-'}"
        )

    def handle(self, *args, **options):
        started = video_stream_monitor_service.start()
        if started:
            self.stdout.write(self.style.SUCCESS('Video stream monitor started. Press Ctrl+C to stop.'))
        else:
            self.stdout.write(self.style.WARNING('Video stream monitor already running, attach monitor mode.'))

        stop_event = Event()
        status_interval = max(0, int(options['status_interval']))

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
            video_stream_monitor_service.stop()
            self.stdout.write(self.style.WARNING('Video stream monitor stopped.'))