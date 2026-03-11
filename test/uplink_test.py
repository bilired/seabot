import argparse
import socket
import struct
import time
from dataclasses import dataclass
from typing import Optional


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


@dataclass
class PacketOptions:
    packet_type: str
    msg_id: int = 0
    with_tail: bool = True


def build_packet(payload: bytes, options: PacketOptions) -> bytes:
    packet_type = options.packet_type.encode('ascii')[:1]
    type_2bytes = packet_type.ljust(2, b'\x00')

    padlen = len(payload) + 2

    header = b''
    header += b'$@'
    header += type_2bytes
    header += struct.pack('<i', options.msg_id)
    header += struct.pack('<i', padlen)

    body = header + payload
    crc = calc_crc(0, body, len(body))
    packet = body + crc

    if options.with_tail:
        packet += b'\xAA\x55'

    return packet


def make_payload_from_text(payload_text: str) -> bytes:
    return payload_text.encode('ascii')


def make_payload_from_int(value: int) -> bytes:
    return struct.pack('<i', value)


def make_payload_from_int_float(cmd_id: int, value: float) -> bytes:
    return struct.pack('<if', cmd_id, value)


def send_packet(host: str, port: int, packet: bytes, timeout_sec: float = 5.0) -> Optional[bytes]:
    with socket.create_connection((host, port), timeout=timeout_sec) as client:
        try:
            client.settimeout(1.0)
            ready = client.recv(64)
            if ready:
                print(f'[recv-ready] {ready!r}')
        except Exception:
            pass

        sent = client.send(packet)
        print(f'[send] bytes={sent}')

        try:
            client.settimeout(1.5)
            response = client.recv(1024)
            if response:
                print(f'[recv] {response.hex()}')
                return response
        except Exception:
            pass

    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='微星图协议 TCP 上行测试脚本')
    parser.add_argument('--host', default='127.0.0.1', help='服务器IP')
    parser.add_argument('--port', type=int, default=9001, help='服务器端口（文档默认 9001）')
    parser.add_argument('--type', dest='packet_type', default='W', help='报文 type，例如 W/Y/B/S/1/8')
    parser.add_argument('--msg-id', type=int, default=0, help='msg_id，默认 0')
    parser.add_argument('--without-tail', action='store_true', help='不追加固定包尾 AA55')

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--payload-text', help='ASCII 文本 payload（常用于 W/Y/B）')
    mode.add_argument('--payload-int', type=int, help='4字节整数 payload（常用于推进器/命令）')
    mode.add_argument('--payload-cmd-float', nargs=2, metavar=('CMD_ID', 'VALUE'), help='int+float 8字节 payload（文档 send_cmd_to_uart 风格）')

    parser.add_argument('--dry-run', action='store_true', help='只打印报文HEX，不实际发送')
    parser.add_argument('--count', type=int, default=1, help='发送次数（>1 即压测模式）')
    parser.add_argument('--interval', type=float, default=0.2, help='每次发送间隔秒数')
    parser.add_argument('--timeout', type=float, default=5.0, help='TCP连接超时秒数')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.payload_text is not None:
        payload = make_payload_from_text(args.payload_text)
    elif args.payload_int is not None:
        payload = make_payload_from_int(args.payload_int)
    else:
        cmd_id = int(args.payload_cmd_float[0])
        value = float(args.payload_cmd_float[1])
        payload = make_payload_from_int_float(cmd_id, value)

    packet = build_packet(
        payload=payload,
        options=PacketOptions(
            packet_type=args.packet_type,
            msg_id=args.msg_id,
            with_tail=not args.without_tail,
        ),
    )

    print(f'[packet-len] {len(packet)}')
    print(f'[packet-hex] {packet.hex()}')

    if args.dry_run:
        return

    total = max(1, args.count)
    send_ok = 0
    recv_ok = 0
    start_time = time.time()

    for i in range(total):
        try:
            response = send_packet(args.host, args.port, packet, timeout_sec=args.timeout)
            send_ok += 1
            if response is not None:
                recv_ok += 1
            print(f'[round] {i + 1}/{total} status=ok recv={response is not None}')
        except Exception as exc:
            print(f'[round] {i + 1}/{total} status=fail err={exc}')

        if i < total - 1 and args.interval > 0:
            time.sleep(args.interval)

    duration = time.time() - start_time
    print('[summary]'
          f' total={total}'
          f' send_ok={send_ok}'
          f' send_fail={total - send_ok}'
          f' recv_ok={recv_ok}'
          f' elapsed={duration:.3f}s'
          f' tps={total / duration:.2f}' if duration > 0 else '')


if __name__ == '__main__':
    main()
