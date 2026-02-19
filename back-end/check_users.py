#!/usr/bin/env python
"""
验证用户注册是否成功的脚本
直接检查 Django 数据库中是否有用户数据
"""

import os
import django

# 配置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seadrone.settings')
django.setup()

from django.contrib.auth.models import User

def check_users():
    """查看数据库中的所有用户"""
    print("=" * 60)
    print("📋 数据库中的所有用户")
    print("=" * 60)
    
    users = User.objects.all()
    
    if not users.exists():
        print("❌ 数据库中没有用户")
        return
    
    print(f"✅ 共有 {users.count()} 个用户\n")
    
    for user in users:
        print(f"ID: {user.id}")
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        print(f"创建时间: {user.date_joined}")
        print(f"最后登录: {user.last_login}")
        print("-" * 60)

def check_user_by_username(username):
    """检查特定用户是否存在"""
    print(f"\n🔍 查找用户: {username}")
    print("-" * 60)
    
    try:
        user = User.objects.get(username=username)
        print(f"✅ 用户存在")
        print(f"ID: {user.id}")
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        print(f"创建时间: {user.date_joined}")
        return True
    except User.DoesNotExist:
        print(f"❌ 用户不存在")
        return False

def create_test_user():
    """创建一个测试用户"""
    print("\n➕ 创建测试用户...")
    print("-" * 60)
    
    try:
        user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )
        print(f"✅ 用户创建成功")
        print(f"ID: {user.id}")
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        return user
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return None

if __name__ == '__main__':
    # 查看所有用户
    check_users()
    
    # 检查特定用户
    check_user_by_username('Admin')
    check_user_by_username('testuser')
    
    print("\n" + "=" * 60)
    print("✨ 验证完成")
    print("=" * 60)
