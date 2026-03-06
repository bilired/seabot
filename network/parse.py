
import struct


def parse_packets(data):
    """
    解析可能包含多个包的二进制数据流（处理粘包情况）
    :param data: 二进制数据流
    :return: 解析出的包列表和剩余数据
    """
    packets = []
    index = 0
    total_length = len(data)
    
    while index + 12 <= total_length:
        # 检查包头标记
        if data[index:index+2] != b'$@':
            index += 1
            continue
        
        # 解析控制类型（2字节，右补零）
        type_bytes = data[index+2:index+4]
        try:
            control_type = type_bytes.rstrip(b'\x00').decode('ascii')
        except UnicodeDecodeError:
            index += 1
            continue
        
        # 解析消息ID（4字节小端）
        msg_id_bytes = data[index+4:index+8]
        if len(msg_id_bytes) < 4:
            break
        msg_id = struct.unpack('<i', msg_id_bytes)[0]
        
        # 解析数据长度（4字节小端）
        padlen_bytes = data[index+8:index+12]
        if len(padlen_bytes) < 4:
            break
        padlen = struct.unpack('<i', padlen_bytes)[0]
        data_length = padlen - 2
        
        # 检查总长度是否足够
        packet_length = 12 + padlen
        if index + packet_length > total_length:
            break  # 数据不足，等待更多数据
        
        # 提取完整包数据
        packet_data = data[index:index+packet_length]
        index += packet_length  # 移动索引到下一个包
        
        try:
            # 验证CRC
            cal_crc_val = calc_crc(0, packet_data, len(packet_data)-2).hex()
            current_crc = packet_data[-2:].hex()
            
            # 提取数据内容（不含CRC）
            content_data = packet_data[12:12+data_length]
            
            # 尝试解码为字符串
            try:
                str_data = content_data.decode('ascii', errors='ignore')
            except:
                str_data = ""
            
            # 尝试解析为整数
            int_data = None
            if len(content_data) >= 4:
                try:
                    int_data = struct.unpack('<i', content_data[0:4])[0]
                except:
                    pass
            
            packet = {
                'type': control_type,
                'msg_id': msg_id,
                'data_length': data_length,
                'data': content_data,
                'cal_crc': cal_crc_val,
                'result_crc': 1 if cal_crc_val == current_crc else 0,
                'hex_data': content_data.hex(),
                'str_data': str_data,
                'int_data': int_data,
            }
            packets.append(packet)
        except Exception as e:
            # 解析失败，跳过错误继续处理后续数据
            continue
    
    # 返回解析出的包列表和剩余未解析数据
    return packets, data[index:]

def parse_packet(data):
    """
    解析推进器控制指令的二进制报文
    :param data: 二进制报文数据
    :return: 解析后的字段字典
    """
    # 检查最小长度
    if len(data) < 12:
        raise ValueError("数据包长度不足，至少需要12字节")
    
    # 验证包头标记
    if data[0:2] != b'$@':
        raise ValueError("无效的包头标记，应为 b'$@'")
    
    # 解析控制类型（2字节，右补零）
    type_bytes = data[2:4]
    control_type = type_bytes.rstrip(b'\x00').decode('ascii')
    
    # 解析消息ID（4字节小端）
    msg_id = struct.unpack('<i', data[4:8])[0]
    
    # 解析数据长度（4字节小端，实际长度=padlen-2）
    padlen = struct.unpack('<i', data[8:12])[0]
    data_length = padlen - 2

    cal_crc = calc_crc(0, data, len(data)-2).hex() 
    current_crc = data[-2:].hex()
    
    
    # 验证数据包总长度
    if len(data) != 14 + data_length:
        raise ValueError(f"数据长度不匹配，期望 {14+data_length} 字节，实际 {len(data)} 字节")
    
    # 解析方向代码（动态长度小端有符号整数）
    data = data[12:12+data_length]

    return {
        'type': control_type,
        'msg_id': msg_id,
        'data_length': padlen-2,  # 实际数据长度
        'data': data,
        'cal_crc': cal_crc,
        'result_crc':  1 if cal_crc == current_crc else 0,
        'hex_data': data.hex(),
        'str_data': data.decode('ascii', errors='ignore'),  # 尝试解码为字符串,失败则返回空字符串
        'int_data': int.from_bytes(data[0:4], byteorder='little', signed=True), #这里假设传进来的是4字节整数，因为如果不是4字节整数，数据包的长度也不对
    }

