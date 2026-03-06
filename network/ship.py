import json
import socket
import threading
# import mysql.connector
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

import logging

from mysqls import upsert_data_pooled
from parse import parse_0_data, parse_D_data, parse_W_data, parse_Y_data, parse_B_data, parse_packet, parse_packets
# 配置日志格式（包含时间戳）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='[%Y-%m-%d %H:%M:%S]'
)


HOST = '0.0.0.0'  # 监听所有网络接口
HTTP_PORT = 9006
PORT_START = 9001        # 服务端口号
SHIP_COUNT = 2
clients = {}

import struct
def generate_packet(type,direction_code):
    """
    生成推进器控制指令的二进制报文
    :param direction_code: 方向代码 (402:上, 404:下, 405:左, 407:右)
    :return: 完整的二进制报文
    """
    # 定义包头结构
    class WXT_Packet_Header:
        def __init__(self):
            self.mark = b'$'  # 0x24
            self.mark1 = b'@'  # 0x40
            self.type = type   # 控制指令类型
            self.msg_id = 0    # 未使用，默认为0
            self.padlen = 4    # 数据长度(方向代码为4字节)
    
    # 创建包头
    header = WXT_Packet_Header()
    
    # 准备发送缓冲区
    send_buff = bytearray()
    
    # 添加包头
    send_buff += header.mark
    send_buff += header.mark1
    send_buff += header.type.ljust(2, b'\x00')   # 2字节，右补零
    send_buff += struct.pack('i', header.msg_id)  # 4字节
    send_buff += struct.pack('i', header.padlen+2) # 4字节
    # 添加方向数据 (4字节)
    send_buff += struct.pack('i', direction_code)
    
    return bytes(send_buff)


def generate_thruster_control_packet(direction_code):
    return generate_packet(b'S',direction_code)

def generate_camera_control_packet(direction_code):
    return generate_packet(b'8',direction_code)

