#!/usr/bin/env python3
"""
创建示例无人船设备
"""
import os
import sys
import django

# 添加 seadrone 项目路径
sys.path.insert(0, '/Users/hanksgao/Desktop/seabot/back-end/seadrone')
os.chdir('/Users/hanksgao/Desktop/seabot/back-end/seadrone')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seadrone.settings')
django.setup()

from accounts.models import DroneDevice

# 清空现有设备（可选）
# DroneDevice.objects.all().delete()

# 创建两个示例设备
devices = [
    {
        'ship_type': '双体',
        'length': 255,
        'model': 'DL-3026',
        'weight': 51,
        'functions': '图传、采样、营养盐监测',
        'status': 'offline',
        'max_speed': 14
    },
    {
        'ship_type': '双体',
        'length': 220,
        'model': 'DL-3022',
        'weight': 44,
        'functions': '图传、采样、多参数水质监测',
        'status': 'offline',
        'max_speed': 12
    }
]

for device_data in devices:
    device, created = DroneDevice.objects.get_or_create(
        model=device_data['model'],
        defaults=device_data
    )
    if created:
        print(f"✅ 创建设备: {device.model}")
    else:
        print(f"⏭️  设备已存在: {device.model}")

print("\n✨ 完成！设备列表：")
for device in DroneDevice.objects.all():
    print(f"  - {device.model} ({device.ship_type})")
