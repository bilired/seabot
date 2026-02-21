#!/usr/bin/env python3
"""
Seabot 仪表板 API 测试脚本
用于测试前后端集成的 API 端点
"""

import requests
import json
import argparse
from typing import Dict, Any, Optional

class DashboardAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.refresh_token = None
    
    def register(self, username: str, password: str) -> Dict[str, Any]:
        """注册新用户"""
        url = f"{self.base_url}/api/register/"
        data = {
            "userName": username,
            "password": password,
            "confirmPassword": password
        }
        
        print(f"\n[注册] POST {url}")
        print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        url = f"{self.base_url}/api/login/"
        data = {
            "userName": username,
            "password": password
        }
        
        print(f"\n[登录] POST {url}")
        print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("code") == 200 and result.get("data"):
            self.token = result["data"].get("token")
            self.refresh_token = result["data"].get("refreshToken")
            print(f"✓ 登录成功，已保存 token")
        
        return result
    
    def get_user_info(self) -> Dict[str, Any]:
        """获取用户信息"""
        if not self.token:
            print("❌ 错误: 未登录，请先调用 login()")
            return {}
        
        url = f"{self.base_url}/api/user/info/"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print(f"\n[获取用户信息] GET {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
    
    def get_menu_list(self) -> Dict[str, Any]:
        """获取菜单列表"""
        if not self.token:
            print("❌ 错误: 未登录，请先调用 login()")
            return {}
        
        url = f"{self.base_url}/api/v3/system/menus/"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print(f"\n[获取菜单列表] GET {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """获取仪表板统计数据"""
        if not self.token:
            print("❌ 错误: 未登录，请先调用 login()")
            return {}
        
        url = f"{self.base_url}/api/dashboard/stats/"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print(f"\n[获取仪表板统计数据] GET {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
    
    def get_sales_data(self) -> Dict[str, Any]:
        """获取销售数据"""
        if not self.token:
            print("❌ 错误: 未登录，请先调用 login()")
            return {}
        
        url = f"{self.base_url}/api/dashboard/sales/"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print(f"\n[获取销售数据] GET {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
    
    def get_user_growth(self) -> Dict[str, Any]:
        """获取用户增长数据"""
        if not self.token:
            print("❌ 错误: 未登录，请先调用 login()")
            return {}
        
        url = f"{self.base_url}/api/dashboard/growth/"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        print(f"\n[获取用户增长数据] GET {url}")
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
    
    def get_user_activity(self, limit: int = 8) -> Dict[str, Any]:
        """获取用户活动日志"""
        if not self.token:
            print("❌ 错误: 未登录，请先调用 login()")
            return {}
        
        url = f"{self.base_url}/api/dashboard/activity/"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"limit": limit}
        
        print(f"\n[获取用户活动日志] GET {url}?limit={limit}")
        response = requests.get(url, headers=headers, params=params)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
    
    def run_full_test(self, username: str = "testuser", password: str = "123456"):
        """运行完整测试流程"""
        print("=" * 60)
        print("Seabot 仪表板 API 完整测试")
        print("=" * 60)
        
        # 1. 注册用户（如果不存在）
        print("\n[步骤 1] 尝试注册新用户...")
        self.register(username, password)
        
        # 2. 登录
        print("\n[步骤 2] 用户登录...")
        login_result = self.login(username, password)
        if login_result.get("code") != 200:
            print("❌ 登录失败，停止测试")
            return
        
        # 3. 获取用户信息
        print("\n[步骤 3] 获取用户信息...")
        self.get_user_info()
        
        # 4. 获取菜单列表
        print("\n[步骤 4] 获取菜单列表...")
        self.get_menu_list()
        
        # 5. 获取仪表板统计数据
        print("\n[步骤 5] 获取仪表板统计数据...")
        self.get_dashboard_stats()
        
        # 6. 获取销售数据
        print("\n[步骤 6] 获取销售数据...")
        self.get_sales_data()
        
        # 7. 获取用户增长数据
        print("\n[步骤 7] 获取用户增长数据...")
        self.get_user_growth()
        
        # 8. 获取用户活动日志
        print("\n[步骤 8] 获取用户活动日志...")
        self.get_user_activity()
        
        print("\n" + "=" * 60)
        print("✓ 完整测试流程已完成！")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Seabot 仪表板 API 测试工具")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API 基础 URL")
    parser.add_argument("--username", default="testuser", help="测试用户名")
    parser.add_argument("--password", default="123456", help="测试密码")
    parser.add_argument("--test", choices=["all", "auth", "dashboard"], default="all", help="测试类型")
    
    args = parser.parse_args()
    
    tester = DashboardAPITester(args.base_url)
    
    if args.test == "all":
        tester.run_full_test(args.username, args.password)
    elif args.test == "auth":
        tester.login(args.username, args.password)
    elif args.test == "dashboard":
        tester.login(args.username, args.password)
        tester.get_dashboard_stats()
        tester.get_sales_data()
        tester.get_user_growth()
        tester.get_user_activity()


if __name__ == "__main__":
    main()
