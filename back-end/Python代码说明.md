# back-end 文件夹 Python 代码说明

## 📁 文件夹结构

```
back-end/
├── seadrone/                    # Django 项目主目录
│   ├── manage.py               # Django 命令行工具
│   ├── db.sqlite3              # SQLite 数据库文件
│   ├── seadrone/               # 项目配置目录
│   │   ├── settings.py         # 项目设置（数据库、应用配置等）
│   │   ├── urls.py             # 主 URL 路由配置
│   │   ├── asgi.py             # ASGI 部署配置
│   │   └── wsgi.py             # WSGI 部署配置
│   │
│   ├── accounts/               # 用户认证应用
│   │   ├── models.py           # 数据模型
│   │   │   ├── DashboardStats  # 仪表板统计数据
│   │   │   ├── UserActivity    # 用户活动日志
│   │   │   ├── DroneDevice     # 无人船设备信息
│   │   │   ├── MonthlySalesData # 月销售数据
│   │   │   └── UserGrowthData  # 用户增长数据
│   │   ├── views.py            # API 视图函数
│   │   │   ├── register_view        # 用户注册
│   │   │   ├── login_view           # 用户登录
│   │   │   ├── DashboardStatsView   # 获取仪表板数据
│   │   │   ├── get_sales_data       # 获取销售数据
│   │   │   ├── get_user_growth      # 获取用户增长
│   │   │   ├── get_drone_list       # 获取设备列表
│   │   │   ├── create_drone         # 创建设备
│   │   │   ├── delete_drone         # 删除设备
│   │   │   └── batch_delete_drone   # 批量删除
│   │   ├── urls.py             # accounts 应用路由
│   │   ├── admin.py            # Django 后台管理
│   │   ├── apps.py             # 应用配置
│   │   ├── migrations/         # 数据库迁移文件
│   │   └── tests.py            # 单元测试
│   │
│   ├── monitoring/             # 数据监测应用（新增）
│   │   ├── models.py           # 监测数据模型
│   │   │   ├── WaterQualityData  # 水质监测数据
│   │   │   └── NutrientData      # 营养盐数据
│   │   ├── views.py            # API 视图函数
│   │   │   ├── get_water_quality_data    # 获取水质数据
│   │   │   ├── get_nutrient_data         # 获取营养盐数据
│   │   │   ├── upload_water_quality_data # 上传水质数据
│   │   │   └── upload_nutrient_data      # 上传营养盐数据
│   │   ├── urls.py             # monitoring 应用路由
│   │   ├── admin.py            # Django 后台管理
│   │   ├── apps.py             # 应用配置
│   │   ├── migrations/         # 数据库迁移文件
│   │   └── tests.py            # 单元测试
│   │
│   └── manage.py               # Django 管理脚本（项目根目录）
│
├── myenv/                      # Python 虚拟环境（已弃用）
├── .venv/                      # Python 虚拟环境（使用此环境）
├── create_dashboard_data.py    # 创建仪表板示例数据
├── create_sample_devices.py    # 创建示例设备
├── create_monitoring_data.py   # 创建监测数据示例
├── check_users.py              # 查看数据库用户
├── test_register.sh            # 测试注册功能
└── test_upload.py              # 测试数据上传
```

---

## 🔧 主要 Python 模块说明

### 1. Django 项目配置 (`seadrone/settings.py`)

**作用：** 项目全局配置

**关键配置：**
```python
# 已安装的应用
INSTALLED_APPS = [
    'rest_framework',      # Django REST Framework
    'corsheaders',         # CORS 支持
    'accounts',            # 用户认证应用
    'monitoring',          # 数据监测应用
]

# JWT 认证配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# CORS 跨域配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

### 2. 账户应用 (`accounts/`)

#### models.py - 数据模型

```python
# 仪表板统计
class DashboardStats(models.Model):
    user = OneToOneField(User)
    total_tasks = IntegerField()
    completed_tasks = IntegerField()
    active_projects = IntegerField()
    total_sales = FloatField()
    new_users_count = IntegerField()

