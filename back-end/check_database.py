#!/usr/bin/env python
"""
完整的数据库内容检查脚本
显示用户、设备、水质数据、营养盐数据等
"""

import os
import django
from datetime import datetime

# 配置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seadrone.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import DashboardStats, DroneDevice
from monitoring.models import WaterQualityData, NutrientData

def print_section(title):
    """打印分隔符"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_users():
    """检查用户信息"""
    print_section("👥 用户账户信息")
    
    users = User.objects.all()
    
    if not users.exists():
        print("❌ 数据库中没有用户")
        return
    
    print(f"✅ 共有 {users.count()} 个用户\n")
    
    for user in users:
        print(f"  ID: {user.id}")
        print(f"  用户名: {user.username}")
        print(f"  邮箱: {user.email if user.email else '(未设置)'}")
        print(f"  创建时间: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  最后登录: {user.last_login if user.last_login else '(未登录)'}")
        print("  " + "-" * 66)

def check_drone_devices():
    """检查无人船设备信息"""
    print_section("🚤 无人船设备信息")
    
    devices = DroneDevice.objects.all()
    
    if not devices.exists():
        print("❌ 数据库中没有设备")
        return
    
    print(f"✅ 共有 {devices.count()} 台设备\n")
    
    for device in devices:
        print(f"  ID: {device.id}")
        print(f"  船型: {device.ship_type}")
        print(f"  型号: {device.model}")
        print(f"  长度: {device.length} m")
        print(f"  重量: {device.weight} kg")
        print(f"  最大速度: {device.max_speed} km/h")
        print(f"  功能: {device.functions}")
        print(f"  状态: {device.status}")
        print("  " + "-" * 66)

def check_water_quality():
    """检查水质数据"""
    print_section("💧 水质监测数据")
    
    data = WaterQualityData.objects.all()
    
    if not data.exists():
        print("❌ 数据库中没有水质数据")
        return
    
    print(f"✅ 共有 {data.count()} 条水质数据记录\n")
    
    # 显示最新的5条
    latest = data.order_by('-collection_time')[:5]
    
    for item in latest:
        print(f"  船型: {item.ship_model}")
        print(f"  温度: {item.temperature}°C")
        print(f"  pH值: {item.pH}")
        print(f"  叶绿素a: {item.chlorophyll} mg/m³")
        print(f"  盐度: {item.salinity} PSU")
        print(f"  溶解氧: {item.dissolved_oxygen} mg/L")
        print(f"  电导率: {item.conductivity} mS/cm")
        print(f"  浊度: {item.turbidity} NTU")
        print(f"  藻密度: {item.blue_green}")
        print(f"  采集时间: {item.collection_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  警告码: {item.warn}")
        print(f"  连接状态: {item.connection_status}")
        print("  " + "-" * 66)

def check_nutrient_data():
    """检查营养盐数据"""
    print_section("🧂 营养盐监测数据")
    
    data = NutrientData.objects.all()
    
    if not data.exists():
        print("❌ 数据库中没有营养盐数据")
        return
    
    print(f"✅ 共有 {data.count()} 条营养盐数据记录\n")
    
    # 显示最新的5条
    latest = data.order_by('-collection_time')[:5]
    
    for item in latest:
        print(f"  数据ID: {item.ship_model}")
        print(f"  时间戳: {item.timestamp}")
        print(f"  连接状态: {item.status}")
        print(f"  氨氮: {item.ammonia_nitrogen} mg/L")
        print(f"  硝酸盐: {item.nitrate} μmol/L")
        print(f"  亚硝酸盐: {item.sub_nitrate} mg/L")
        print(f"  磷酸盐: {item.phosphates} mg/L")
        print(f"  警告码: {item.warn}")
        print(f"  入库时间: {item.collection_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("  " + "-" * 66)

def check_dashboard_stats():
    """检查仪表板统计数据"""
    print_section("📊 仪表板统计数据")
    
    stats = DashboardStats.objects.all()
    
    if not stats.exists():
        print("❌ 数据库中没有仪表板数据")
        return
    
    print(f"✅ 共有 {stats.count()} 条统计记录\n")
    
    for stat in stats:
        print(f"  用户: {stat.user.username}")
        print(f"  总任务数: {stat.total_tasks}")
        print(f"  已完成任务: {stat.completed_tasks}")
        print(f"  活跃项目: {stat.active_projects}")
        print(f"  总销售额: {stat.total_sales}")
        print(f"  新用户数: {stat.new_users_count}")
        print(f"  更新时间: {stat.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("  " + "-" * 66)

def check_database_summary():
    """显示数据库总结"""
    print_section("📈 数据库总结")
    
    print(f"  👥 用户账户: {User.objects.count()} 个")
    print(f"  🚤 无人船设备: {DroneDevice.objects.count()} 台")
    print(f"  💧 水质数据: {WaterQualityData.objects.count()} 条记录")
    print(f"  🧂 营养盐数据: {NutrientData.objects.count()} 条记录")
    print(f"  📊 仪表板数据: {DashboardStats.objects.count()} 条记录")

def main():
    """主函数"""
    print("\n" + "🔍 " * 17 + "🔍")
    print("   " + " " * 15 + "数据库内容检查")
    print("🔍 " * 17 + "🔍\n")
    
    check_database_summary()
    check_users()
    check_drone_devices()
    check_water_quality()
    check_nutrient_data()
    check_dashboard_stats()
    
    print("\n" + "=" * 70)
    print("  ✨ 数据库检查完成")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
