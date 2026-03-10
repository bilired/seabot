import logging
import os
import socket
import struct
import threading
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from .models import NutrientData, WaterQualityData

logger = logging.getLogger(__name__)


def load_ship_port_model_map() -> Dict[str, str]:
    default_map = {
        '9001': 'DL-3022',
        '9003': 'DL-3026',
    }

    raw = os.getenv('SHIP_PORT_MODEL_MAP', '').strip()
    if not raw:
        return default_map

    parsed: Dict[str, str] = {}
    for item in raw.split(','):
        part = item.strip()
        if not part or ':' not in part:
            continue
        port, model = part.split(':', 1)
        port = port.strip()
        model = model.strip()
        if port and model:
            parsed[port] = model

    if not parsed:
        return default_map

    merged = default_map.copy()
    merged.update(parsed)
    return merged


def calc_crc(crc: int, buf: bytes, length: int) -> bytes:
    remainder = crc & 0xFFFF
    top_bit = 0x8000

    for i in range(length):
        byte = buf[i]
        acc = (byte << 8) & 0xFF00
        remainder ^= acc
        remainder &= 0xFFFF

        for _ in range(8):
            if remainder & top_bit:
                remainder = ((remainder << 1) ^ 0x8005) & 0xFFFF
            else:
                remainder = (remainder << 1) & 0xFFFF

    return remainder.to_bytes(2, byteorder='big', signed=False)


def parse_packets(data: bytes) -> Tuple[List[dict], bytes]:
    packets: List[dict] = []
    index = 0
    total_length = len(data)

    while index + 12 <= total_length:
        if data[index:index + 2] != b'$@':
            index += 1
            continue

        packet_type_raw = data[index + 2:index + 4]
        try:
            packet_type = packet_type_raw.rstrip(b'\x00').decode('ascii')
        except UnicodeDecodeError:
            index += 1
            continue

        msg_id_bytes = data[index + 4:index + 8]
        if len(msg_id_bytes) < 4:
            break
        message_id = struct.unpack('<i', msg_id_bytes)[0]

        padlen_bytes = data[index + 8:index + 12]
        if len(padlen_bytes) < 4:
            break
        padded_length = struct.unpack('<i', padlen_bytes)[0]
        payload_len = padded_length - 2

        packet_length = 12 + padded_length
        if index + packet_length > total_length:
            break

        packet_data = data[index:index + packet_length]
        index += packet_length

        calculated_crc = calc_crc(0, packet_data, len(packet_data) - 2).hex()
        current_crc = packet_data[-2:].hex()

        payload_bytes = packet_data[12:12 + payload_len]
        payload_text = payload_bytes.decode('ascii', errors='ignore')

        int_payload = None
        if len(payload_bytes) >= 4:
            try:
                int_payload = struct.unpack('<i', payload_bytes[0:4])[0]
            except Exception:
                int_payload = None

        packets.append({
            'packet_type': packet_type,
            'message_id': message_id,
            'payload_length': payload_len,
            'payload_bytes': payload_bytes,
            'payload_text': payload_text,
            'payload_hex': payload_bytes.hex(),
            'payload_int': int_payload,
            'calculated_crc': calculated_crc,
            'crc_valid': int(calculated_crc == current_crc),
        })

    return packets, data[index:]


def parse_water_payload(ship_model: str, input_text: str) -> dict:
    parts = input_text.strip().split('|')
    if len(parts) != 10:
        raise ValueError(f'无效水质数据格式，应有10个字段，实际收到 {len(parts)} 个')

    return {
        'ship_model': str(ship_model),
        'temperature': float(parts[2]) if parts[2] else 0.0,
        'ph': float(parts[3]) if parts[3] else 0.0,
        'conductivity': float(parts[4]) if parts[4] else 0.0,
        'salinity': float(parts[5]) if parts[5] else 0.0,
        'turbidity': float(parts[6]) if parts[6] else 0.0,
        'chlorophyll': float(parts[7]) if parts[7] else 0.0,
        'algae': int(round(float(parts[8]))) if parts[8] else 0,
        'dissolved_oxygen': float(parts[9]) if parts[9] else 0.0,
        'warning_code': parts[1] or '正常',
        'connection_status': '在线',
    }


