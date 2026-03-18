#!/usr/bin/env python3
"""
Use ffprobe to sample video stream metrics and upload them to:
POST /api/upload/video-stream/

Quick start:
  python3 video_stream_ffprobe_uploader.py \
    --stream-url rtsp://127.0.0.1:8554/live/test \
    --ship-model DL-3026 \
    --upload-url http://127.0.0.1:8000/api/upload/video-stream/

Requirements:
  - ffprobe command available in PATH (from FFmpeg)
  - requests package
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import requests


@dataclass
class CollectorConfig:
    stream_url: str
    ship_model: str
    upload_url: str
    interval: float
    timeout: float
    packet_size: int
    source_ip: str
    source_port: int | None
    target_ip: str
    target_port: int | None
    enable_ping_probe: bool
    ping_count: int
    run_once: bool


@dataclass
class RuntimeState:
    frame_count_total: int = 0
    packet_count_total: int = 0


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
    frac = frac.strip()
    if not frac or frac == '0/0':
        return None
    if '/' not in frac:
        return _to_float(frac)
    left, right = frac.split('/', 1)
    num = _to_float(left)
    den = _to_float(right)
    if num is None or den in (None, 0):
        return None
    return num / den


def _parse_host_port(stream_url: str) -> tuple[str, int | None]:
    parsed = urlparse(stream_url)
    host = parsed.hostname or ''
    port = parsed.port
    return host, port


def run_ffprobe(stream_url: str, timeout: float) -> dict[str, Any]:
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


def run_ping_probe(host: str, timeout: float, count: int) -> NetworkStats:
    if not host:
        return NetworkStats()

    cmd = ['ping', '-n', '-q', '-c', str(max(count, 1)), '-W', str(max(int(timeout), 1)), host]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=max(timeout + 2, 3), check=False)
    text = f"{proc.stdout}\n{proc.stderr}"

    loss_rate: float | None = None
    latency_ms: float | None = None
    jitter_ms: float | None = None

    for line in text.splitlines():
        line = line.strip()
        if 'packet loss' in line and '%' in line:
            try:
                loss_str = line.split('%', 1)[0].split()[-1]
                loss_rate = float(loss_str)
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


def extract_video_stream(info: dict[str, Any]) -> dict[str, Any]:
    streams = info.get('streams') or []
    for stream in streams:
        if stream.get('codec_type') == 'video':
            return stream
    raise RuntimeError('no video stream found in ffprobe result')


def build_payload(
    cfg: CollectorConfig,
    state: RuntimeState,
    probe: dict[str, Any],
    network_stats: NetworkStats,
) -> dict[str, Any]:
    stream = extract_video_stream(probe)
    fmt = probe.get('format') or {}

    width = stream.get('width')
    height = stream.get('height')

    # Prefer average frame rate; fallback to r_frame_rate.
    fps = _parse_fraction(stream.get('avg_frame_rate')) or _parse_fraction(stream.get('r_frame_rate'))

    bit_rate_bps = _to_float(stream.get('bit_rate')) or _to_float(fmt.get('bit_rate'))
    bitrate_kbps = (bit_rate_bps / 1000.0) if bit_rate_bps else None

    codec = str(stream.get('codec_name') or 'unknown').upper()

    # Local cumulative estimation (ffprobe snapshots do not provide cumulative packet counters).
    interval_seconds = max(cfg.interval, 0.1)
    frame_increment = int((fps or 0.0) * interval_seconds)
    state.frame_count_total += max(frame_increment, 0)

    if bit_rate_bps and cfg.packet_size > 0:
        bytes_per_sec = bit_rate_bps / 8.0
        packets = int(bytes_per_sec * interval_seconds / cfg.packet_size)
        state.packet_count_total += max(packets, 0)

    protocol = 'RTSP' if cfg.stream_url.lower().startswith('rtsp://') else 'HTTP'

    payload = {
        'ship_model': cfg.ship_model,
        'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
        'stream_protocol': protocol,
        'video_codec': codec,
        'transport_protocol': 'UDP',
        'source_ip': cfg.source_ip,
        'source_port': cfg.source_port,
        'target_ip': cfg.target_ip,
        'target_port': cfg.target_port,
        'stream_url': cfg.stream_url,
        'frame_width': width,
        'frame_height': height,
        'fps': round(fps, 2) if fps else None,
        'bitrate_kbps': round(bitrate_kbps, 2) if bitrate_kbps else None,
        'packet_size': cfg.packet_size,
        'packet_count': state.packet_count_total,
        'frame_count': state.frame_count_total,
        # Use ping probe as a practical approximation for network quality.
        'loss_rate': round(network_stats.loss_rate, 3) if network_stats.loss_rate is not None else 0,
        'latency_ms': round(network_stats.latency_ms, 3)
        if network_stats.latency_ms is not None
        else None,
        'jitter_ms': round(network_stats.jitter_ms, 3) if network_stats.jitter_ms is not None else None,
        'status': 'normal',
        'warn': '1' if (network_stats.loss_rate or 0) >= 5 else '0',
        'raw_payload': json.dumps({'stream': stream, 'format': fmt}, ensure_ascii=False)[:3000],
    }

    return payload


def post_payload(upload_url: str, payload: dict[str, Any], timeout: float) -> None:
    resp = requests.post(upload_url, json=payload, timeout=timeout)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f'upload failed: http={resp.status_code}, body={resp.text[:300]}')

    body: dict[str, Any] = {}
    try:
        body = resp.json()
    except Exception:
        pass

    code = body.get('code')
    if code not in (None, 200):
        raise RuntimeError(f'upload failed: code={code}, body={body}')


def parse_args() -> CollectorConfig:
    parser = argparse.ArgumentParser(description='Collect stream stats with ffprobe and upload to Django API')
    parser.add_argument('--stream-url', required=True, help='Live stream URL, e.g. rtsp://127.0.0.1:8554/live/test')
    parser.add_argument('--ship-model', required=True, help='Ship model identifier, e.g. DL-3026')
    parser.add_argument(
        '--upload-url',
        default='http://127.0.0.1:8000/api/upload/video-stream/',
        help='Backend upload endpoint URL',
    )
    parser.add_argument('--interval', type=float, default=5.0, help='Sampling interval in seconds')
    parser.add_argument('--timeout', type=float, default=8.0, help='Timeout for ffprobe and HTTP requests')
    parser.add_argument('--packet-size', type=int, default=1200, help='Estimated RTP packet size in bytes')
    parser.add_argument('--source-ip', default='127.0.0.1', help='Source IP field for payload')
    parser.add_argument('--source-port', type=int, default=None, help='Source port field for payload')
    parser.add_argument('--target-ip', default='127.0.0.1', help='Target IP field for payload')
    parser.add_argument('--target-port', type=int, default=None, help='Target port field for payload')
    parser.add_argument(
        '--disable-ping-probe',
        action='store_true',
        help='Disable ping probe for loss/latency/jitter estimation',
    )
    parser.add_argument('--ping-count', type=int, default=4, help='ICMP packets per probe round')
    parser.add_argument('--once', action='store_true', help='Run only one collection cycle')

    args = parser.parse_args()

    target_ip, target_port = _parse_host_port(args.stream_url)
    source_ip = args.source_ip
    source_port = args.source_port

    return CollectorConfig(
        stream_url=args.stream_url,
        ship_model=args.ship_model,
        upload_url=args.upload_url,
        interval=max(args.interval, 0.5),
        timeout=max(args.timeout, 1.0),
        packet_size=max(args.packet_size, 200),
        source_ip=source_ip,
        source_port=source_port,
        target_ip=args.target_ip if args.target_ip else target_ip,
        target_port=args.target_port if args.target_port is not None else target_port,
        enable_ping_probe=not args.disable_ping_probe,
        ping_count=max(args.ping_count, 1),
        run_once=bool(args.once),
    )


def main() -> int:
    cfg = parse_args()
    state = RuntimeState()

    print('[collector] started')
    print(f'[collector] stream={cfg.stream_url}')
    print(f'[collector] upload={cfg.upload_url}')
    print(f'[collector] ship_model={cfg.ship_model}')
    print(f'[collector] interval={cfg.interval}s')
    print(f'[collector] ping_probe={cfg.enable_ping_probe}, ping_count={cfg.ping_count}')

    while True:
        started = time.time()
        try:
            probe = run_ffprobe(cfg.stream_url, timeout=cfg.timeout)
            network_stats = NetworkStats()
            if cfg.enable_ping_probe:
                ping_host = cfg.target_ip or _parse_host_port(cfg.stream_url)[0]
                network_stats = run_ping_probe(
                    host=ping_host,
                    timeout=cfg.timeout,
                    count=cfg.ping_count,
                )

            payload = build_payload(cfg, state, probe, network_stats)
            post_payload(cfg.upload_url, payload, timeout=cfg.timeout)
            print(
                '[ok] '
                f"fps={payload['fps']} "
                f"bitrate_kbps={payload['bitrate_kbps']} "
                f"loss={payload['loss_rate']}% "
                f"latency={payload['latency_ms']}ms "
                f"jitter={payload['jitter_ms']}ms "
                f"frames={payload['frame_count']} "
                f"packets={payload['packet_count']}"
            )
        except KeyboardInterrupt:
            print('\n[collector] stopped by user')
            return 0
        except Exception as exc:
            print(f'[warn] {exc}')

        if cfg.run_once:
            print('[collector] run once completed')
            return 0

        elapsed = time.time() - started
        sleep_time = max(cfg.interval - elapsed, 0.1)
        time.sleep(sleep_time)


if __name__ == '__main__':
    raise SystemExit(main())
