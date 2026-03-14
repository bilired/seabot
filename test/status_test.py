"""
模拟无人船持续上报船体位置 (B 包) 的测试脚本。

协议 B 包 payload 字段顺序（8字段）:
  data_id | timestamp | latitude | longitude | course | speed | battery_level | water_extraction

时间戳格式: YYYYMMDDHHmmss (UTC)
"""

import socket
import struct
import time
from datetime import datetime, timezone


# ---------- 与 ship_gateway.py 保持一致的 CRC 实现 ----------

def calc_crc(crc: int, buf: bytes, length: int) -> bytes:
    remainder = crc & 0xFFFF
    top_bit = 0x8000
    for i in range(length):
        byte = buf[i]
        remainder ^= (byte << 8) & 0xFF00
        remainder &= 0xFFFF
        for _ in range(8):
            if remainder & top_bit:
                remainder = ((remainder << 1) ^ 0x8005) & 0xFFFF
            else:
                remainder = (remainder << 1) & 0xFFFF
    return remainder.to_bytes(2, byteorder='big', signed=False)


def build_packet(packet_type: str, msg_id: int, payload: bytes) -> bytes:
    """构造标准协议帧: $@ + type(2B) + msg_id(4B LE) + padlen(4B LE) + payload + CRC(2B) + tail(AA55)"""
    type_2b = packet_type.encode('ascii')[:1].ljust(2, b'\x00')
    padlen = len(payload) + 2  # +2 for CRC
    header = b'$@' + type_2b + struct.pack('<i', msg_id) + struct.pack('<i', padlen)
    body = header + payload
    crc = calc_crc(0, body, len(body))
    return body + crc + b'\xAA\x55'


# ---------- 连接 ----------

HOST, PORT = '127.0.0.1', 9003
SHIP_MODEL = 'DL-3026'

s = socket.create_connection((HOST, PORT), timeout=8)
s.settimeout(2)
try:
    print('ready:', s.recv(64))
except Exception:
    pass

# ---------- 初始位置 ----------

latitude  = 24.60
longitude = 118.33
course    = 90.0   # 航向（度）
speed     = 0.8    # 速度（米/秒）
battery   = 24.6   # 电池电压（V）
WATER_STATES = ['normal', 'sampling', 'lifting', 'recovering', 'abnormal']

packet_count = 0
while True:
    # 模拟简单运动：纬度上下、经度左右
    latitude  += speed * 0.00001 * (1 - 2 * (packet_count % 2))
    longitude += speed * 0.00001 * (1 - 2 * ((packet_count // 20) % 2))
    course     = (course + 2) % 360

    # 速度在 0.3 ~ 1.5 m/s 之间缓慢波动
    speed = 0.9 + 0.6 * __import__('math').sin(packet_count * 0.1)
    speed = round(max(0.3, min(1.5, speed)), 1)

    # 电池电压缓慢下降，降至 22.0 V 后回到 25.2 V（模拟充电循环）
    battery -= 0.05
    if battery < 22.0:
        battery = 25.2
    battery = round(battery, 1)

    # 采水状态每 15 包循环切换一次
    water_ext = WATER_STATES[(packet_count // 15) % len(WATER_STATES)]

    # 使用真实 UTC 时间戳
    ts = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')

    # 协议字段顺序: data_id|timestamp|latitude|longitude|course|speed|battery_level|water_extraction
    payload_text = (
        f'{SHIP_MODEL}|{ts}|{latitude:.6f}|{longitude:.6f}'
        f'|{course:.0f}|{speed:.1f}|{battery}|{water_ext}'
    )
    payload = payload_text.encode('ascii')
    packet  = build_packet('B', packet_count, payload)

    s.sendall(packet)
    print(f'[{packet_count:04d}] {ts}  lat={latitude:.6f} lon={longitude:.6f}'
          f'  course={course:.0f}°  speed={speed:.1f}m/s  bat={battery}V  water={water_ext}')

    packet_count += 1
    time.sleep(1)