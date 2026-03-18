from __future__ import annotations

import json
import logging
import os
import shutil
import socket
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from django.db import close_old_connections
from django.utils import timezone

from .models import VideoStreamTransferRecord


logger = logging.getLogger(__name__)


@dataclass
class StreamRuntimeState:
    frame_count_total: int = 0
    packet_count_total: int = 0
    was_active: bool = False  # 上一轮是否成功探测到推流


@dataclass
class NetworkStats:
    loss_rate: float | None = None
    latency_ms: float | None = None
    jitter_ms: float | None = None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text or text == 'N/A':
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_fraction(frac: str | None) -> float | None:
    if not frac:
        return None
    text = frac.strip()
    if not text or text == '0/0':
        return None
    if '/' not in text:
        return _to_float(text)
    left, right = text.split('/', 1)
    numerator = _to_float(left)
    denominator = _to_float(right)
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def _stream_target(stream_url: str) -> tuple[str, int | None, str, str]:
    """
    返回 (host, port, scheme, ip)。ip为host解析结果，解析失败则为''。
    """
    parsed = urlparse(stream_url)
    host = parsed.hostname or ''
    port = parsed.port
    scheme = parsed.scheme.lower()
    ip = ''
    if host:
        try:
            ip = socket.gethostbyname(host)
        except Exception:
            ip = ''
    return host, port, scheme, ip


def _resolve_host_ip(host: str | None) -> str:
    if not host:
        return ''
    try:
        return socket.gethostbyname(host)
    except Exception:
        return ''


def _default_port(scheme: str) -> int | None:
    return {
        'rtsp': 554,
        'rtmp': 1935,
        'http': 80,
        'https': 443,
    }.get(scheme)


def _stream_protocol(scheme: str) -> str:
    if scheme == 'rtsp':
        return 'RTSP'
    if scheme == 'rtmp':
        return 'RTMP'
    if scheme in {'http', 'https'}:
        return 'HTTP'
    return scheme.upper() or 'UNKNOWN'


def _transport_protocol(scheme: str) -> str:
    if scheme == 'rtsp':
        return 'UDP'
    if scheme in {'http', 'https', 'rtmp'}:
        return 'TCP'
    return 'TCP'


def _run_ffprobe(stream_url: str, timeout: float) -> dict[str, Any]:
    cmd = [
        'ffprobe',
        '-v',
        'error',
        '-show_streams',
        '-show_format',
        '-print_format',
        'json',
        stream_url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or 'ffprobe failed')

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'ffprobe json parse failed: {exc}') from exc


def _run_ping_probe(host: str, timeout: float, count: int) -> NetworkStats:
    if not host:
        return NetworkStats()

    cmd = ['ping', '-n', '-q', '-c', str(max(count, 1)), '-W', str(max(int(timeout), 1)), host]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=max(timeout + 2, 3), check=False)
    text = f'{proc.stdout}\n{proc.stderr}'

    loss_rate: float | None = None
    latency_ms: float | None = None
    jitter_ms: float | None = None

    for line in text.splitlines():
        line = line.strip()
        if 'packet loss' in line and '%' in line:
            try:
                loss_rate = float(line.split('%', 1)[0].split()[-1])
            except Exception:
                pass
        if line.startswith('round-trip') or line.startswith('rtt'):
            try:
                values = line.split('=', 1)[1].strip().split()[0]
                parts = values.split('/')
                if len(parts) >= 4:
                    latency_ms = float(parts[1])
                    jitter_ms = float(parts[3])
            except Exception:
                pass

    return NetworkStats(loss_rate=loss_rate, latency_ms=latency_ms, jitter_ms=jitter_ms)


def _extract_video_stream(info: dict[str, Any]) -> dict[str, Any]:
    for stream in info.get('streams') or []:
        if stream.get('codec_type') == 'video':
            return stream
    raise RuntimeError('no video stream found in ffprobe result')


