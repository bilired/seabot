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
from django.db import transaction
from django.core.files.storage import default_storage
from uuid import uuid4
import os
import re
from datetime import timedelta
from .models import DashboardStats, UserActivity, DroneDevice, UserProfile
from .sms_verify.service import send_sms_verify_code, check_sms_verify_code


MOBILE_PATTERN = re.compile(r'^1\d{10}$')


def _is_valid_mobile(mobile):
    if not mobile:
        return False
    return bool(MOBILE_PATTERN.match(str(mobile).strip()))


def _is_mobile_registered(mobile: str) -> bool:
    mobile = (mobile or '').strip()
    if not mobile:
        return False

    return (
        UserProfile.objects.filter(user__is_active=True, mobile=mobile).exists()
        or User.objects.filter(is_active=True, last_name=mobile).exists()
    )

@api_view(['POST'])
@permission_classes([])  # 允许任何人注册
def register_view(request):
    """用户注册"""
    # 1. 获取前端传来的数据
    username = request.data.get('userName')
    password = request.data.get('password')
    confirm_password = request.data.get('confirmPassword')
    mobile = (request.data.get('mobile') or request.data.get('phone') or '').strip()
    sms_code = (request.data.get('smsCode') or request.data.get('verifyCode') or '').strip()
    
    # 2. 验证输入
    if not username or not password or not confirm_password:
        return Response({
            "code": 400,
            "msg": "用户名和密码不能为空"
        }, status=status.HTTP_200_OK)

    if not mobile:
        return Response({
            "code": 400,
            "msg": "手机号不能为空"
        }, status=status.HTTP_200_OK)

    if not _is_valid_mobile(mobile):
        return Response({
            "code": 400,
            "msg": "手机号格式不正确"
        }, status=status.HTTP_200_OK)

    if not sms_code:
        return Response({
            "code": 400,
            "msg": "验证码不能为空"
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

    if _is_mobile_registered(mobile):
        return Response({
            "code": 400,
            "msg": "该手机号已被注册"
        }, status=status.HTTP_200_OK)

    try:
        verify_ok, verify_msg, _ = check_sms_verify_code(mobile, sms_code)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"短信验证服务异常：{str(e)}"
        }, status=status.HTTP_200_OK)

    if not verify_ok:
        return Response({
            "code": 400,
            "msg": verify_msg or "短信验证码校验失败"
        }, status=status.HTTP_200_OK)
    
    # 7. 创建新用户
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password
            )
            user.last_name = mobile
            user.save(update_fields=['last_name'])

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.mobile = mobile
            profile.save(update_fields=['mobile'])

            DashboardStats.objects.create(user=user)
        
        # 8. 返回成功响应
        return Response({
            "code": 200,
            "msg": "注册成功，请登录",
            "data": {
                "userId": user.id,
                "userName": user.username,
                "mobile": mobile
            }
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"注册失败：{str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])
def send_register_sms_code_view(request):
    """注册：发送短信验证码"""
    mobile = (request.data.get('mobile') or request.data.get('phone') or '').strip()

    if not mobile:
        return Response({
            "code": 400,
            "msg": "手机号不能为空"
        }, status=status.HTTP_200_OK)

    if not _is_valid_mobile(mobile):
        return Response({
            "code": 400,
            "msg": "手机号格式不正确"
        }, status=status.HTTP_200_OK)

    if _is_mobile_registered(mobile):
        return Response({
            "code": 400,
            "msg": "该手机号已被注册"
        }, status=status.HTTP_200_OK)

    try:
        success, message, _ = send_sms_verify_code(mobile)
        if not success:
            return Response({
                "code": 400,
                "msg": message or "验证码发送失败"
            }, status=status.HTTP_200_OK)

        return Response({
            "code": 200,
            "msg": message or "验证码发送成功"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"短信服务异常：{str(e)}"
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([])
def verify_register_sms_code_view(request):
    """注册：校验短信验证码"""
    mobile = (request.data.get('mobile') or request.data.get('phone') or '').strip()
    sms_code = (request.data.get('smsCode') or request.data.get('verifyCode') or '').strip()

    if not mobile:
        return Response({
            "code": 400,
            "msg": "手机号不能为空"
        }, status=status.HTTP_200_OK)

    if not _is_valid_mobile(mobile):
        return Response({
            "code": 400,
            "msg": "手机号格式不正确"
        }, status=status.HTTP_200_OK)

    if not sms_code:
        return Response({
            "code": 400,
            "msg": "验证码不能为空"
        }, status=status.HTTP_200_OK)

    try:
        success, message, _ = check_sms_verify_code(mobile, sms_code)
        if not success:
            return Response({
                "code": 400,
                "msg": message or "验证码校验失败"
            }, status=status.HTTP_200_OK)

        return Response({
            "code": 200,
            "msg": message or "验证码校验通过"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"短信服务异常：{str(e)}"
        }, status=status.HTTP_200_OK)


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
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    return Response({
        "code": 200,
        "msg": "获取成功",
        "data": {
            "userId": user.id,
            "userName": user.username,
            "email": user.email,
            "mobile": profile.mobile or user.last_name or '',
            "avatar": profile.avatar,
            "roles": ["R_ADMIN"],   # 返回管理员角色
            "buttons": []  # 按钮权限，后续可以实现
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_user_avatar(request):
    """上传当前用户头像"""
    max_size = 5 * 1024 * 1024
    file = request.FILES.get('file')
    if not file:
        return Response({
            "code": 400,
            "msg": "请选择要上传的头像"
        }, status=status.HTTP_200_OK)

    if not file.content_type or not file.content_type.startswith('image/'):
        return Response({
            "code": 400,
            "msg": "仅支持图片文件"
        }, status=status.HTTP_200_OK)

    if file.size > max_size:
        return Response({
            "code": 400,
            "msg": "头像大小不能超过5MB"
        }, status=status.HTTP_200_OK)

    ext = os.path.splitext(file.name)[1] or '.jpg'
    filename = f"avatar/{request.user.id}_{uuid4().hex}{ext.lower()}"
    saved_path = default_storage.save(filename, file)
    avatar_url = default_storage.url(saved_path)

    if not avatar_url.startswith('http'):
        avatar_url = request.build_absolute_uri(avatar_url)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.avatar = avatar_url
    profile.save(update_fields=['avatar'])

    return Response({
        "code": 200,
        "msg": "头像上传成功",
        "data": {
            "url": avatar_url
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # 需要身份验证
def menu_list_view(request):
    """获取菜单列表 (前端动态路由所需)"""
    # 返回扁平化一级菜单结构
    menu_list = [
        {
            "path": "/console",
            "name": "Console",
            "component": "/dashboard/console",
            "meta": {
                "title": "工作台",
                "icon": "ri:home-smile-2-line",
                "fixedTab": True,
                "roles": ["R_ADMIN", "R_USER"]
            }
        },
        {
            "path": "/analysis",
            "name": "Analysis",
            "component": "/dashboard/analysis",
            "meta": {
                "title": "数据监测",
                "icon": "ri:align-item-bottom-line",
                "roles": ["R_ADMIN", "R_USER"]
            }
        },
        {
            "path": "/drone",
            "name": "DroneManage",
            "component": "/system/drone",
            "meta": {
                "title": "无人船管理",
                "icon": "ri:ship-line",
                "roles": ["R_ADMIN"]
            }
        },
        {
            "path": "/user",
            "name": "User",
            "component": "/system/user",
            "meta": {
                "title": "用户管理",
                "icon": "ri:user-line",
                "roles": ["R_ADMIN"]
            }
        },
        {
            "path": "/user-center",
            "name": "UserCenter",
            "component": "/system/user-center",
            "meta": {
                "title": "个人中心",
                "icon": "ri:user-line",
                "roles": ["R_ADMIN", "R_USER"],
                "isHide": True,
                "isHideTab": True
            }
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
            
            # 统计在线设备数（仅当前用户）
            online_devices = DroneDevice.objects.filter(owner=request.user, status='online').count()
            
            # 计算系统运行时长（从当前用户的第一个设备创建时间或用户注册时间开始计算）
            first_device = DroneDevice.objects.filter(owner=request.user).order_by('created_at').first()
            user = request.user
            
            if first_device:
                start_time = min(first_device.created_at, user.date_joined)
            else:
                start_time = user.date_joined
            
            now = timezone.now()
            uptime_days = (now - start_time).days
            
            # 统计本月新增设备数（仅当前用户）
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_new_devices = DroneDevice.objects.filter(owner=request.user, created_at__gte=month_start).count()
            
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


def _normalize_gender_label(value):
    if value in ['1', 1, '男', 'male', 'Male', 'M', 'm']:
        return '男'
    if value in ['2', 2, '女', 'female', 'Female', 'F', 'f']:
        return '女'
    return '未知'


def _normalize_gender_code(value):
    if value in ['1', 1, '男', 'male', 'Male', 'M', 'm']:
        return '1'
    if value in ['2', 2, '女', 'female', 'Female', 'F', 'f']:
        return '2'
    return ''


def _build_user_item(user, operator='system'):
    profile = getattr(user, 'profile', None)
    user_mobile = ''
    if profile:
        user_mobile = profile.mobile or ''
    if not user_mobile:
        user_mobile = user.last_name or ''

    return {
        "id": user.id,
        "avatar": "",
        "status": '1' if user.is_active else '4',
        "userName": user.username,
        "userGender": _normalize_gender_label(user.first_name),
        "nickName": user.username,
        "userPhone": user_mobile,
        "userEmail": user.email or '',
        "userRoles": ['R_ADMIN'] if (user.is_superuser or user.is_staff) else ['R_USER'],
        "createBy": operator,
        "createTime": user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
        "updateBy": operator,
        "updateTime": (user.last_login or user.date_joined).strftime('%Y-%m-%d %H:%M:%S') if (user.last_login or user.date_joined) else ''
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_list(request):
    """账户管理：获取用户列表"""
    try:
        current = int(request.query_params.get('current', 1))
        size = int(request.query_params.get('size', 20))

        user_name = request.query_params.get('userName')
        user_phone = request.query_params.get('userPhone')
        user_email = request.query_params.get('userEmail')
        status_value = request.query_params.get('status')
        user_gender = request.query_params.get('userGender')

        queryset = User.objects.all().select_related('profile').order_by('-id')

        if user_name:
            queryset = queryset.filter(username__icontains=user_name)
        if user_phone:
            queryset = queryset.filter(Q(profile__mobile__icontains=user_phone) | Q(last_name__icontains=user_phone)).distinct()
        if user_email:
            queryset = queryset.filter(email__icontains=user_email)
        if status_value == '1':
            queryset = queryset.filter(is_active=True)
        elif status_value in ['4', '0']:
            queryset = queryset.filter(is_active=False)

        gender_code = _normalize_gender_code(user_gender)
        if gender_code == '1':
            queryset = queryset.filter(first_name='男')
        elif gender_code == '2':
            queryset = queryset.filter(first_name='女')

        total = queryset.count()
        start = (current - 1) * size
        end = start + size
        users = queryset[start:end]

        records = [_build_user_item(item, request.user.username) for item in users]

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
            "msg": f"获取用户列表失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    """账户管理：创建用户"""
    try:
        user_name = request.data.get('userName') or request.data.get('username')
        user_phone = request.data.get('userPhone') or request.data.get('phone', '')
        user_email = request.data.get('userEmail') or request.data.get('email', '')
        user_gender = request.data.get('userGender') or request.data.get('gender', '1')
        user_roles = request.data.get('userRoles') or request.data.get('role', [])
        status_value = request.data.get('status', '1')
        password = request.data.get('password', '123456')

        if not user_name:
            return Response({
                "code": 400,
                "msg": "用户名不能为空"
            }, status=status.HTTP_200_OK)

        if User.objects.filter(username=user_name).exists():
            return Response({
                "code": 400,
                "msg": "用户名已存在"
            }, status=status.HTTP_200_OK)

        user = User.objects.create_user(
            username=user_name,
            email=user_email,
            password=password
        )
        user.first_name = _normalize_gender_label(user_gender)
        user.last_name = user_phone
        user.is_active = str(status_value) != '4'
        user.is_staff = isinstance(user_roles, list) and 'R_ADMIN' in user_roles
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.mobile = user_phone or ''
        profile.save(update_fields=['mobile'])

        DashboardStats.objects.get_or_create(user=user)

        return Response({
            "code": 200,
            "msg": "创建成功",
            "data": {
                "id": user.id
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"创建用户失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user(request):
    """账户管理：更新用户"""
    user_id = request.data.get('id')
    if not user_id:
        return Response({
            "code": 400,
            "msg": "用户ID不能为空"
        }, status=status.HTTP_200_OK)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "code": 404,
            "msg": "用户不存在"
        }, status=status.HTTP_200_OK)

    try:
        user_name = request.data.get('userName') or request.data.get('username')
        user_phone = request.data.get('userPhone') or request.data.get('phone')
        user_email = request.data.get('userEmail') or request.data.get('email')
        user_gender = request.data.get('userGender') or request.data.get('gender')
        user_roles = request.data.get('userRoles') or request.data.get('role')
        status_value = request.data.get('status')
        new_password = request.data.get('password')

        if user_name and user_name != user.username and User.objects.filter(username=user_name).exists():
            return Response({
                "code": 400,
                "msg": "用户名已存在"
            }, status=status.HTTP_200_OK)

        if user_name:
            user.username = user_name
        if user_phone is not None:
            user.last_name = user_phone
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.mobile = user_phone
            profile.save(update_fields=['mobile'])
        if user_email is not None:
            user.email = user_email
        if user_gender is not None:
            user.first_name = _normalize_gender_label(user_gender)
        if status_value is not None:
            user.is_active = str(status_value) != '4'
        if isinstance(user_roles, list):
            user.is_staff = 'R_ADMIN' in user_roles
        if new_password:
            user.set_password(new_password)

        user.save()

        return Response({
            "code": 200,
            "msg": "更新成功",
            "data": {
                "id": user.id
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "code": 500,
            "msg": f"更新用户失败: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    """账户管理：注销用户（软删除）"""
    user_id = request.data.get('id')
    if not user_id:
        return Response({
            "code": 400,
            "msg": "用户ID不能为空"
        }, status=status.HTTP_200_OK)

    if str(request.user.id) == str(user_id):
        return Response({
            "code": 400,
            "msg": "不能注销当前登录账户"
        }, status=status.HTTP_200_OK)

    try:
        with transaction.atomic():
            user = User.objects.select_related('profile').get(id=user_id)
            user.is_active = False
            user.last_name = ''
            user.save(update_fields=['is_active', 'last_name'])

            if hasattr(user, 'profile'):
                user.profile.mobile = ''
                user.profile.save(update_fields=['mobile'])
    except User.DoesNotExist:
        return Response({
            "code": 404,
            "msg": "用户不存在"
        }, status=status.HTTP_200_OK)

    return Response({
        "code": 200,
        "msg": "注销成功"
    }, status=status.HTTP_200_OK)

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

        queryset = DroneDevice.objects.filter(owner=request.user)
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
                "image": item.image,
                "streamUrl": item.stream_url,
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
        image = request.data.get('image', '')
        stream_url = request.data.get('streamUrl', '')
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
            owner=request.user,
            ship_type=ship_type,
            length=int(length),
            model=model,
            weight=float(weight),
            functions=functions,
            image=image,
            stream_url=stream_url,
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
def update_drone(request):
    """更新无人船设备"""
    device_id = request.data.get('id')
    if not device_id:
        return Response({
            "code": 400,
            "msg": "设备ID不能为空"
        }, status=status.HTTP_200_OK)

    try:
        device = DroneDevice.objects.get(id=device_id, owner=request.user)
    except DroneDevice.DoesNotExist:
        return Response({
            "code": 404,
            "msg": "设备不存在"
        }, status=status.HTTP_200_OK)

    ship_type = request.data.get('shipType')
    length = request.data.get('length')
    model = request.data.get('model')
    weight = request.data.get('weight')
    functions = request.data.get('functions')
    image = request.data.get('image', '')
    stream_url = request.data.get('streamUrl', '')
    status_value = request.data.get('status')
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

    device.ship_type = ship_type
    device.length = int(length)
    device.model = model
    device.weight = float(weight)
    device.functions = functions
    device.image = image
    device.stream_url = stream_url
    device.max_speed = float(max_speed)
    if status_value in ['online', 'offline']:
        device.status = status_value
    device.save()

    return Response({
        "code": 200,
        "msg": "更新成功",
        "data": {
            "id": str(device.id)
        }
    }, status=status.HTTP_200_OK)


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

    deleted, _ = DroneDevice.objects.filter(id=device_id, owner=request.user).delete()
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

    deleted, _ = DroneDevice.objects.filter(id__in=ids, owner=request.user).delete()

    return Response({
        "code": 200,
        "msg": "删除成功",
        "data": {
            "deleted": deleted
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_drone_image(request):
    """上传无人船照片"""
    file = request.FILES.get('file')
    if not file:
        return Response({
            "code": 400,
            "msg": "请选择要上传的图片"
        }, status=status.HTTP_200_OK)

    if not file.content_type or not file.content_type.startswith('image/'):
        return Response({
            "code": 400,
            "msg": "仅支持图片文件"
        }, status=status.HTTP_200_OK)

    ext = os.path.splitext(file.name)[1] or '.jpg'
    filename = f"drone/{uuid4().hex}{ext.lower()}"
    saved_path = default_storage.save(filename, file)
    image_url = default_storage.url(saved_path)

    if not image_url.startswith('http'):
        image_url = request.build_absolute_uri(image_url)

    return Response({
        "code": 200,
        "msg": "上传成功",
        "data": {
            "url": image_url
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




