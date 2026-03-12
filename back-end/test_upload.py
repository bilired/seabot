#!/usr/bin/env python3
"""
测试数据上传API
模拟无人船向服务器上传传感器数据
"""

import requests
import random
import time
from datetime import datetime

# API配置
BASE_URL = "http://localhost:8000/api"
WATER_QUALITY_URL = f"{BASE_URL}/upload/water-quality/"
NUTRIENT_URL = f"{BASE_URL}/upload/nutrient/"

# 设备配置
SHIP_MODELS = ["DL-3026", "DL-3022", "DL-3018"]


def generate_water_quality_data(ship_model):
    """生成模拟的水质数据"""
    return {
        "ship_model": ship_model,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "warn": random.choice(["0", "0", "0", "1"]),
        "temperature": round(20 + random.uniform(-2, 8), 2),
        "pH": round(7 + random.uniform(-0.5, 0.5), 2),
        "chlorophyll": round(10 + random.uniform(0, 20), 2),
        "salinity": round(30 + random.uniform(-3, 5), 2),
        "dissolved_oxygen": round(6 + random.uniform(0, 3), 2),
        "conductivity": round(400 + random.uniform(-50, 150), 2),
        "turbidity": round(1 + random.uniform(0, 4), 2),
        "blue-green": round(500 + random.uniform(-200, 1500), 2)
    }


def generate_nutrient_data(ship_model):
    """生成模拟的营养盐数据"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {
        "data_id": ship_model,
        "timestamp": now,
        "status": random.choice([0, 1]),
        "ammonia_nitrogen": round(random.uniform(0.1, 0.8), 2),
        "ammonia_nitrogen_timestamp": now,
        "nitrate": round(random.uniform(0.5, 3.0), 2),
        "nitrate_timestamp": now,
        "sub_nitrate": round(random.uniform(0.01, 0.2), 2),
        "sub_nitrate_timestamp": now,
        "phosphates": round(random.uniform(0.1, 1.0), 2),
        "phosphates_timestamp": now,
        "warn": random.choice(["0", "0", "0", "1"]),
    }


def upload_water_quality(data):
    """上传水质数据"""
    try:
        response = requests.post(WATER_QUALITY_URL, json=data)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] 水质数据上传成功 - {data['ship_model']}")
            return True
        else:
            print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] 上传失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] 错误: {e}")
        return False


def upload_nutrient(data):
    """上传营养盐数据"""
    try:
        response = requests.post(NUTRIENT_URL, json=data)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] 营养盐数据上传成功 - {data['data_id']}")
            return True
        else:
            print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] 上传失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] 错误: {e}")
        return False


def test_single_upload():
    """测试单次上传"""
    print("=" * 60)
    print("测试单次数据上传")
    print("=" * 60)
    
    ship_model = SHIP_MODELS[0]
    
    # 上传水质数据
    water_data = generate_water_quality_data(ship_model)
    print(f"\n📤 上传水质数据: {water_data}")
    upload_water_quality(water_data)
    
    # 上传营养盐数据
    nutrient_data = generate_nutrient_data(ship_model)
    print(f"\n📤 上传营养盐数据: {nutrient_data}")
    upload_nutrient(nutrient_data)


def test_batch_upload(count=5):
    """测试批量上传"""
    print("\n" + "=" * 60)
    print(f"测试批量上传 ({count} 条数据)")
    print("=" * 60)
    
    success = 0
    failed = 0
    
    for i in range(count):
        ship_model = random.choice(SHIP_MODELS)
        
        # 随机上传水质或营养盐数据
        if random.random() > 0.5:
            data = generate_water_quality_data(ship_model)
            if upload_water_quality(data):
                success += 1
            else:
                failed += 1
        else:
            data = generate_nutrient_data(ship_model)
            if upload_nutrient(data):
                success += 1
            else:
                failed += 1
        
        time.sleep(0.5)  # 避免过快请求
    
    print(f"\n📊 统计: 成功 {success} 条, 失败 {failed} 条")


def test_continuous_upload(interval=10, duration=60):
    """测试持续上传（模拟真实设备）"""
    print("\n" + "=" * 60)
    print(f"测试持续上传 (间隔{interval}秒, 持续{duration}秒)")
    print("按 Ctrl+C 停止")
    print("=" * 60)
    
    start_time = time.time()
    count = 0
    
    try:
        while (time.time() - start_time) < duration:
            for ship_model in SHIP_MODELS:
                # 每个设备同时上传水质和营养盐数据
                water_data = generate_water_quality_data(ship_model)
                nutrient_data = generate_nutrient_data(ship_model)
                
                upload_water_quality(water_data)
                upload_nutrient(nutrient_data)
                
                count += 2
            
            print(f"\n⏳ 等待 {interval} 秒...")
            time.sleep(interval)
        
        print(f"\n✅ 完成! 总共上传了 {count} 条数据")
    
    except KeyboardInterrupt:
        print(f"\n\n⚠️  用户中断! 总共上传了 {count} 条数据")


def main():
    """主函数"""
    print("\n🚢 无人船数据上传测试工具")
    print("=" * 60)
    print("1. 单次上传测试")
    print("2. 批量上传测试 (5条)")
    print("3. 批量上传测试 (20条)")
    print("4. 持续上传测试 (10秒间隔, 60秒)")
    print("5. 持续上传测试 (自定义)")
    print("=" * 60)
    
    choice = input("\n请选择测试模式 (1-5): ").strip()
    
    if choice == "1":
        test_single_upload()
    elif choice == "2":
        test_batch_upload(5)
    elif choice == "3":
        test_batch_upload(20)
    elif choice == "4":
        test_continuous_upload(interval=10, duration=60)
    elif choice == "5":
        interval = int(input("上传间隔(秒): "))
        duration = int(input("持续时间(秒, 0=无限): "))
        if duration == 0:
            duration = float('inf')
        test_continuous_upload(interval, duration)
    else:
        print("❌ 无效的选择")


if __name__ == "__main__":
    main()
