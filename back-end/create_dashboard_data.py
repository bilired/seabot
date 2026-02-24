#!/usr/bin/env python3
"""
创建工作台样本数据（销售数据、用户增长数据）
"""
import os
import sys
import django
from datetime import datetime, timedelta

# 添加 seadrone 项目路径
sys.path.insert(0, '/Users/hanksgao/Desktop/seabot/back-end/seadrone')
os.chdir('/Users/hanksgao/Desktop/seabot/back-end/seadrone')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seadrone.settings')
django.setup()

from accounts.models import MonthlySalesData, UserGrowthData, DashboardStats
from django.contrib.auth.models import User

# 清空现有数据（可选）
# MonthlySalesData.objects.all().delete()
# UserGrowthData.objects.all().delete()

# 创建月度销售数据
sales_data = [
    {'month': '1月', 'sales': 5000},
    {'month': '2月', 'sales': 6500},
    {'month': '3月', 'sales': 4500},
    {'month': '4月', 'sales': 7200},
    {'month': '5月', 'sales': 8100},
    {'month': '6月', 'sales': 9200},
    {'month': '7月', 'sales': 8500},
    {'month': '8月', 'sales': 9800},
    {'month': '9月', 'sales': 10200},
    {'month': '10月', 'sales': 11500},
    {'month': '11月', 'sales': 12000},
    {'month': '12月', 'sales': 13500},
]

for item in sales_data:
    record, created = MonthlySalesData.objects.get_or_create(
        month=item['month'],
        defaults={'sales': item['sales']}
    )
    if created:
        print(f"✅ 创建销售数据: {item['month']}")
    else:
        print(f"⏭️  销售数据已存在: {item['month']}")

# 创建用户增长数据
base_date = datetime(2026, 1, 1)
growth_data_values = [
    {'newUsers': 50, 'activeUsers': 300},
    {'newUsers': 65, 'activeUsers': 350},
    {'newUsers': 45, 'activeUsers': 380},
    {'newUsers': 80, 'activeUsers': 420},
    {'newUsers': 95, 'activeUsers': 480},
    {'newUsers': 70, 'activeUsers': 530},
    {'newUsers': 88, 'activeUsers': 580},
    {'newUsers': 102, 'activeUsers': 620},
    {'newUsers': 75, 'activeUsers': 680},
    {'newUsers': 110, 'activeUsers': 750},
]

for i, item in enumerate(growth_data_values):
    date = base_date + timedelta(days=7*i)
    record, created = UserGrowthData.objects.get_or_create(
        date=date,
        defaults={
            'new_users': item['newUsers'],
            'active_users': item['activeUsers']
        }
    )
    if created:
        print(f"✅ 创建增长数据: {date.strftime('%Y-%m-%d')}")
    else:
        print(f"⏭️  增长数据已存在: {date.strftime('%Y-%m-%d')}")

# 更新 DashboardStats 示例数据
try:
    user = User.objects.first()
    if user:
        stats, _ = DashboardStats.objects.get_or_create(user=user)
        stats.total_tasks = 30
        stats.completed_tasks = 18
        stats.active_projects = 5
        stats.total_sales = 98900.00
        stats.new_users_count = 850
        stats.save()
        print(f"✅ 更新用户 {user.username} 的仪表板统计数据")
except Exception as e:
    print(f"⚠️  更新仪表板数据失败: {e}")

print("\n✨ 完成！工作台样本数据已创建")
