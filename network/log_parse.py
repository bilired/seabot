import re
from datetime import datetime
import os

import re
from datetime import datetime

from mysqls import upsert_data_pooled
from parse import parse_0_data, parse_W_data, parse_Y_data, parse_B_data, parse_packets


def toTimestamp(time_str):
    import time
    time_struct = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(time_struct))
    return timestamp

def parse_log(line):
    """
    从形如 "[aaa] - bbb 收到原始数据：ccc" 的字符串中提取三个部分的内容
    
    参数:
        text (str): 输入的文本字符串
    
    返回:
        tuple: 包含三个部分内容的元组 (aaa, bbb, ccc)
    """
    # 使用正则表达式匹配模式
    pattern = r'\[(.*?)\]\s*-\s*(.*?)\s*收到原始数据：(.*)'
    match = re.match(pattern, line)
    
    if match:
        # 返回匹配到的三个组
        return match.group(1), match.group(2), match.group(3)
    else:
        # 如果没有匹配到，返回三个空字符串
        return None,None,None

def parse_log_file(file_path):
    """解析日志文件"""
    parsed_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parsed_line = parse_log(line)
                if parsed_line[0]:
                    parsed_data.append(parsed_line)
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在")
    except Exception as e:
        print(f"读取文件时出错: {e}")
    return parsed_data

def main():
    # 假设日志文件名为 log.txt
    log_file = 'ship_python_server_2025-07-11_161502_log.log'
    
    # 检查文件是否存在
    if not os.path.exists(log_file):
        print(f"错误：当前目录下未找到 {log_file} 文件")
        return
    
    # 解析日志文件
    logs = parse_log_file(log_file)

    vis = {}
    parseLogs = []

    print(len(logs))
    for l in logs:
        # if(vis.get(l[2],None)):
        #     continue
        # vis[l[2]]=True
        try:
            dd,other = parse_packets(bytes.fromhex(l[2]))
            # print(l)
            for d in  dd:
                # if d['type']=="W":
                #     print(l[1],d["str_data"])
                #     print(parse_W_data(l[1],d["str_data"]))
                    
                #     result = upsert_data_pooled(
                #         "znhyhj_device_water_quality",
                #         [],
                #         parse_W_data(l[1],d["str_data"])
                #     )
                #     print(f"单条操作结果: 影响{result}行")

                # if d['type']=="Y" or d['type']=="@":
                #     print(l[0],l[1],l[2],d["str_data"])
                #     tmp = parse_Y_data(l[1],d["str_data"])
                #     tmp['timestamp']=toTimestamp(l[0])
                #     print(tmp)
                #     result = upsert_data_pooled(
                #         "znhyhj_device_nutrient_data",
                #         [],
                #         tmp
                #     )
                #     print(f"单条操作结果: 影响{result}行")

                # if d['type']=="0":
                #     print(l[0],l[1],l[2],d["str_data"])
                #     tmp = parse_0_data(l[1],d["str_data"])
                #     tmp['timestamp']=toTimestamp(l[0])
                #     print(tmp)
                #     result = upsert_data_pooled(
                #         "znhyhj_device_depth_data",
                #         [],
                #         tmp
                #     )
                #     print(f"单条操作结果: 影响{result}行")


                if d['type']=="B":
                    print(l[0],l[1],l[2],d["str_data"])
                    tmp = parse_B_data(str(int(l[1])-1),d["str_data"])
                    tmp['timestamp']=toTimestamp(l[0])
                    print(tmp)
                    result = upsert_data_pooled(
                        "znhyhj_device_remote_control",
                        [],
                        tmp
                    )
                    print(f"单条操作结果: 影响{result}行")
                parseLogs.append(d)
        except ValueError as e:
            # if(l[2].startswith("2440")):
            #     print(l)
            #     print(e)
            print(e)
            None
        finally:
            None

    vis = {}
    for v in parseLogs:
        vis[v['type']]=vis.get(v['type'],0)+1
    print(vis)
    # for i in parseLogs[0:100]:
    #     if i['type']=="1":
    #         print(i)
            
            
if __name__ == "__main__":
    main()

