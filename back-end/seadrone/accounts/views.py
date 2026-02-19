# accounts/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

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