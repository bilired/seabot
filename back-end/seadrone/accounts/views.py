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
        - totalTasks: 总任务数
        - completedTasks: 已完成任务数
        - activeProjects: 活跃项目数
        - totalSales: 总销售额
        - newUsersCount: 新用户数
        """
        try:
            user = request.user
            stats, created = DashboardStats.objects.get_or_create(user=user)
            
            return Response({
                "code": 200,
                "msg": "获取成功",
                "data": {
                    "totalTasks": stats.total_tasks,
                    "completedTasks": stats.completed_tasks,
                    "activeProjects": stats.active_projects,
                    "totalSales": float(stats.total_sales),
                    "newUsersCount": stats.new_users_count,
                    "updatedAt": stats.updated_at.isoformat()
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
        user = request.user
        stats = DashboardStats.objects.get(user=user)
        
        # 模拟月度销售数据
        sales_data = [
            {"month": "1月", "sales": 5000},
            {"month": "2月", "sales": 6500},
            {"month": "3月", "sales": 4500},
            {"month": "4月", "sales": 7200},
            {"month": "5月", "sales": 8100},
            {"month": "6月", "sales": 9200},
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
        # 模拟用户增长数据
        growth_data = [
            {"date": "2024-01-01", "newUsers": 50, "activeUsers": 300},
            {"date": "2024-01-08", "newUsers": 65, "activeUsers": 350},
            {"date": "2024-01-15", "newUsers": 45, "activeUsers": 380},
            {"date": "2024-01-22", "newUsers": 80, "activeUsers": 420},
            {"date": "2024-01-29", "newUsers": 95, "activeUsers": 480},
            {"date": "2024-02-05", "newUsers": 70, "activeUsers": 530},
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_water_quality_data(request):
    """获取水质监测数据
    
    返回：水质数据列表
    """
    try:
        from .models import WaterQualityData
        
        # 获取最新的20条数据
        water_data = WaterQualityData.objects.all()[:20]
        
        data_list = []
        for item in water_data:
            data_list.append({
                "shipModel": item.ship_model,
                "temperature": item.temperature,
                "ph": item.ph,
                "chlorophyll": item.chlorophyll,
                "salinity": item.salinity,
                "dissolvedOxygen": item.dissolved_oxygen,
                "conductivity": item.conductivity,
                "turbidity": item.turbidity,
                "algae": item.algae,
                "warningCode": item.warning_code,
                "collectionTime": item.collection_time.strftime('%Y-%m-%d %H:%M:%S'),
                "connectionStatus": item.connection_status
            })
        
        return Response({
            "code": 200,
            "msg": "获取成功",
            "data": data_list
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"获取水质数据失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_nutrient_data(request):
    """获取营养盐数据
    
    返回：营养盐数据列表
    """
    try:
        from .models import NutrientData
        
        # 获取最新的20条数据
        nutrient_data = NutrientData.objects.all()[:20]
        
        data_list = []
        for item in nutrient_data:
            data_list.append({
                "shipModel": item.ship_model,
                "phosphate": item.phosphate,
                "phosphateTime": item.phosphate_time.strftime('%Y-%m-%d %H:%M:%S'),
                "ammonia": item.ammonia,
                "ammoniaTime": item.ammonia_time.strftime('%Y-%m-%d %H:%M:%S'),
                "nitrate": item.nitrate,
                "nitrateTime": item.nitrate_time.strftime('%Y-%m-%d %H:%M:%S'),
                "nitrite": item.nitrite,
                "nitriteTime": item.nitrite_time.strftime('%Y-%m-%d %H:%M:%S'),
                "errorCode1": item.error_code1,
                "errorCode2": item.error_code2,
                "instrumentStatus": item.instrument_status,
                "collectionTime": item.collection_time.strftime('%Y-%m-%d %H:%M:%S'),
                "connectionStatus": item.connection_status
            })
        
        return Response({
            "code": 200,
            "msg": "获取成功",
            "data": data_list
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"获取营养盐数据失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # 允许设备无需认证上传（或使用设备令牌）
def upload_water_quality_data(request):
    """无人船上传水质数据
    
    请求参数：
    - shipModel: 船型号
    - temperature: 水温
    - ph: pH值
    - chlorophyll: 叶绿素
    - salinity: 盐度
    - dissolvedOxygen: 溶解氧
    - conductivity: 电导率
    - turbidity: 浊度
    - algae: 蓝绿藻
    - warningCode: 警告码（可选）
    """
    try:
        from .models import WaterQualityData
        
        # 获取数据
        ship_model = request.data.get('shipModel')
        temperature = request.data.get('temperature')
        ph = request.data.get('ph')
        chlorophyll = request.data.get('chlorophyll')
        salinity = request.data.get('salinity')
        dissolved_oxygen = request.data.get('dissolvedOxygen')
        conductivity = request.data.get('conductivity')
        turbidity = request.data.get('turbidity')
        algae = request.data.get('algae')
        warning_code = request.data.get('warningCode', '正常')
        
        # 验证必填字段
        if not all([ship_model, temperature is not None, ph is not None]):
            return Response({
                "code": 400,
                "msg": "缺少必填字段"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建数据记录
        water_data = WaterQualityData.objects.create(
            ship_model=ship_model,
            temperature=float(temperature),
            ph=float(ph),
            chlorophyll=float(chlorophyll or 0),
            salinity=float(salinity or 0),
            dissolved_oxygen=float(dissolved_oxygen or 0),
            conductivity=float(conductivity or 0),
            turbidity=float(turbidity or 0),
            algae=int(algae or 0),
            warning_code=warning_code,
            connection_status='在线'
        )
        
        return Response({
            "code": 200,
            "msg": "数据上传成功",
            "data": {
                "id": water_data.id,
                "collectionTime": water_data.collection_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"数据上传失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # 允许设备无需认证上传
def upload_nutrient_data(request):
    """无人船上传营养盐数据
    
    请求参数：
    - shipModel: 船型号
    - phosphate: 磷酸盐
    - ammonia: 氨氮
    - nitrate: 硝酸盐
    - nitrite: 亚硝酸盐
    - errorCode1, errorCode2: 错误码（可选）
    - instrumentStatus: 仪器状态（可选）
    """
    try:
        from .models import NutrientData
        from django.utils import timezone
        
        # 获取数据
        ship_model = request.data.get('shipModel')
        phosphate = request.data.get('phosphate')
        ammonia = request.data.get('ammonia')
        nitrate = request.data.get('nitrate')
        nitrite = request.data.get('nitrite')
        error_code1 = request.data.get('errorCode1', '00')
        error_code2 = request.data.get('errorCode2', '00')
        instrument_status = request.data.get('instrumentStatus', '正常')
        
        # 验证必填字段
        if not all([ship_model, phosphate is not None]):
            return Response({
                "code": 400,
                "msg": "缺少必填字段"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        now = timezone.now()
        
        # 创建数据记录
        nutrient_data = NutrientData.objects.create(
            ship_model=ship_model,
            phosphate=float(phosphate),
            phosphate_time=now,
            ammonia=float(ammonia or 0),
            ammonia_time=now,
            nitrate=float(nitrate or 0),
            nitrate_time=now,
            nitrite=float(nitrite or 0),
            nitrite_time=now,
            error_code1=error_code1,
            error_code2=error_code2,
            instrument_status=instrument_status,
            connection_status='在线'
        )
        
        return Response({
            "code": 200,
            "msg": "数据上传成功",
            "data": {
                "id": nutrient_data.id,
                "collectionTime": nutrient_data.collection_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"数据上传失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
