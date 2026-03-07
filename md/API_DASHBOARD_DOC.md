# Seabot 仪表板 API 文档

## 概述

本文档详细描述了 Seabot 项目中"工作台"（Dashboard）仪表板与 Django 后端之间的 API 接口规范。

**基础 URL**: `http://localhost:8000/api`

**认证方式**: JWT Token（Bearer Token）

---

## 目录

1. [认证接口](#认证接口)
2. [仪表板数据接口](#仪表板数据接口)
3. [响应格式规范](#响应格式规范)
4. [错误处理](#错误处理)
5. [集成指南](#集成指南)

---

## 认证接口

### 1. 用户注册

**端点**: `POST /api/register/`

**功能**: 注册新用户

**请求参数**:
```json
{
  "userName": "string",        // 用户名（3-30个字符）
  "password": "string",        // 密码（至少6个字符）
  "confirmPassword": "string"  // 确认密码（必须与password相同）
}
```

**成功响应 (201)**:
```json
{
  "code": 200,
  "msg": "注册成功，请登录",
  "data": {
    "userId": 1,
    "userName": "username"
  }
}
```

**错误响应**:
- `400`: 用户名或密码格式错误
- `500`: 注册失败

---

### 2. 用户登录

**端点**: `POST /api/login/`

**功能**: 用户登录，获取访问令牌

**请求参数**:
```json
{
  "userName": "string",  // 用户名
  "password": "string"   // 密码
}
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**错误响应**:
- `401`: 用户名或密码错误

**使用说明**:
- 将 `token` 保存到本地存储
- 在后续请求的 `Authorization` 头中使用: `Authorization: Bearer <token>`
- 当 token 过期时，使用 `refreshToken` 获取新的 `token`

---

### 3. 获取用户信息

**端点**: `GET /api/user/info/`

**功能**: 获取当前登录用户的基本信息

**认证**: ✅ 需要 JWT Token

**请求头**:
```
Authorization: Bearer <token>
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "userId": 1,
    "userName": "admin",
    "email": "admin@example.com",
    "avatar": "",
    "roles": ["R_ADMIN"],
    "buttons": []
  }
}
```

---

### 4. 获取菜单列表

**端点**: `GET /api/v3/system/menus/`

**功能**: 获取菜单列表，用于前端动态路由

**认证**: ✅ 需要 JWT Token

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
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
      "children": [...]
    }
  ]
}
```

---

## 仪表板数据接口

### 1. 获取仪表板统计数据

**端点**: `GET /api/dashboard/stats/`

**功能**: 获取仪表板统计信息（总任务数、完成数、活跃项目、销售额等）

**认证**: ✅ 需要 JWT Token

**请求头**:
```
Authorization: Bearer <token>
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "totalTasks": 128,           // 总任务数
    "completedTasks": 96,        // 已完成任务数
    "activeProjects": 12,        // 活跃项目数
    "totalSales": 45600.50,      // 总销售额
    "newUsersCount": 256,        // 新用户数
    "updatedAt": "2024-02-20T10:30:45.123Z"  // 更新时间
  }
}
```

**前端使用示例**:
```typescript
import { fetchDashboardStats } from '@/api/dashboard'

const loadStats = async () => {
  const response = await fetchDashboardStats()
  if (response.code === 200) {
    const { totalTasks, completedTasks, activeProjects, totalSales } = response.data
    // 使用这些数据更新卡片组件
  }
}
```

---

### 2. 获取销售数据

**端点**: `GET /api/dashboard/sales/`

**功能**: 获取月度销售数据，用于销售概览图表

**认证**: ✅ 需要 JWT Token

**请求头**:
```
Authorization: Bearer <token>
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "month": "1月",
      "sales": 5000
    },
    {
      "month": "2月",
      "sales": 6500
    },
    {
      "month": "3月",
      "sales": 4500
    },
    {
      "month": "4月",
      "sales": 7200
    },
    {
      "month": "5月",
      "sales": 8100
    },
    {
      "month": "6月",
      "sales": 9200
    }
  ]
}
```

**前端使用示例**:
```typescript
import { fetchSalesData } from '@/api/dashboard'

const loadSalesData = async () => {
  const response = await fetchSalesData()
  if (response.code === 200) {
    // 返回的 data 可直接用于 ECharts
    const chartData = response.data.map(item => item.sales)
    const xAxisData = response.data.map(item => item.month)
  }
}
```

---

### 3. 获取用户增长数据

**端点**: `GET /api/dashboard/growth/`

**功能**: 获取用户增长趋势数据，用于用户增长图表

**认证**: ✅ 需要 JWT Token

**请求头**:
```
Authorization: Bearer <token>
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "date": "2024-01-01",
      "newUsers": 50,      // 新增用户数
      "activeUsers": 300   // 活跃用户数
    },
    {
      "date": "2024-01-08",
      "newUsers": 65,
      "activeUsers": 350
    },
    {
      "date": "2024-01-15",
      "newUsers": 45,
      "activeUsers": 380
    },
    {
      "date": "2024-01-22",
      "newUsers": 80,
      "activeUsers": 420
    },
    {
      "date": "2024-01-29",
      "newUsers": 95,
      "activeUsers": 480
    },
    {
      "date": "2024-02-05",
      "newUsers": 70,
      "activeUsers": 530
    }
  ]
}
```

**前端使用示例**:
```typescript
import { fetchUserGrowth } from '@/api/dashboard'

const loadUserGrowth = async () => {
  const response = await fetchUserGrowth()
  if (response.code === 200) {
    // 提取活跃用户数用于绘图
    const activeUsersData = response.data.map(item => item.activeUsers)
    const dates = response.data.map(item => {
      const date = new Date(item.date)
      return `${date.getMonth() + 1}-${date.getDate()}`
    })
  }
}
```

---

### 4. 获取用户活动日志

**端点**: `GET /api/dashboard/activity/`

**功能**: 获取用户的最近活动日志

**认证**: ✅ 需要 JWT Token

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `limit` | integer | 10 | 返回的记录数 |

**请求示例**:
```
GET /api/dashboard/activity/?limit=8
```

**成功响应 (200)**:
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": [
    {
      "id": 1,
      "activityType": "login",                    // 活动类型
      "description": "admin 登录成功",
      "createdAt": "2024-02-20T10:30:45.123Z"
    },
    {
      "id": 2,
      "activityType": "task_completed",
      "description": "完成了任务：完善数据面板",
      "createdAt": "2024-02-20T09:15:30.456Z"
    },
    {
      "id": 3,
      "activityType": "file_uploaded",
      "description": "上传了文件：report.pdf",
      "createdAt": "2024-02-20T08:00:00.000Z"
    }
  ]
}
```

**活动类型说明**:
- `login`: 用户登录
- `task_completed`: 任务完成
- `project_created`: 项目创建
- `file_uploaded`: 文件上传
- `other`: 其他

**前端使用示例**:
```typescript
import { fetchUserActivity } from '@/api/dashboard'

const loadUserActivity = async () => {
  const response = await fetchUserActivity(8)
  if (response.code === 200) {
    const activityList = response.data
    // 渲染活动列表
  }
}
```

---

## 响应格式规范

### 成功响应格式

所有成功响应遵循以下格式：

```json
{
  "code": 200,
  "msg": "操作成功提示信息",
  "data": {
    // 具体数据
  }
}
```

### 失败响应格式

所有失败响应遵循以下格式：

```json
{
  "code": 400,
  "msg": "错误提示信息"
}
```

### HTTP 状态码说明

| 状态码 | 说明 |
|--------|------|
| `200` | 请求成功 |
| `201` | 资源创建成功 |
| `400` | 请求参数错误 |
| `401` | 未授权（缺少或无效的 Token） |
| `403` | 禁止访问 |
| `404` | 资源不存在 |
| `500` | 服务器内部错误 |

---

## 错误处理

### 常见错误码

| 错误码 | 说明 | 处理方案 |
|--------|------|---------|
| `400` | 用户名或密码格式错误 | 检查输入数据 |
| `401` | Token 过期或无效 | 重新登录或刷新 Token |
| `403` | 没有访问权限 | 检查用户角色 |
| `500` | 服务器内部错误 | 联系管理员 |

### Token 过期处理

当收到 `401` 错误时，使用 `refreshToken` 获取新的 `token`：

```typescript
const refreshAccessToken = async (refreshToken: string) => {
  try {
    // 此处假设有一个 refresh 端点
    const response = await request.post({
      url: '/api/token/refresh/',
      data: { refresh: refreshToken }
    })
    
    if (response.code === 200) {
      // 保存新的 token
      localStorage.setItem('token', response.data.token)
      // 重试之前的请求
      return true
    }
  } catch (error) {
    // 刷新失败，需要重新登录
    redirectToLogin()
  }
}
```

---

## 集成指南

### 前端集成步骤

#### 1. 安装依赖

确保项目已安装必要的依赖：
```bash
npm install axios # 或使用 pnpm install
```

#### 2. 创建 HTTP 请求工具

已在 `src/utils/http/index.ts` 中创建，配置了拦截器处理 JWT Token。

#### 3. 创建 API 模块

已在 `src/api/dashboard.ts` 中创建仪表板 API 模块：

```typescript
// src/api/dashboard.ts
import request from '@/utils/http'

export function fetchDashboardStats() {
  return request.get({
    url: '/api/dashboard/stats/'
  })
}
```

#### 4. 在组件中使用

```typescript
<script setup lang="ts">
import { onMounted } from 'vue'
import { fetchDashboardStats } from '@/api/dashboard'

const loadData = async () => {
  const response = await fetchDashboardStats()
  if (response.code === 200) {
    // 使用数据
    console.log(response.data)
  }
}

onMounted(() => {
  loadData()
})
</script>
```

### 后端集成步骤

#### 1. 数据库迁移

创建模型后运行迁移：

```bash
cd back-end/seadrone
python manage.py makemigrations
python manage.py migrate
```

#### 2. 创建测试数据

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from accounts.models import DashboardStats, UserActivity

# 创建测试用户
user = User.objects.create_user(username='testuser', password='123456')

# 创建统计数据
stats = DashboardStats.objects.create(
    user=user,
    total_tasks=100,
    completed_tasks=80,
    active_projects=10,
    total_sales=50000.00,
    new_users_count=200
)

# 创建活动日志
activity = UserActivity.objects.create(
    user=user,
    activity_type='login',
    description='用户登录成功'
)
```

#### 3. 启动服务

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 常见问题

### Q1: 如何处理跨域问题？

A: Django 已配置 CORS 中间件，允许来自 `http://localhost:5173` 的请求。

### Q2: Token 有效期是多长？

A: 根据 `settings.py` 配置：
- `ACCESS_TOKEN_LIFETIME`: 1小时
- `REFRESH_TOKEN_LIFETIME`: 7天

### Q3: 如何添加新的仪表板统计字段？

A: 在 `accounts/models.py` 的 `DashboardStats` 模型中添加新字段，然后运行迁移。

### Q4: 后端如何实时更新统计数据？

A: 当用户执行操作（如完成任务）时，在对应的视图中更新 `DashboardStats` 模型。

---

## 技术栈

### 后端

- **框架**: Django 5.2.10
- **API**: Django REST Framework
- **认证**: djangorestframework-simplejwt
- **跨域**: django-cors-headers
- **数据库**: SQLite3（开发）

### 前端

- **框架**: Vue 3
- **UI 框架**: Element Plus
- **HTTP 客户端**: Axios
- **构建工具**: Vite
- **图表**: ECharts

---

## 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2024-02-20 | 初始版本 |

---

## 联系方式

如有问题或建议，请联系开发团队。

---

**最后更新**: 2024年2月20日