def calc_crc(crc: int, buf: bytes, length:int ) -> int:
    remainder = crc & 0xFFFF  # 强制转为16位无符号
    top_bit = 0x8000
    
    for i in range(length):
        # 将字节转为无符号整型 (Python中bytes直接返回0-255)
        byte = buf[i]
        
        acc = (byte << 8) & 0xFF00  # 左移8位并确保在16位范围内
        remainder ^= acc
        remainder &= 0xFFFF  # 保持16位
        
        for _ in range(8):    # 处理每个bit
            if remainder & top_bit:
                remainder = ((remainder << 1) ^ 0x8005) & 0xFFFF
            else:
                remainder = (remainder << 1) & 0xFFFF
                
    remainder =  remainder ^ 0x0000  # 最终异或值（此处不影响结果）
    return remainder.to_bytes(2, byteorder='big', signed=False)



def parse_W_data(ship_id:str,input_str:str):
    from datetime import datetime, timezone
    """
    解析输入字符串并生成对应JSON
    :param ship_id: 船只唯一标识符
    :param input_str: 输入字符串 (格式: 20250611105905|0000|29.26|7.10|0.003|0.000|25.110|0.373|0.000)
    :return: JSON字符串
    """
    # 分割输入字符串
    parts = input_str.strip().split('|')
    if len(parts) != 10:
        raise ValueError(f"无效的输入格式，应有10个字段，实际收到 {len(parts)} 个")

    # 解析并转换数据
    raw_timestamp = parts[0]
    warn_code = parts[1]
    
    # 转换时间戳 (YYYYMMDDHHMMSS -> ISO格式)
    dt = datetime.strptime(raw_timestamp, "%Y%m%d%H%M%S")
    # 设置为UTC时间并获取Unix时间戳
    timestamp_seconds = int(dt.timestamp()) #.replace(tzinfo=timezone.utc)
    
    # 数值转换并处理无效值
    data_map = {
        'temperature': float(parts[2]) if parts[2] != '' else None,
        'pH': float(parts[3]) if parts[3] != '' else None,
        'conductivity': float(parts[4]) if parts[4] != '' else None,
        'salinity': float(parts[5]) if parts[5] != '' else None,
        'turbidity': float(parts[6]) if parts[6] != '' else None,
        'chlorophyll': float(parts[7]) if parts[7] != '' else None,
        'blue_green': float(parts[8]) if parts[8] != '' else None,
        "dissolved_oxygen": float(parts[9]) if parts[9] != '' else None,
    }
    
    # 构建最终数据结构 (不含输入中不存在的dissolved_oxygen)
    result = {
        "ship_id": str(ship_id),
        "timestamp": timestamp_seconds,
        "status": 1,  # 默认设置为已连接
        "warn": warn_code,
        **data_map
    }
    return result 
    # return json.dumps(result, ensure_ascii=False)