class VideoStreamMonitorService:
    def __init__(self) -> None:
        self.interval = max(float(os.getenv('VIDEO_STREAM_MONITOR_INTERVAL', '5')), 5.0)
        self.timeout = max(float(os.getenv('VIDEO_STREAM_MONITOR_TIMEOUT', '8')), 1.0)
        self.packet_size = max(int(os.getenv('VIDEO_STREAM_MONITOR_PACKET_SIZE', '1200')), 200)
        self.ping_count = max(int(os.getenv('VIDEO_STREAM_MONITOR_PING_COUNT', '3')), 1)
        self.max_records = max(int(os.getenv('VIDEO_STREAM_MONITOR_MAX_RECORDS', '150')), 50)
        self.enable_ping_probe = os.getenv('VIDEO_STREAM_MONITOR_PING_ENABLED', '1').lower() not in {'0', 'false', 'no'}
        # 默认开启主动探测：感知到推流开始后每5秒采集一次，推流断开后停止记录。
        self.active_pull_enabled = os.getenv('VIDEO_STREAM_MONITOR_ACTIVE_PULL', '1').lower() in {'1', 'true', 'yes'}
        self.source_host = os.getenv('VIDEO_STREAM_MONITOR_SOURCE_HOST', 'push.yunpingtai.cc').strip()
        self.source_ip_override = os.getenv('VIDEO_STREAM_MONITOR_SOURCE_IP', '').strip()
        self.target_host_override = os.getenv('VIDEO_STREAM_MONITOR_TARGET_HOST', '8.130.132.91').strip()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._states: dict[str, StreamRuntimeState] = {}
        self._last_cycle_started_at: str | None = None
        self._last_cycle_finished_at: str | None = None
        self._last_error: str = ''
        self._last_device_count = 0
        self._last_active_count = 0
        self._ffprobe_available = shutil.which('ffprobe') is not None

    def start(self) -> bool:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return False
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, name='video-stream-monitor', daemon=True)
            self._thread.start()
            return True

    def stop(self, timeout: float = 5.0) -> None:
        with self._lock:
            self._stop_event.set()
            thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=timeout)

    def status(self) -> dict[str, Any]:
        with self._lock:
            thread = self._thread
            return {
                'running': bool(thread and thread.is_alive()),
                'interval': self.interval,
                'timeout': self.timeout,
                'packet_size': self.packet_size,
                'ping_enabled': self.enable_ping_probe,
                'active_pull_enabled': self.active_pull_enabled,
                'source_host': self.source_host,
                'source_ip_override': self.source_ip_override,
                'target_host_override': self.target_host_override,
                'ping_count': self.ping_count,
                'max_records': self.max_records,
                'ffprobe_available': self._ffprobe_available,
                'tracked_streams': len(self._states),
                'last_device_count': self._last_device_count,
                'last_active_count': self._last_active_count,
                'last_cycle_started_at': self._last_cycle_started_at,
                'last_cycle_finished_at': self._last_cycle_finished_at,
                'last_error': self._last_error,
            }

    def _run_loop(self) -> None:
        logger.info('Video stream monitor started')
        while not self._stop_event.is_set():
            started = time.time()
            try:
                self._run_cycle()
            except Exception as exc:
                logger.warning('Video stream monitor cycle failed: %s', exc)
                with self._lock:
                    self._last_error = str(exc)

            sleep_time = max(self.interval - (time.time() - started), 0.5)
            self._stop_event.wait(sleep_time)
        logger.info('Video stream monitor stopped')

    def _run_cycle(self) -> None:
        from accounts.models import DroneDevice

        close_old_connections()
        started_at = timezone.now().isoformat()
        active_keys: set[str] = set()
        devices = list(
            DroneDevice.objects.exclude(stream_url__isnull=True)
            .exclude(stream_url='')
            .order_by('id')
        )

        with self._lock:
            self._last_cycle_started_at = started_at
            self._last_device_count = len(devices)
            self._last_active_count = 0
            self._last_error = ''

        if not self.active_pull_enabled:
            # Passive push mode: no outbound stream probing.
            close_old_connections()
            with self._lock:
                self._last_active_count = 0
                self._last_cycle_finished_at = timezone.now().isoformat()
            return

        if not self._ffprobe_available:
            raise RuntimeError('ffprobe 不在 PATH 中，无法采集视频流信息')

        active_count = 0
        for device in devices:
            if self._stop_event.is_set():
                break
            stream_url = (device.stream_url or '').strip()
            if not stream_url:
                continue
            state_key = f'{device.id}:{stream_url}'
            active_keys.add(state_key)
            state = self._states.setdefault(state_key, StreamRuntimeState())

            try:
                self._sample_device(device, stream_url, state)
                if not state.was_active:
                    logger.info('推流开始: %s  URL=%s', device.model, stream_url)
                state.was_active = True
                active_count += 1
            except Exception as exc:
                if state.was_active:
                    # 推流端断开 —— 记录一条结束事件，停止本轮累计
                    logger.info('推流断开: %s  URL=%s  原因=%s', device.model, stream_url, exc)
                    self._record_stream_ended(device, stream_url, state, exc)
                    state.was_active = False
                else:
                    # 推流尚未开始，静默跳过
                    logger.debug('等待推流: %s  %s', device.model, exc)

        stale_keys = [key for key in self._states.keys() if key not in active_keys]
        for key in stale_keys:
            self._states.pop(key, None)

        self._cleanup_old_records()
        close_old_connections()

        with self._lock:
            self._last_active_count = active_count
            self._last_cycle_finished_at = timezone.now().isoformat()

    def _sample_device(self, device: Any, stream_url: str, state: StreamRuntimeState) -> None:
        probe = _run_ffprobe(stream_url, timeout=self.timeout)
        stream = _extract_video_stream(probe)
        fmt = probe.get('format') or {}
        host, target_port, scheme, target_ip = _stream_target(stream_url)
        if self.target_host_override:
            override_ip = _resolve_host_ip(self.target_host_override)
            target_ip = override_ip or self.target_host_override
        elif not target_ip:
            target_ip = host or '127.0.0.1'
        fps = _parse_fraction(stream.get('avg_frame_rate')) or _parse_fraction(stream.get('r_frame_rate'))
        bit_rate_bps = _to_float(stream.get('bit_rate')) or _to_float(fmt.get('bit_rate'))
        bitrate_kbps = bit_rate_bps / 1000.0 if bit_rate_bps else None
        width = stream.get('width')
        height = stream.get('height')

        interval_seconds = max(self.interval, 0.1)
        frame_increment = int((fps or 0.0) * interval_seconds)
        state.frame_count_total += max(frame_increment, 0)

        if bit_rate_bps:
            bytes_per_sec = bit_rate_bps / 8.0
            packets = int(bytes_per_sec * interval_seconds / self.packet_size)
            state.packet_count_total += max(packets, 0)

        network_stats = NetworkStats()
        if self.enable_ping_probe and target_ip:
            network_stats = _run_ping_probe(target_ip, timeout=self.timeout, count=self.ping_count)

        source_ip = self.source_ip_override or _resolve_host_ip(self.source_host)

        VideoStreamTransferRecord.objects.create(
            ship_model=str(device.model),
            timestamp=timezone.now(),
            stream_protocol=_stream_protocol(scheme),
            video_codec=str(stream.get('codec_name') or 'unknown').upper(),
            transport_protocol=_transport_protocol(scheme),
            source_ip=source_ip,
            source_port=None,
            target_ip=target_ip,
            target_port=target_port if target_port is not None else _default_port(scheme),
            stream_url=stream_url,
            frame_width=width,
            frame_height=height,
            fps=round(fps, 2) if fps else None,
            bitrate_kbps=round(bitrate_kbps, 2) if bitrate_kbps else None,
            packet_size=self.packet_size,
            packet_count=state.packet_count_total,
            frame_count=state.frame_count_total,
            loss_rate=round(network_stats.loss_rate, 3) if network_stats.loss_rate is not None else 0,
            latency_ms=round(network_stats.latency_ms, 3) if network_stats.latency_ms is not None else None,
            jitter_ms=round(network_stats.jitter_ms, 3) if network_stats.jitter_ms is not None else None,
            status='normal',
            warn='1' if (network_stats.loss_rate or 0) >= 5 else '0',
            raw_payload=json.dumps({'stream': stream, 'format': fmt}, ensure_ascii=False)[:3000],
        )

    def _record_stream_ended(self, device: Any, stream_url: str, state: StreamRuntimeState, exc: Exception) -> None:
        """推流断开时记录一条结束事件（只在状态从 active→inactive 时调用一次）。"""
        host, target_port, scheme, target_ip = _stream_target(stream_url)
        if self.target_host_override:
            override_ip = _resolve_host_ip(self.target_host_override)
            target_ip = override_ip or self.target_host_override
        elif not target_ip:
            target_ip = host or '127.0.0.1'
        source_ip = self.source_ip_override or _resolve_host_ip(self.source_host)
        VideoStreamTransferRecord.objects.create(
            ship_model=str(device.model),
            timestamp=timezone.now(),
            stream_protocol=_stream_protocol(scheme),
            video_codec='UNKNOWN',
            transport_protocol=_transport_protocol(scheme),
            source_ip=source_ip,
            source_port=None,
            target_ip=target_ip,
            target_port=target_port if target_port is not None else _default_port(scheme),
            stream_url=stream_url,
            packet_size=self.packet_size,
            packet_count=state.packet_count_total,
            frame_count=state.frame_count_total,
            loss_rate=0,
            latency_ms=None,
            jitter_ms=None,
            status='error',
            warn='1',
            raw_payload=str(exc)[:3000],
        )
        with self._lock:
            self._last_error = str(exc)

    def _cleanup_old_records(self) -> None:
        total = VideoStreamTransferRecord.objects.count()
        if total <= self.max_records:
            return
        stale_ids = list(
            VideoStreamTransferRecord.objects.order_by('collection_time')
            .values_list('id', flat=True)[: total - self.max_records]
        )
        if stale_ids:
            VideoStreamTransferRecord.objects.filter(id__in=stale_ids).delete()


video_stream_monitor_service = VideoStreamMonitorService()