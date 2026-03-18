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
        'pH': 8.1,
        'chlorophyll': 15.3,
        'salinity': 32.5,
        'dissolved_oxygen': 7.8,
        'conductivity': 45000,
        'turbidity': 1.2,
        'blue_green': 150,
        'warn': '0',
        'connection_status': '在线',
    },
    {
        'ship_model': 'DL-3026',
        'temperature': 28.2,
        'pH': 8.0,
        'chlorophyll': 14.8,
        'salinity': 32.3,
        'dissolved_oxygen': 7.9,
        'conductivity': 44800,
        'turbidity': 1.1,
        'blue_green': 145,
        'warn': '0',
        'connection_status': '在线',
    },
    {
        'ship_model': 'DL-3022',
        'temperature': 29.1,
        'pH': 8.2,
        'chlorophyll': 16.5,
        'salinity': 33.0,
        'dissolved_oxygen': 7.5,
        'conductivity': 45500,
        'turbidity': 1.5,
        'blue_green': 180,
        'warn': '0',
        'connection_status': '在线',
    },
    {
        'ship_model': 'DL-3022',
        'temperature': 29.0,
        'pH': 8.1,
        'chlorophyll': 16.0,
        'salinity': 32.8,
        'dissolved_oxygen': 7.6,
        'conductivity': 45200,
        'turbidity': 1.4,
        'blue_green': 170,
        'warn': '0',
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
        'timestamp': now,
        'status': 1,
        'ammonia_nitrogen': 0.15,
        'ammonia_nitrogen_timestamp': now,
        'nitrate': 2.3,
        'nitrate_timestamp': now,
        'sub_nitrate': 0.08,
        'sub_nitrate_timestamp': now,
        'phosphates': 0.85,
        'phosphates_timestamp': now,
        'warn': '0',
    },
    {
        'ship_model': 'DL-3026',
        'timestamp': now - timedelta(hours=1),
        'status': 1,
        'ammonia_nitrogen': 0.14,
        'ammonia_nitrogen_timestamp': now - timedelta(hours=1),
        'nitrate': 2.2,
        'nitrate_timestamp': now - timedelta(hours=1),
        'sub_nitrate': 0.07,
        'sub_nitrate_timestamp': now - timedelta(hours=1),
        'phosphates': 0.82,
        'phosphates_timestamp': now - timedelta(hours=1),
        'warn': '0',
    },
    {
        'ship_model': 'DL-3022',
        'timestamp': now,
        'status': 1,
        'ammonia_nitrogen': 0.18,
        'ammonia_nitrogen_timestamp': now,
        'nitrate': 2.6,
        'nitrate_timestamp': now,
        'sub_nitrate': 0.10,
        'sub_nitrate_timestamp': now,
        'phosphates': 0.95,
        'phosphates_timestamp': now,
        'warn': '0',
    },
    {
        'ship_model': 'DL-3022',
        'timestamp': now - timedelta(hours=1),
        'status': 1,
        'ammonia_nitrogen': 0.17,
        'ammonia_nitrogen_timestamp': now - timedelta(hours=1),
        'nitrate': 2.5,
        'nitrate_timestamp': now - timedelta(hours=1),
        'sub_nitrate': 0.09,
        'sub_nitrate_timestamp': now - timedelta(hours=1),
        'phosphates': 0.92,
        'phosphates_timestamp': now - timedelta(hours=1),
        'warn': '0',
    },
]

for sample in nutrient_samples:
    NutrientData.objects.create(**sample)
    print(f"Created nutrient data for {sample['ship_model']}")

print("\n✅ Successfully created monitoring data!")