def parse_Y_data(ship_id: str, input_str: str):
    from datetime import datetime, timezone
    """
    解析营养盐数据输入字符串并生成对应JSON
    :param ship_id: 船只唯一标识符
    :param input_str: 输入字符串 (格式: Y0.483|20250401143208|0.573|20250401143107|0.202|20250401143007|0.491|20250401142906|0|0|3|0|3|2:)
    :return: JSON对象
    """
    # 预处理输入字符串
    cleaned_str = input_str.strip().rstrip(':')
    parts = cleaned_str.split('|')
    
    # 验证字段数量
    if len(parts) != 14:
        raise ValueError(f"无效的输入格式，应有14个字段，实际收到 {len(parts)} 个")
    
    # 获取当前系统时间作为主时间戳（INT类型）
    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    
    # 处理首个字段的特殊字符 'Y'
    phosphate_value = parts[0].lstrip('Y')
    
    # 构建并返回JSON结构
    return {
        "ship_id": str(ship_id),
        "timestamp": current_timestamp,  # INT类型时间戳
        "status": 1,
        "CH1datetime": parts[1] if parts[1] else None,    # 磷酸盐获取时间
        "phosphate": float(phosphate_value) if phosphate_value != '' else None,
        "CH2datetime": parts[3] if parts[3] else None,    # 氨氮获取时间
        "ammonia": float(parts[2]) if parts[2] != '' else None,
        "CH3datetime": parts[5] if parts[5] else None,    # 硝酸盐获取时间
        "nitrate": float(parts[4]) if parts[4] != '' else None,
        "CH4datetime": parts[7] if parts[7] else None,    # 亚硝酸盐获取时间
        "sub_nitrate": float(parts[6]) if parts[6] != '' else None,
        "error_code_nutrient1": int(parts[8]) if parts[8] != '' else 0,
        "error_code_nutrient2": int(parts[9]) if parts[9] != '' else 0,
        "nutrient_state": int(parts[10]) if parts[10] != '' else 0
    }

def parse_D_data(ship_id: str, input_str: str):
    from datetime import datetime, timezone
    """
    解析营养盐数据输入字符串并生成对应JSON
    :param ship_id: 船只唯一标识符
    :param input_str: 输入字符串 (格式: 2.00|0.00)
    :return: JSON对象
    """
    # 预处理输入字符串
    cleaned_str = input_str.strip().rstrip(':')
    parts = cleaned_str.split('|')
    
    # 验证字段数量
    if len(parts) != 2:
        raise ValueError(f"无效的输入格式，应有2个字段，实际收到 {len(parts)} 个")
    
    # 获取当前系统时间作为主时间戳（INT类型）
    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    
    
    # 构建并返回JSON结构
    return {
        "ship_id": str(ship_id),
        "timestamp": current_timestamp,  # INT类型时间戳
        "depth": float(parts[0]) if parts[0] != '' else None, 
    }
def parse_B_data(ship_id: str, input_str: str):
    from datetime import datetime, timezone
    """
    解析船只数据输入字符串并生成对应JSON
    :param ship_id: 船只唯一标识符
    :param input_str: 输入字符串 (格式: DL-3026|20250711144400|1|24.6668664|118.2232124|0.00|0.05|46.03)
    :return: JSON对象
    """
    # 预处理输入字符串
    cleaned_str = input_str.strip()
    parts = cleaned_str.split('|')
    
    # 验证字段数量 (基于示例数据应有8个字段)
    if len(parts) != 8:
        raise ValueError(f"无效的输入格式，应有8个字段，实际收到 {len(parts)} 个")
    
    # 获取当前系统时间作为主时间戳（INT类型）
    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    
    # 构建并返回JSON结构
    return {
        "ship_id": str(ship_id),
        "data_id": parts[0],                 # 数据唯一标识 (String)
        "timestamp": current_timestamp,  # INT类型时间戳
        "boat_timestamp": parts[1],               # 转换后的UNIX时间戳 (INT)
        "boat_latitude": parts[3],            # 纬度 (String)
        "boat_longitude": parts[4],           # 经度 (String)
        "boat_direction": float(parts[6]) if parts[6] != '' else None,  # 航向 (Float)
        "boat_speed": float(parts[5]) if parts[5] != '' else None,      # 速度 (Float)
        "battery_voltage": float(parts[7]) if parts[7] != '' else None, # 电池电量 (Float)
    }