def _parse_device_time(value: str) -> datetime:
    dt = datetime.strptime(value, '%Y%m%d%H%M%S')
    return dt.replace(tzinfo=timezone.utc)


def parse_nutrient_payload(ship_model: str, input_text: str) -> dict:
    cleaned = input_text.strip().rstrip(':')
    parts = cleaned.split('|')
    if len(parts) < 11:
        raise ValueError(f'无效营养盐数据格式，至少11个字段，实际收到 {len(parts)} 个')

    phosphate_value = parts[0].lstrip('Y')

    return {
        'ship_model': str(ship_model),
        'phosphate': float(phosphate_value) if phosphate_value else 0.0,
        'phosphate_time': _parse_device_time(parts[1]) if parts[1] else datetime.now(timezone.utc),
        'ammonia': float(parts[2]) if parts[2] else 0.0,
        'ammonia_time': _parse_device_time(parts[3]) if parts[3] else datetime.now(timezone.utc),
        'nitrate': float(parts[4]) if parts[4] else 0.0,
        'nitrate_time': _parse_device_time(parts[5]) if parts[5] else datetime.now(timezone.utc),
        'nitrite': float(parts[6]) if parts[6] else 0.0,
        'nitrite_time': _parse_device_time(parts[7]) if parts[7] else datetime.now(timezone.utc),
        'error_code1': str(parts[8]) if len(parts) > 8 and parts[8] != '' else '00',
        'error_code2': str(parts[9]) if len(parts) > 9 and parts[9] != '' else '00',
        'instrument_status': str(parts[10]) if len(parts) > 10 and parts[10] != '' else '正常',
        'connection_status': '在线',
    }


def parse_boat_payload(input_text: str) -> dict:
    """Parse type-B boat status payload.

    Expected format (8 fields):
    shipModel|boatTimestamp|status|latitude|longitude|speed|direction|batteryVoltage
    """
    parts = input_text.strip().split('|')
    if len(parts) < 1 or not parts[0].strip():
        raise ValueError('无效船体数据格式，缺少 shipModel 字段')

    def _to_float(value: str):
        return float(value) if value != '' else None

    data = {
        'ship_model': parts[0].strip(),
        'raw': input_text.strip(),
    }

    if len(parts) >= 8:
        data.update({
            'boat_timestamp': parts[1] or None,
            'status': parts[2] or None,
            'latitude': _to_float(parts[3]),
            'longitude': _to_float(parts[4]),
            'speed': _to_float(parts[5]),
            'direction': _to_float(parts[6]),
            'battery_voltage': _to_float(parts[7]),
        })

    return data


def parse_depth_payload(input_text: str) -> dict:
    """Parse type-D depth payload.

    Common format: depth|reserved
    """
    parts = input_text.strip().rstrip(':').split('|')
    if not parts or parts[0] == '':
        raise ValueError('无效深度数据格式，缺少 depth 字段')

    return {
        'depth': float(parts[0]),
        'raw': input_text.strip(),
    }


def parse_rtk_payload(input_text: str) -> dict:
    """Parse type-0 RTK payload.

    Expected format (7 fields):
    depth|RTKlatitude|RTKlatitude_direction|RTKlongitude|RTKlongitude_direction|temperature|RTKelevation
    """
    parts = input_text.strip().rstrip(':').split('|')
    if len(parts) != 7:
        raise ValueError(f'无效RTK数据格式，应有7个字段，实际收到 {len(parts)} 个')

    return {
        'depth': float(parts[0]) if parts[0] else None,
        'rtk_latitude': float(parts[1]) if parts[1] else None,
        'rtk_latitude_direction': parts[2] or None,
        'rtk_longitude': float(parts[3]) if parts[3] else None,
        'rtk_longitude_direction': parts[4] or None,
        'temperature': float(parts[5]) if parts[5] else None,
        'rtk_elevation': float(parts[6]) if parts[6] else None,
        'raw': input_text.strip(),
    }