actions = {
    'up':     generate_thruster_control_packet(402),
    'down':   generate_thruster_control_packet(404) ,
    'left':   generate_thruster_control_packet(405) ,
    'right':  generate_thruster_control_packet(407),
    'camera_normal':   generate_camera_control_packet(327) , # 文档是错的，实习生抄反了
    'camera_night':  generate_camera_control_packet(326),
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
    logging.info(remainder)
    return remainder.to_bytes(2, byteorder='big', signed=False)

# oridata = actions['camera_night']
# print(parse_packet(oridata+calc_crc(0,oridata,len(oridata))))
# 0/0

def handle_client_connection(client,port):
    global clients
    """处理客户端TCP连接
    参数：
        client_socket : socket - 客户端套接字对象
    """
    try:
        # 发送准备就绪信号
        client.send(b'Ready')
        logging.info("已发送准备就绪信号")
        
        while True:
            # 接收TCP数据（最大1024字节）
            data = client.recv(1024)
            if not data:
                break  # 连接已关闭

            logging.info(f"{port} 收到原始数据：{data.hex()}")
            
            if data.hex() == '00' or data.hex().startswith('2440'):
                if data.hex() == '00':
                    logging.info(f"{port} 收到心跳包")
                    tmp = {
                        "ship_id":str(port),
                        "timestamp_bucket":int(int(datetime.now(timezone.utc).timestamp())/300)*300,
                        "timestamp_last":int(datetime.now(timezone.utc).timestamp()),
                    }
                    result = upsert_data_pooled(
                        "znhyhj_device_hartbeat_bucket_hsitory", ["ship_id","timestamp_bucket"], tmp
                    )
                    tmp = {
                        "ship_port":str(port),
                        "control_port": str(port+1),
                        "last_heartbeat":tmp['timestamp_last']
                    }
                    result = upsert_data_pooled(
                        "znhyhj_device_management_bar", ["control_port","ship_port"], tmp
                    )

                else :
                    clients[port] = client
                    packs,_ = parse_packets(data)
                    
                    # 如果是遥控器
                    
                    try:
                        needSend = False
                        for d in packs:
                            print(d)
                            if d['type']!="B":
                                needSend = True
                            else:
                                result = upsert_data_pooled(
                                    "znhyhj_device_remote_control", [], parse_B_data(port-1,d["str_data"])
                                )

                        if needSend and port%2==0:
                            other_clinet = clients.get(port-1)
                            if other_clinet is not None:
                                other_clinet.send(data)
                            
                    except Exception as e:
                        logging.info(f"{port} 未知错误：{data.hex()}")
                        logging.info(f"{port} 未知错误：{e}")
                        import traceback
                        # 打印原始异常堆栈
                        tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
                        tb_text = ''.join(tb_lines)
                        logging.error(f"原始错误堆栈：\n{tb_text}")
                        None
                    
                    for d in  packs:
                        try:
                            # logging.info(f"{port} 接收到数据包 {json.dumps(d,ensure_ascii=False)}")
                            print(d)
                            if d['type']=="W":
                                result = upsert_data_pooled(
                                    "znhyhj_device_water_quality", [], parse_W_data(port,d["str_data"])
                                )

                            if d['type']=="Y" or d['type']=="@":
                                tmp = parse_Y_data(port,d["str_data"])
                                result = upsert_data_pooled(
                                    "znhyhj_device_nutrient_data", [], tmp
                                )

                            if d['type']=="D":
                                tmp = parse_D_data(port,d["str_data"])
                                result = upsert_data_pooled(
                                    "znhyhj_device_depth_data", [], tmp
                                )
                                
                            if d['type']=="0":
                                tmp = parse_0_data(port,d["str_data"])
                                result = upsert_data_pooled(
                                    "znhyhj_device_depth_data", [], tmp
                                )
                                
                        except ValueError as e:
                            logging.info(f"{port} 收到错误数据：{data.hex()}")
                            logging.info(f"{port} 未知错误：{e}")
                            import traceback
                            # 打印原始异常堆栈
                            tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
                            tb_text = ''.join(tb_lines)
                            logging.error(f"原始错误堆栈：\n{tb_text}")
                            None
                        except Exception as e:
                            logging.info(f"{port} 未知错误：{data.hex()}")
                            logging.info(f"{port} 未知错误：{e}")
                            import traceback
                            # 打印原始异常堆栈
                            tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
                            tb_text = ''.join(tb_lines)
                            logging.error(f"原始错误堆栈：\n{tb_text}")
                            None



            
    except Exception as e:
        logging.info(f"连接处理异常：{str(e)}")
    finally:
        client.close()


    # HTTP请求处理器
class HTTPHandler(BaseHTTPRequestHandler):
    # 添加超时保护
    timeout = 5  # 秒（根据实际情况调整）

    def setup(self):
        # 每次请求单独设置超时
        self.request.settimeout(self.timeout)
        super().setup()

    def handle(self):
        try:
            super().handle()
        except socket.timeout:
            logging.warning("Request timed out, closing connection")
            self.close_connection = True
        except ConnectionResetError:
            logging.warning("Client connection reset")
            self.close_connection = True

    def do_OPTIONS(self):
        # 处理OPTIONS方法
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        # 处理GET请求
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(b'Hello World')
    def do_POST(self):
        global clients
        if self.path == '/shipAction' or self.path == '/shipAction/':
            
            # 从 body 读取二进制数据
            content_length = int(self.headers.get('Content-Length', 0))
            binary_data = self.rfile.read(content_length)       
            
             # 设置响应头
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

            # json
            try:
                data = json.loads(binary_data.decode('utf-8'))
                logging.info(f"收到控制命令：{data}")
                oridata = actions[data['cmd']]
                cmd =  oridata+calc_crc(0,oridata,len(oridata))
                ship_port = data['ship_port']
                control_port = data['control_port']
                logging.info(f"收到JSON数据：{data}")
            except Exception as e:
                logging.info(f"JSON解析错误：{str(e)}")
                return self.wfile.write(json.dumps({
                        "status":"解析错误:格式错误",
                        "data":'''{"cmd":"up","ship_port":9001,"control_port":9002}''',
                        "supportCmd":[v for v in actions.keys()]
                    }).encode())
            
            success = 0

            try:
                clients[control_port].send(cmd)
                success|=1
                logging.info(f'发送{cmd.hex()}到{control_port}成功:')
            except Exception as e:
                logging.info(f'发送{cmd.hex()}到{control_port}失败')
                
            try:
                clients[ship_port].send(cmd)
                success|=2
                logging.info(f'发送{cmd}到{ship_port}成功')
            except Exception as e:
                logging.info(f'发送{cmd}到{ship_port}失败')

            dics = {
                1: "已成功发送到遥控器",
                2: "已成功发送到无人船",
                3: "已成功发送到无人船和遥控器",
                0: "设备未在线"
            }
            return self.wfile.write(json.dumps({
                "status":"发送错误" if success == 0 else "发送成功",
                "data":dics[success]
            }).encode())
            
            # return self.wfile.write(json.dumps({
            #         "status":"发送成功",
            #         "data":'''OK'''
            #     }).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
            
def run_http_server():
    """带异常处理和自动重启的HTTP服务"""
    retry_count = 1
    RETRY_DELAY = 10  # 重试间隔时间（秒）
    while retry_count:
        try:
            logging.info(f"🔄 启动HTTP服务 ")
            http_server = HTTPServer((HOST, HTTP_PORT), HTTPHandler)
            logging.info(f"✅ HTTP服务已就绪 {HOST}:{HTTP_PORT}")
            http_server.serve_forever()
            
        except Exception as e:
            logging.error(f" 服务异常: {str(e)}")
            logging.warning(f" 正常重试第{retry_count}次 ⏳ {RETRY_DELAY}秒后尝试重启...")
            import time
            time.sleep(RETRY_DELAY)
            retry_count += 1
            
        finally:
            if hasattr(http_server, 'server_close'):
                http_server.server_close()

def start_http_server():
    http_thread = threading.Thread(target=run_http_server)
    http_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
    http_thread.start()


def start_server(host,port):
    global clients
    """启动TCP监听服务"""
    # 创建TCP套接字
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置端口重用选项
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定地址和端口
    server.bind((host, port))
    # 开始监听（最大排队连接数2）
    server.listen(2)
    logging.info(f"服务已启动，监听地址：{host}:{port}")

    while True:
        # 接受客户端连接
        client, addr = server.accept()
        logging.info(f"新的客户端连接：{addr} ,端口号为：{port}")
        # 为每个客户端创建独立线程
        thread = threading.Thread(target=handle_client_connection, args=(client,port))
        thread.start()

if __name__ == "__main__":
    start_http_server()
    for port in range(PORT_START, PORT_START + SHIP_COUNT*2):
        thread = threading.Thread(target=start_server, args=(HOST,port))
        # thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        thread.start()