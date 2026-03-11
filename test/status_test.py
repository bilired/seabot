import socket, time, struct

def calc_crc(buf: bytes) -> bytes:
    remainder = 0
    top_bit = 0x8000
    for b in buf:
        remainder ^= (b << 8) & 0xFF00
        remainder &= 0xFFFF
        for _ in range(8):
            if remainder & top_bit:
                remainder = ((remainder << 1) ^ 0x8005) & 0xFFFF
            else:
                remainder = (remainder << 1) & 0xFFFF
    return remainder.to_bytes(2, 'big')

host, port = "127.0.0.1", 9001 #8.130.132.91

s = socket.create_connection((host, port), timeout=8)
s.settimeout(2)
try:
    print("ready:", s.recv(64))
except Exception:
    pass

# 初始位置和运动参数
latitude = 30.512345
longitude = 114.412345
direction = 90
speed = 0.8

# 模拟船体不停运动
packet_count = 0
while True:
    # 动态更新位置（模拟船体运动）
    # 北偏移 (direction=0) 或 东偏移 (direction=90)
    # 每次更新经纬度
    lat_offset = speed * 0.00001 * (1 - 2 * (packet_count % 2))  # 上下运动
    lon_offset = speed * 0.00001 * (1 - 2 * ((packet_count // 20) % 2))  # 左右运动
    
    latitude += lat_offset
    longitude += lon_offset
    
    # 更新航向（缓慢旋转）
    direction = (direction + 2) % 360
    
    # 构造动态B类型数据包
    payload_text = f"DL-3022|20260311{(packet_count % 86400):06d}|normal|{latitude:.6f}|{longitude:.6f}|{speed:.1f}|{direction:.0f}|24.6"
    payload = payload_text.encode("ascii")
    
    header = b"$@" + b"B\x00" + struct.pack("<i", packet_count) + struct.pack("<i", len(payload) + 2)
    packet = header + payload
    packet += calc_crc(packet)
    
    s.sendall(packet)
    print(f"[{packet_count:04d}] 发送: 纬度={latitude:.6f}, 经度={longitude:.6f}, 航向={direction:.0f}°, 速度={speed:.1f}节")
    
    packet_count += 1
    time.sleep(1)  # 每秒发送一个更新包