# 用户活动日志
class UserActivity(models.Model):
    user = ForeignKey(User)
    activity_type = CharField()  # login, task_completed, etc.
    description = TextField()
    created_at = DateTimeField(auto_now_add=True)

# 无人船设备
class DroneDevice(models.Model):
    ship_type = CharField(max_length=100)
    length = FloatField()
    model = CharField(max_length=50)
    weight = FloatField()
    functions = TextField()
    status = CharField(choices=['online', 'offline'])
    max_speed = FloatField()

# 月销售数据
class MonthlySalesData(models.Model):
    month = CharField()
    sales = IntegerField()

# 用户增长数据
class UserGrowthData(models.Model):
    date = DateField()
    new_users = IntegerField()
    active_users = IntegerField()
```

#### views.py - API 视图

**认证相关：**
```python
def register_view(request):
    """用户注册 POST /api/register/"""
    # 检查用户是否存在
    # 创建新用户
    # 返回成功消息

def login_view(request):
    """用户登录 POST /api/login/"""
    # 验证用户名密码
    # 生成 JWT Token
    # 返回 access_token 和 refresh_token

def user_info_view(request):
    """获取用户信息 GET /api/user/info/"""
    # 需要有效的 access_token
    # 返回当前用户信息
```

**仪表板相关：**
```python
class DashboardStatsView(APIView):
    """获取仪表板统计数据 GET /api/dashboard/stats/"""
    def get(self, request):
        # 获取用户的 DashboardStats 对象
        # 返回统计数据 JSON

def get_sales_data(request):
    """获取销售数据 GET /api/dashboard/sales/"""
    # 查询 MonthlySalesData 表
    # 返回 12 个月的销售数据

def get_user_growth(request):
    """获取用户增长数据 GET /api/dashboard/growth/"""
    # 查询 UserGrowthData 表
    # 返回周期性的用户增长数据
```

**设备管理相关：**
```python
def get_drone_list(request):
    """获取设备列表 GET /api/drone/list/"""
    # 查询所有 DroneDevice
    # 返回设备列表

def create_drone(request):
    """创建设备 POST /api/drone/create/"""
    # 验证请求数据
    # 创建新 DroneDevice
    # 返回新设备信息

def delete_drone(request):
    """删除设备 POST /api/drone/delete/"""
    # 根据 ID 删除设备
    # 返回删除结果

def batch_delete_drone(request):
    """批量删除设备 POST /api/drone/batch-delete/"""
    # 根据 ID 列表删除多个设备
    # 返回删除结果
```

---

### 3. 监测应用 (`monitoring/`)

#### models.py - 监测数据模型

```python
# 水质监测数据
class WaterQualityData(models.Model):
    ship_model = CharField()              # 船型号
    temperature = FloatField()            # 水温
    ph = FloatField()                     # pH 值
    chlorophyll = FloatField()            # 叶绿素
    salinity = FloatField()               # 盐度
    dissolved_oxygen = FloatField()       # 溶解氧
    conductivity = FloatField()           # 电导率
    turbidity = FloatField()              # 浊度
    algae = IntegerField()                # 蓝绿藻
    warning_code = CharField()            # 警告码
    collection_time = DateTimeField()     # 采集时间
    connection_status = CharField()       # 连接状态

# 营养盐数据
class NutrientData(models.Model):
    ship_model = CharField()              # 船型号
    phosphate = FloatField()              # 磷酸盐
    phosphate_time = DateTimeField()
    ammonia = FloatField()                # 氨氮
    ammonia_time = DateTimeField()
    nitrate = FloatField()                # 硝酸盐
    nitrate_time = DateTimeField()
    nitrite = FloatField()                # 亚硝酸盐
    nitrite_time = DateTimeField()
    error_code1 = CharField()             # 错误码 1
    error_code2 = CharField()             # 错误码 2
    instrument_status = CharField()       # 仪器状态
    collection_time = DateTimeField()     # 采集时间
    connection_status = CharField()       # 连接状态
```

#### views.py - 监测数据 API

```python
def get_water_quality_data(request):
    """获取水质数据 GET /api/analysis/water-quality/"""
    # 查询最新 20 条水质记录
    # 格式化数据返回