def parse_0_data(ship_id: str, input_str: str):
    from datetime import datetime, timezone
    """
    解析营养盐数据输入字符串并生成对应JSON
    :param ship_id: 船只唯一标识符
    :param input_str: 输入字符串 (格式: 2.00|0.00)
    :return: JSON对象
    """
    # 预处理输入字符串
    cleaned_str = input_str.strip().rstrip(':')
    parts = cleaned_str.split('|')
    
    # 验证字段数量
    if len(parts) != 7:
        raise ValueError(f"无效的输入格式，应有2个字段，实际收到 {len(parts)} 个")
    
    # 获取当前系统时间作为主时间戳（INT类型）
    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    
    
    # 构建并返回JSON结构
    return {
        "ship_id": str(ship_id),
        "timestamp": current_timestamp,  # INT类型时间戳
        "depth": float(parts[0]) if parts[0] != '' else None, 
        "RTKlatitude": float(parts[1]) if parts[1] != '' else None, 
        "RTKlatitude_direction": (parts[2]) if parts[2] != '' else None, 
        "RTKlongitude": float(parts[3]) if parts[3] != '' else None, 
        "RTKlongitude_direction": (parts[4]) if parts[4] != '' else None, 
        "temperature": float(parts[5]) if parts[5] != '' else None, 
        "RTKelevation": float(parts[6]) if parts[6] != '' else None, 
    }

if __name__ == "__main__":
    # 生成测试数据包
    generated_data = bytes.fromhex('244030000000000052000000302e303000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000bb05')
    generated_data = bytes.fromhex('24405700000000003f00000032303235303433303030303632327c303030307c32322e37317c352e33397c302e3030357c302e3030307c32382e3032337c302e3035307c302e303030ba1a')
    generated_data = bytes.fromhex('244053000000000006000000970100000632')
    generated_data = bytes.fromhex('24404000000000006300000059302e3438337c32303235303430313134333230387c302e3537337c32303235303430313134333130377c302e3230327c32303235303430313134333030377c302e3439317c32303235303430313134323930367c307c307c337c307c337c323a2330')
    generated_data = bytes.fromhex('24405700000000003f00000032303235303631303134353530377c303030307c33332e38317c362e37337c302e3030357c302e3030307c32342e3932307c302e3034347c302e30303031dc')
    generated_data = bytes.fromhex('24405700000000003f00000032303235303631303134353435367c303030307c33332e38317c362e37347c302e3030347c302e3030307c32342e3933387c302e3031357c302e3030306b2b')
    # 解析数据包
    # parse_packets

    # generated_data = bytes.fromhex('24 40 59 00 00 00 00 58 00 00 00 30 2E 34 38 33 7C 32 30 32 35 30 34 30 31 31 34 33 32 30 38 7C 30 2E 35 37 33 7C 32 30 32 35 30 34 30 31 31 34 33 31 30 37 7C 30 2E 32 30 32 7C 32 30 32 35 30 34 30 31 31 34 33 30 30 37 7C 30 2E 34 39 31 7C 32 30 32 35 30 34 30 31 31 34 32 39 30 36 7C 30 7C 30 7C 33 7C 30 7C 33 7C 32 3A B7'.replace(" ",""))
    
    data = '244042000000000041000000444c2d333032367c32303235303731313134343430307c317c32342e363636383636347c3131382e323233323132347c302e30307c302e30357c34362e30338171'.replace(" ","")
    data = bytes.fromhex(data)
    data,_ = parse_packets(data)
    print(data)
    a = parse_B_data("3000",data[0]['str_data'])
    print(data)
    print(a)

    # a = parse_W_data("3000",'20250611105854|0000|29.26|7.10|0.004|0.000|25.104|0.436|0.000')
    # print(a)
    # 打印解析结果
    # print(f"控制类型: {parsed['type']}")
    # print(f"消息ID: {parsed['msg_id']}")
    # print(f"数据长度字段: {parsed['data_length']}")
    # print(f"数据: {parsed['data']}")
    # print(f"数据: {parsed['str_data']}")
    # print(f"数据: {parsed['int_data']}")
    # print(f"校验码: {parsed['cal_crc']}")
    # print(f"校验结果: {parsed['result_crc']}")