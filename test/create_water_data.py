#!/usr/bin/env python
"""创建水质测试数据"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seadrone.settings')
django.setup()

from accounts.models import WaterQualityData, NutrientData
from datetime import datetime

# 创建水质监测数据
water_data = [
    {
        "ship_model": "DL-3026",
        "temperature": 22.5,
        "ph": 7.2,
        "chlorophyll": 15.3,
        "salinity": 32.1,
        "dissolved_oxygen": 8.2,
        "conductivity": 450,
        "turbidity": 2.5,
        "algae": 850,
        "warning_code": "正常",
        "connection_status": "在线"
    },
    {
        "ship_model": "DL-3022",
        "temperature": 21.8,
        "ph": 7.1,
        "chlorophyll": 12.8,
        "salinity": 31.9,
        "dissolved_oxygen": 8.5,
        "conductivity": 455,
        "turbidity": 2.2,
        "algae": 650,
        "warning_code": "正常",
        "connection_status": "在线"
    },
    {
        "ship_model": "DL-3020",
        "temperature": 23.2,
        "ph": 7.3,
        "chlorophyll": 18.5,
        "salinity": 32.3,
        "dissolved_oxygen": 7.9,
        "conductivity": 440,
        "turbidity": 3.8,
        "algae": 1200,
        "warning_code": "警告",
        "connection_status": "在线"
    },
    {
        "ship_model": "DL-3018",
        "temperature": 22.1,
        "ph": 7.0,
        "chlorophyll": 14.2,
        "salinity": 31.8,
        "dissolved_oxygen": 8.3,
        "conductivity": 460,
        "turbidity": 2.8,
        "algae": 950,
        "warning_code": "正常",
        "connection_status": "在线"
    },
    {
        "ship_model": "DL-3016",
        "temperature": 20.5,
        "ph": 6.9,
        "chlorophyll": 11.5,
        "salinity": 31.5,
        "dissolved_oxygen": 8.7,
        "conductivity": 445,
        "turbidity": 2.0,
        "algae": 500,
        "warning_code": "正常",
        "connection_status": "在线"
    }
]

for data in water_data:
    WaterQualityData.objects.create(**data)

print(f"✓ 创建了 {len(water_data)} 条水质数据")

# 创建营养盐数据
now = datetime.now()
nutrient_data = [
    {
        "ship_model": "DL-3026",
        "phosphate": 0.45,
        "phosphate_time": now,
        "ammonia": 0.28,
        "ammonia_time": now,
        "nitrate": 1.52,
        "nitrate_time": now,
        "nitrite": 0.08,
        "nitrite_time": now,
        "error_code1": "00",
        "error_code2": "00",
        "instrument_status": "正常",
        "connection_status": "在线"
    },
    {
        "ship_model": "DL-3022",
        "phosphate": 0.38,
        "phosphate_time": now,
        "ammonia": 0.22,
        "ammonia_time": now,
        "nitrate": 1.35,
        "nitrate_time": now,
        "nitrite": 0.06,
        "nitrite_time": now,
        "error_code1": "00",
        "error_code2": "00",
        "instrument_status": "正常",
        "connection_status": "在线"
    },
    {
        "ship_model": "DL-3020",
        "phosphate": 0.58,
        "phosphate_time": now,
        "ammonia": 0.42,
        "ammonia_time": now,
        "nitrate": 1.78,
        "nitrate_time": now,
        "nitrite": 0.12,
        "nitrite_time": now,
        "error_code1": "00",
        "error_code2": "00",
        "instrument_status": "正常",
        "connection_status": "在线"
    },
    {
        "ship_model": "DL-3018",
        "phosphate": 0.42,
        "phosphate_time": now,
        "ammonia": 0.25,
        "ammonia_time": now,
        "nitrate": 1.48,
        "nitrate_time": now,
        "nitrite": 0.07,
        "nitrite_time": now,
        "error_code1": "00",
        "error_code2": "00",
        "instrument_status": "正常",
        "connection_status": "在线"
    },
    {
        "ship_model": "DL-3016",
        "phosphate": 0.32,
        "phosphate_time": now,
        "ammonia": 0.18,
        "ammonia_time": now,
        "nitrate": 1.22,
        "nitrate_time": now,
        "nitrite": 0.05,
        "nitrite_time": now,
        "error_code1": "00",
        "error_code2": "00",
        "instrument_status": "正常",
        "connection_status": "在线"
    }
]

for data in nutrient_data:
    NutrientData.objects.create(**data)

print(f"✓ 创建了 {len(nutrient_data)} 条营养盐数据")
print("\n水质数据初始化完成！")