def get_nutrient_data(request):
    """获取营养盐数据 GET /api/analysis/nutrient/"""
    # 查询最新 20 条营养盐记录
    # 格式化数据返回

def upload_water_quality_data(request):
    """上传水质数据 POST /api/upload/water-quality/"""
    # 接收无人船上传的水质数据
    # 验证和保存数据
    # 返回保存结果

def upload_nutrient_data(request):
    """上传营养盐数据 POST /api/upload/nutrient/"""
    # 接收无人船上传的营养盐数据
    # 验证和保存数据
    # 返回保存结果
```

---

## 🚀 常用 Python 脚本

### create_dashboard_data.py

**功能：** 创建 12 个月的销售数据和用户增长数据

**使用：**
```bash
python3 create_dashboard_data.py
```

**做了什么：**
- 创建 12 条 MonthlySalesData 记录
- 创建 10 条 UserGrowthData 记录
- 更新 DashboardStats 的统计数据

---

### create_sample_devices.py

**功能：** 创建示例设备

**使用：**
```bash
python3 create_sample_devices.py
```

**创建的设备：**
- DL-3026 - 海洋监测无人船
- DL-3022 - 浅水监测无人船

---

### create_monitoring_data.py

**功能：** 创建示例监测数据

**使用：**
```bash
python3 create_monitoring_data.py
```

**创建的数据：**
- 4 条水质监测记录
- 4 条营养盐数据记录

---

### check_users.py

**功能：** 查看数据库中的用户

**使用：**
```bash
python3 check_users.py
```

**输出：** 所有用户及其信息

---

### test_upload.py

**功能：** 测试数据上传接口

**使用：**
```bash
python3 test_upload.py
```

**测试内容：**
- 上传水质数据
- 上传营养盐数据
- 验证上传结果

---

## 🔐 认证和权限

### JWT 认证流程

```
1. 用户登录
   POST /api/login/
   返回：access_token, refresh_token

2. 使用 Token 请求 API
   GET /api/dashboard/stats/
   Header: Authorization: Bearer {access_token}

3. Token 过期时刷新
   POST /api/token/refresh/
   Body: {refresh_token}
   返回：新的 access_token
```

### 权限设置

- **无需认证：** 监测数据查询、数据上传
- **需要认证：** 仪表板数据、设备管理、用户信息

---

## 📝 Django 常用命令

```bash
# 进入后端目录
cd back-end/seadrone

# 激活虚拟环境
source ../../.venv/bin/activate

# 创建迁移
python3 manage.py makemigrations

# 应用迁移
python3 manage.py migrate

# 运行服务器
python3 manage.py runserver 8000

# 创建超级用户
python3 manage.py createsuperuser

# 进入 Django Shell
python3 manage.py shell

# 清空数据库
python3 manage.py flush

# 查看 SQL 语句
python3 manage.py sqlmigrate app_name migration_name
```

---

## 💡 快速开发工作流

### 添加新的 API 端点步骤

1. **创建模型** (models.py)
```python
class MyModel(models.Model):
    field1 = CharField()
    field2 = DateTimeField(auto_now_add=True)
```

2. **创建视图** (views.py)
```python
@api_view(['GET'])
def my_endpoint(request):
    data = MyModel.objects.all()
    return Response({
        'code': 200,
        'msg': 'success',
        'data': list(data.values())
    })
```

3. **添加路由** (urls.py)
```python
path('my-endpoint/', views.my_endpoint, name='my_endpoint'),
```

4. **创建迁移**
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

5. **前端调用** (src/api/dashboard.ts)
```typescript
export function fetchMyData() {
    return request.get({
        url: '/api/my-endpoint/'
    })
}
```

---

## 🐛 调试技巧

### 查看数据库内容

```bash
python3 manage.py shell

# 在 Django Shell 中
from accounts.models import DashboardStats
DashboardStats.objects.all()

from monitoring.models import WaterQualityData
WaterQualityData.objects.all()
```

### 查看 API 请求日志

在 settings.py 中启用日志：
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## 📚 相关文档链接

- [Django 官方文档](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