def generate_packet(command_type: bytes, direction_code: int) -> bytes:
    send_buff = bytearray()
    send_buff += b'$'
    send_buff += b'@'
    send_buff += command_type.ljust(2, b'\x00')
    send_buff += struct.pack('i', 0)
    send_buff += struct.pack('i', 6)
    send_buff += struct.pack('i', direction_code)
    return bytes(send_buff)


ACTIONS = {
    'up': generate_packet(b'S', 402),
    'down': generate_packet(b'S', 404),
    'left': generate_packet(b'S', 405),
    'right': generate_packet(b'S', 407),
    'camera_normal': generate_packet(b'8', 327),
    'camera_night': generate_packet(b'8', 326),
    'sampling_on': generate_packet(b'8', 328),
    'sampling_off': generate_packet(b'8', 329),
    'monitoring_lift': generate_packet(b'8', 330),
    'monitoring_recover': generate_packet(b'8', 331),
    'instrument_normal': generate_packet(b'8', 332),
    'instrument_abnormal': generate_packet(b'8', 333),
}


class ShipGatewayService:
    def __init__(self, host: str = '0.0.0.0', port_start: int = 9001, ship_count: int = 2) -> None:
        self.host = host
        self.port_start = port_start
        self.ship_count = ship_count
        self.ship_port_model_map = load_ship_port_model_map()
        self.reported_ship_model_by_port: Dict[int, str] = {}
        self.last_boat_packet_by_port: Dict[int, dict] = {}
        self.last_depth_packet_by_port: Dict[int, dict] = {}
        self.last_rtk_packet_by_port: Dict[int, dict] = {}
        self.clients: Dict[int, socket.socket] = {}
        self._servers: List[socket.socket] = []
        self._threads: List[threading.Thread] = []
        self._lock = threading.Lock()
        self._running = False

    def start(self) -> None:
        if self._running:
            return

        self._running = True
        for port in range(self.port_start, self.port_start + self.ship_count * 2):
            thread = threading.Thread(target=self._start_server, args=(port,), daemon=True)
            thread.start()
            self._threads.append(thread)
        logger.info('Ship gateway started on ports %s-%s', self.port_start, self.port_start + self.ship_count * 2 - 1)

    def stop(self) -> None:
        self._running = False
        with self._lock:
            for client in self.clients.values():
                try:
                    client.close()
                except Exception:
                    pass
            self.clients.clear()
            self.reported_ship_model_by_port.clear()
            self.last_boat_packet_by_port.clear()
            self.last_depth_packet_by_port.clear()
            self.last_rtk_packet_by_port.clear()

        for server in self._servers:
            try:
                server.close()
            except Exception:
                pass
        self._servers.clear()

    def status(self) -> dict:
        with self._lock:
            online_ports = sorted(self.clients.keys())
            reported_models = {str(port): model for port, model in self.reported_ship_model_by_port.items()}
            last_boat_packets = {
                str(port): payload for port, payload in self.last_boat_packet_by_port.items()
            }
            last_depth_packets = {
                str(port): payload for port, payload in self.last_depth_packet_by_port.items()
            }
            last_rtk_packets = {
                str(port): payload for port, payload in self.last_rtk_packet_by_port.items()
            }
        return {
            'running': self._running,
            'host': self.host,
            'port_start': self.port_start,
            'ship_count': self.ship_count,
            'online_ports': online_ports,
            'reported_models': reported_models,
            'last_boat_packets': last_boat_packets,
            'last_depth_packets': last_depth_packets,
            'last_rtk_packets': last_rtk_packets,
        }

    def send_action(self, cmd: str, ship_port: int, control_port: int) -> dict:
        if cmd not in ACTIONS:
            raise ValueError(f'不支持的命令: {cmd}')

        payload = ACTIONS[cmd]
        packet = payload + calc_crc(0, payload, len(payload))

        delivered = []
        failed = []

        with self._lock:
            for port in (control_port, ship_port):
                client = self.clients.get(port)
                if not client:
                    failed.append(port)
                    continue
                try:
                    client.send(packet)
                    delivered.append(port)
                except Exception:
                    failed.append(port)

        return {
            'cmd': cmd,
            'packet_hex': packet.hex(),
            'delivered_ports': delivered,
            'failed_ports': failed,
        }

    def _start_server(self, port: int) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, port))
        server.listen(5)
        server.settimeout(1)
        self._servers.append(server)
        logger.info('TCP listener started: %s:%s', self.host, port)

        while self._running:
            try:
                client, _ = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            thread = threading.Thread(target=self._handle_client_connection, args=(client, port), daemon=True)
            thread.start()

    def _handle_client_connection(self, client: socket.socket, port: int) -> None:
        try:
            client.send(b'Ready')
            while self._running:
                try:
                    data = client.recv(1024)
                except (ConnectionResetError, BrokenPipeError, OSError):
                    # Peer closed/reset connection, stop this client loop quietly.
                    break
                if not data:
                    break

                with self._lock:
                    self.clients[port] = client

                if data.hex() == '00':
                    continue

                packets, _ = parse_packets(data)
                self._persist_packets(ship_port=port, packets=packets)

                if port % 2 == 0 and any(packet['packet_type'] != 'B' for packet in packets):
                    with self._lock:
                        paired = self.clients.get(port - 1)
                    if paired:
                        try:
                            paired.send(data)
                        except Exception:
                            pass
        finally:
            with self._lock:
                if self.clients.get(port) is client:
                    self.clients.pop(port, None)
                self.reported_ship_model_by_port.pop(port, None)
                self.last_boat_packet_by_port.pop(port, None)
                self.last_depth_packet_by_port.pop(port, None)
                self.last_rtk_packet_by_port.pop(port, None)
            try:
                client.close()
            except Exception:
                pass

    def _extract_ship_model_from_boat_packet(self, payload_text: str) -> str:
        parts = payload_text.strip().split('|')
        if len(parts) >= 1 and parts[0].strip():
            return parts[0].strip()
        return ''

    def _resolve_ship_model(self, ship_port: int) -> str:
        with self._lock:
            reported = self.reported_ship_model_by_port.get(ship_port)
        if reported:
            return reported
        return self.ship_port_model_map.get(str(ship_port), str(ship_port))

    def _persist_packets(self, ship_port: int, packets: List[dict]) -> None:
        for packet in packets:
            if packet['packet_type'] != 'B':
                continue
            try:
                boat_payload = parse_boat_payload(packet['payload_text'])
                reported = boat_payload['ship_model']
                with self._lock:
                    self.reported_ship_model_by_port[ship_port] = reported
                    self.last_boat_packet_by_port[ship_port] = boat_payload
            except Exception as exc:
                logger.warning('Parse boat packet failed on port %s: %s', ship_port, exc)

        ship_model = self._resolve_ship_model(ship_port)
        for packet in packets:
            packet_type = packet['packet_type']
            try:
                if packet_type == 'W':
                    model_data = parse_water_payload(ship_model, packet['payload_text'])
                    WaterQualityData.objects.create(**model_data)
                elif packet_type in ('Y', '@'):
                    model_data = parse_nutrient_payload(ship_model, packet['payload_text'])
                    NutrientData.objects.create(**model_data)
                elif packet_type == 'D':
                    depth_payload = parse_depth_payload(packet['payload_text'])
                    with self._lock:
                        self.last_depth_packet_by_port[ship_port] = depth_payload
                elif packet_type == '0':
                    rtk_payload = parse_rtk_payload(packet['payload_text'])
                    with self._lock:
                        self.last_rtk_packet_by_port[ship_port] = rtk_payload
            except Exception as exc:
                logger.warning('Persist packet failed on port %s type %s: %s', ship_port, packet_type, exc)


gateway_service = ShipGatewayService()
