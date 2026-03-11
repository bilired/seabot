#!/usr/bin/env python
"""
Create sample monitoring data for water quality and nutrients
"""
import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seadrone.settings')
django.setup()

from monitoring.models import WaterQualityData, NutrientData

# Clear existing data
WaterQualityData.objects.all().delete()
NutrientData.objects.all().delete()

# Create water quality data samples
print("Creating water quality data...")
now = timezone.now()

water_quality_samples = [
    {
        'ship_model': 'DL-3026',
        'temperature': 28.5,
        'ph': 8.1,
        'chlorophyll': 15.3,
        'salinity': 32.5,
        'dissolved_oxygen': 7.8,
        'conductivity': 45000,
        'turbidity': 1.2,
        'algae': 150,
        'warning_code': '正常',
        'connection_status': '在线',
    },
    {
        'ship_model': 'DL-3026',
        'temperature': 28.2,
        'ph': 8.0,
        'chlorophyll': 14.8,
        'salinity': 32.3,
        'dissolved_oxygen': 7.9,
        'conductivity': 44800,
        'turbidity': 1.1,
        'algae': 145,
        'warning_code': '正常',
        'connection_status': '在线',
    },
    {
        'ship_model': 'DL-3022',
        'temperature': 29.1,
        'ph': 8.2,
        'chlorophyll': 16.5,
        'salinity': 33.0,
        'dissolved_oxygen': 7.5,
        'conductivity': 45500,
        'turbidity': 1.5,
        'algae': 180,
        'warning_code': '正常',
        'connection_status': '在线',
    },
    {
        'ship_model': 'DL-3022',
        'temperature': 29.0,
        'ph': 8.1,
        'chlorophyll': 16.0,
        'salinity': 32.8,
        'dissolved_oxygen': 7.6,
        'conductivity': 45200,
        'turbidity': 1.4,
        'algae': 170,
        'warning_code': '正常',
        'connection_status': '在线',
    },
]

for sample in water_quality_samples:
    WaterQualityData.objects.create(**sample)
    print(f"Created water quality data for {sample['ship_model']}")

# Create nutrient data samples
print("\nCreating nutrient data...")

nutrient_samples = [
    {
        'ship_model': 'DL-3026',
        'phosphate': 0.85,
        'phosphate_time': now,
        'ammonia': 0.15,
        'ammonia_time': now,
        'nitrate': 2.3,
        'nitrate_time': now,
        'nitrite': 0.08,
        'nitrite_time': now,
        'error_code1': '00',
        'error_code2': '00',
        'instrument_status': '正常',
        'connection_status': '在线',
    },
    {
        'ship_model': 'DL-3026',
        'phosphate': 0.82,
        'phosphate_time': now - timedelta(hours=1),
        'ammonia': 0.14,
        'ammonia_time': now - timedelta(hours=1),
        'nitrate': 2.2,
        'nitrate_time': now - timedelta(hours=1),
        'nitrite': 0.07,
        'nitrite_time': now - timedelta(hours=1),
        'error_code1': '00',
        'error_code2': '00',
        'instrument_status': '正常',
        'connection_status': '在线',
    },
    {
        'ship_model': 'DL-3022',
        'phosphate': 0.95,
        'phosphate_time': now,
        'ammonia': 0.18,
        'ammonia_time': now,
        'nitrate': 2.6,
        'nitrate_time': now,
        'nitrite': 0.10,
        'nitrite_time': now,
        'error_code1': '00',
        'error_code2': '00',
        'instrument_status': '正常',
        'connection_status': '在线',
    },
    {
        'ship_model': 'DL-3022',
        'phosphate': 0.92,
        'phosphate_time': now - timedelta(hours=1),
        'ammonia': 0.17,
        'ammonia_time': now - timedelta(hours=1),
        'nitrate': 2.5,
        'nitrate_time': now - timedelta(hours=1),
        'nitrite': 0.09,
        'nitrite_time': now - timedelta(hours=1),
        'error_code1': '00',
        'error_code2': '00',
        'instrument_status': '正常',
        'connection_status': '在线',
    },
]

for sample in nutrient_samples:
    NutrientData.objects.create(**sample)
    print(f"Created nutrient data for {sample['ship_model']}")

print("\n✅ Successfully created monitoring data!")
