# accounts/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import DashboardStats, UserActivity, DroneDevice

@api_view(['POST'])
@permission_classes([])  # 允许任何人注册
def register_view(request):
    """用户注册"""
    # 1. 获取前端传来的数据
    username = request.data.get('userName')
    password = request.data.get('password')
    confirm_password = request.data.get('confirmPassword')
    
    # 2. 验证输入
    if not username or not password or not confirm_password:
        return Response({
            "code": 400,
            "msg": "用户名和密码不能为空"
        }, status=status.HTTP_200_OK)
    
    # 3. 检查用户名长度
    if len(username) < 3 or len(username) > 30:
        return Response({
            "code": 400,
            "msg": "用户名长度必须在 3-30 个字符之间"
        }, status=status.HTTP_200_OK)
    
    # 4. 检查密码长度
    if len(password) < 6:
        return Response({
            "code": 400,
            "msg": "密码长度不能少于 6 个字符"
        }, status=status.HTTP_200_OK)
    
    # 5. 检查两次密码是否相同
    if password != confirm_password:
        return Response({
            "code": 400,
            "msg": "两次密码输入不一致"
        }, status=status.HTTP_200_OK)
    
    # 6. 检查用户是否已存在
    if User.objects.filter(username=username).exists():
        return Response({
            "code": 400,
            "msg": "用户名已被注册"
        }, status=status.HTTP_200_OK)
    
    # 7. 创建新用户
    try:
        user = User.objects.create_user(
            username=username,
            password=password
        )
        # 为新用户创建仪表板统计数据
        DashboardStats.objects.create(user=user)
        
        # 8. 返回成功响应
        return Response({
            "code": 200,
            "msg": "注册成功，请登录",
            "data": {
                "userId": user.id,
                "userName": user.username
            }
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"注册失败：{str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # 覆盖全局设置，允许任何人访问登录接口
def login_view(request):
    # 1. 获取前端传来的数据
    username = request.data.get('userName')
    password = request.data.get('password')
    
    # 2. 验证用户名密码
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # 3. 用户名密码正确，生成 Token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # 记录登录活动
        UserActivity.objects.create(
            user=user,
            activity_type='login',
            description=f'{user.username} 登录成功'
        )
        
        return Response({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "token": access_token,  # 前端期望的字段名
                "refreshToken": refresh_token  # 前端期望的字段名
            }
        }, status=status.HTTP_200_OK)
    else:
        # 4. 登录失败
        return Response({
            "code": 401,
            "msg": "用户名或密码错误"
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 需要身份验证
def user_info_view(request):
    """获取当前登录用户的信息"""
    user = request.user
    
    return Response({
        "code": 200,
        "msg": "获取成功",
        "data": {
            "userId": user.id,
            "userName": user.username,
            "email": user.email,
            "avatar": "",  # 如果需要头像，可以从扩展的 User 模型获取
            "roles": ["R_ADMIN"],   # 返回管理员角色
            "buttons": []  # 按钮权限，后续可以实现
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 需要身份验证
def menu_list_view(request):
    """获取菜单列表 (前端动态路由所需)"""
    # 返回一个基础的菜单结构，前端可以根据这个菜单动态注册路由
    menu_list = [
        {
            "path": "/dashboard",
            "name": "Dashboard",
            "component": "Dashboard",
            "meta": {
                "title": "仪表盘",
                "icon": "dashboard",
                "roles": ["R_ADMIN", "R_USER"]
            }
        },
        {
            "path": "/system",
            "name": "System",
            "component": "Layout",
            "meta": {
                "title": "系统管理",
                "icon": "setting",
                "roles": ["R_ADMIN"]
            },
            "children": [
                {
                    "path": "user",
                    "name": "User",
                    "component": "system/user/index",
                    "meta": {
                        "title": "用户管理",
                        "icon": "user",
                        "roles": ["R_ADMIN"]
                    }
                }
            ]
        }
    ]
    
    return Response({
        "code": 200,
        "msg": "获取成功",
        "data": menu_list
    }, status=status.HTTP_200_OK)


class DashboardStatsView(APIView):
    """获取仪表板统计数据"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取仪表板统计数据
        
        返回数据包含：
        - onlineDevices: 在线设备数
        - systemUptime: 系统运行时长（天）
        - monthlyNewDevices: 本月新增设备数
        - todayActivities: 今日动态数
        """
        try:
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            # 统计在线设备数
            online_devices = DroneDevice.objects.filter(status='online').count()
            
            # 计算系统运行时长（从第一个设备创建时间或用户注册时间开始计算）
            first_device = DroneDevice.objects.order_by('created_at').first()
            user = request.user
            
            if first_device:
                start_time = min(first_device.created_at, user.date_joined)
            else:
                start_time = user.date_joined
            
            now = timezone.now()
            uptime_days = (now - start_time).days
            
            # 统计本月新增设备数
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_new_devices = DroneDevice.objects.filter(created_at__gte=month_start).count()
            
            # 统计今日动态数
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_activities = UserActivity.objects.filter(created_at__gte=today_start).count()
            
            return Response({
                "code": 200,
                "msg": "获取成功",
                "data": {
                    "onlineDevices": online_devices,
                    "systemUptime": uptime_days,
                    "monthlyNewDevices": monthly_new_devices,
                    "todayActivities": today_activities,
                    "updatedAt": now.isoformat()
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": 500,
                "msg": f"获取数据失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_activity(request):
    """获取用户活动日志
    
    参数：
    - limit: 返回的记录数（默认10）
    
    返回：活动日志列表
    """
    try:
        user = request.user
        limit = int(request.query_params.get('limit', 10))
        
        activities = UserActivity.objects.filter(user=user)[:limit]
        
        activity_list = []
        for activity in activities:
            activity_list.append({
                "id": activity.id,
                "activityType": activity.activity_type,
                "description": activity.description,
                "createdAt": activity.created_at.isoformat()
            })
        
        return Response({
            "code": 200,
            "msg": "获取成功",
            "data": activity_list
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"获取数据失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_drone_list(request):
    """获取无人船设备列表

    参数：
    - current: 当前页（默认1）
    - size: 每页数量（默认10）
    - keyword: 关键字（可选）
    """
    try:
        current = int(request.query_params.get('current', 1))
        size = int(request.query_params.get('size', 10))
        keyword = request.query_params.get('keyword')

        queryset = DroneDevice.objects.all()
        if keyword:
            queryset = queryset.filter(Q(model__icontains=keyword) | Q(ship_type__icontains=keyword))

        total = queryset.count()
        start = (current - 1) * size
        end = start + size
        devices = queryset.order_by('-id')[start:end]

        records = []
        for item in devices:
            records.append({
                "id": str(item.id),
                "shipType": item.ship_type,
                "length": item.length,
                "model": item.model,
                "weight": item.weight,
                "functions": item.functions,
                "status": item.status,
                "maxSpeed": item.max_speed
            })

        return Response({
            "code": 200,
            "msg": "获取成功",
            "data": {
                "records": records,
                "current": current,
                "size": size,
                "total": total
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"获取数据失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_drone(request):
    """创建无人船设备"""
    try:
        ship_type = request.data.get('shipType')
        length = request.data.get('length')
        model = request.data.get('model')
        weight = request.data.get('weight')
        functions = request.data.get('functions')
        status_value = request.data.get('status', 'offline')
        max_speed = request.data.get('maxSpeed')

        if not ship_type or not model or not functions:
            return Response({
                "code": 400,
                "msg": "船型、型号、功能模块为必填项"
            }, status=status.HTTP_200_OK)

        if length is None or weight is None or max_speed is None:
            return Response({
                "code": 400,
                "msg": "长度、重量、最高航速为必填项"
            }, status=status.HTTP_200_OK)

        device = DroneDevice.objects.create(
            ship_type=ship_type,
            length=int(length),
            model=model,
            weight=float(weight),
            functions=functions,
            status=status_value if status_value in ['online', 'offline'] else 'offline',
            max_speed=float(max_speed)
        )

        return Response({
            "code": 200,
            "msg": "创建成功",
            "data": {
                "id": str(device.id)
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"创建失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_drone(request):
    """删除无人船设备"""
    device_id = request.data.get('id')
    if not device_id:
        return Response({
            "code": 400,
            "msg": "设备ID不能为空"
        }, status=status.HTTP_200_OK)

    deleted, _ = DroneDevice.objects.filter(id=device_id).delete()
    if deleted == 0:
        return Response({
            "code": 404,
            "msg": "设备不存在"
        }, status=status.HTTP_200_OK)

    return Response({
        "code": 200,
        "msg": "删除成功"
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_delete_drone(request):
    """批量删除无人船设备"""
    ids = request.data.get('ids')
    if not isinstance(ids, list) or len(ids) == 0:
        return Response({
            "code": 400,
            "msg": "设备ID列表不能为空"
        }, status=status.HTTP_200_OK)

    deleted, _ = DroneDevice.objects.filter(id__in=ids).delete()

    return Response({
        "code": 200,
        "msg": "删除成功",
        "data": {
            "deleted": deleted
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sales_data(request):
    """获取销售数据（用于销售概览图表）
    
    返回：月度销售数据
    """
    try:
        from .models import MonthlySalesData
        
        # 从数据库获取月度销售数据
        sales_records = MonthlySalesData.objects.all()
        
        if not sales_records.exists():
            # 如果数据库中没有数据，返回默认数据
            sales_data = [
                {"month": "1月", "sales": 5000},
                {"month": "2月", "sales": 6500},
                {"month": "3月", "sales": 4500},
                {"month": "4月", "sales": 7200},
                {"month": "5月", "sales": 8100},
                {"month": "6月", "sales": 9200},
            ]
        else:
            sales_data = [
                {"month": item.month, "sales": item.sales}
                for item in sales_records
            ]
        
        return Response({
            "code": 200,
            "msg": "获取成功",
            "data": sales_data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"获取销售数据失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_growth(request):
    """获取用户增长数据
    
    返回：用户数增长趋势
    """
    try:
        from .models import UserGrowthData
        
        # 从数据库获取用户增长数据
        growth_records = UserGrowthData.objects.all()
        
        if not growth_records.exists():
            # 如果数据库中没有数据，返回默认数据
            growth_data = [
                {"date": "2024-01-01", "newUsers": 50, "activeUsers": 300},
                {"date": "2024-01-08", "newUsers": 65, "activeUsers": 350},
                {"date": "2024-01-15", "newUsers": 45, "activeUsers": 380},
                {"date": "2024-01-22", "newUsers": 80, "activeUsers": 420},
                {"date": "2024-01-29", "newUsers": 95, "activeUsers": 480},
                {"date": "2024-02-05", "newUsers": 70, "activeUsers": 530},
            ]
        else:
            growth_data = [
                {
                    "date": item.date.strftime('%Y-%m-%d'),
                    "newUsers": item.new_users,
                    "activeUsers": item.active_users
                }
                for item in growth_records
            ]
        
        return Response({
            "code": 200,
            "msg": "获取成功",
            "data": growth_data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"获取用户增长数据失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




