# 🌊 无人船监测系统

一个完整的无人船监测系统，包含 Vue 3 前端和 Django 后端。

## 📱 快速导航

### 📚 文档
- **项目完整说明**：查看 [项目使用说明.md](项目使用说明.md)
- **Python 代码说明**：查看 [back-end/Python代码说明.md](back-end/Python代码说明.md)

### 🚀 快速开始

#### 方式 1：使用启动脚本（推荐）
```bash
# 查看交互式菜单
bash start.sh
```

#### 方式 2：手动启动

**启动后端：**
```bash
cd back-end/seadrone
source ../../.venv/bin/activate
python3 manage.py runserver 0.0.0.0:8000
```

**启动前端：**
```bash
cd art-design-pro
pnpm dev
```

### 🔗 重要链接

| 服务 | 地址 | 描述 |
|------|------|------|
| 🎨 前端应用 | http://localhost:5173 | Vue 3 + Element Plus UI |
| 📡 后端 API | http://localhost:8000/api/ | Django REST Framework |
| ⚙️ 后台管理 | http://localhost:8000/admin/ | Django 管理后台 |
| 📚 文档中心 | http://localhost:5173/#/docs | 在线文档（启动前端后） |

### 📋 创建示例数据
bash start.sh
```bash
cd back-end/seadrone
source ../../.venv/bin/activate

# 创建仪表板数据
python3 create_dashboard_data.py

# 创建示例设备
python3 create_sample_devices.py

# 创建监测数据
python3 create_monitoring_data.py
```

## 🏗️ 项目结构

```
seabot/
├── art-design-pro/          # 前端项目（Vue 3 + TypeScript）
├── back-end/                # 后端项目（Django + DRF）
│   └── seadrone/
│       ├── accounts/        # 用户认证和仪表板
│       └── monitoring/      # 数据监测（水质、营养盐）
├── 项目使用说明.md          # 完整项目说明
└── start.sh                 # 快速启动脚本
```

## 🔐 默认用户

### 管理员账户
需要通过以下命令创建：
```bash
cd back-end/seadrone
source ../../.venv/bin/activate
python3 manage.py createsuperuser
```

## 📡 API 快速参考

### 用户认证
- `POST /api/register/` - 注册
- `POST /api/login/` - 登录
- `GET /api/user/info/` - 获取用户信息

### 仪表板
- `GET /api/dashboard/stats/` - 统计数据
- `GET /api/dashboard/sales/` - 销售数据
- `GET /api/dashboard/growth/` - 用户增长

### 监测数据
- `GET /api/analysis/water-quality/` - 水质数据
- `GET /api/analysis/nutrient/` - 营养盐数据
- `POST /api/upload/water-quality/` - 上传水质
- `POST /api/upload/nutrient/` - 上传营养盐

### 设备管理
- `GET /api/drone/list/` - 设备列表
- `POST /api/drone/create/` - 创建设备
- `POST /api/drone/delete/` - 删除设备
- `POST /api/drone/batch-delete/` - 批量删除

## 🛠️ 常用命令

```bash
# Django 迁移
python3 manage.py makemigrations
python3 manage.py migrate

# 创建超级用户
python3 manage.py createsuperuser

# Django Shell
python3 manage.py shell

# 查看数据库用户
python3 check_users.py

# 运行测试
bash test_register.sh
python3 test_upload.py
```

## 📚 完整文档

更详细的信息请参考：

1. **[项目使用说明.md](项目使用说明.md)** - 完整的项目结构、API 文档、开发工作流
2. **[back-end/Python代码说明.md](back-end/Python代码说明.md)** - Python 后端代码详解
3. **前端文档中心** - 访问 http://localhost:5173/#/docs（启动前端后）

## 🐛 常见问题

### 端口被占用
```bash
# 查找占用端口的进程
lsof -i :8000

# 删除数据库重新初始化
rm back-end/seadrone/db.sqlite3
cd back-end/seadrone
python3 manage.py migrate
python3 create_monitoring_data.py
```

### 数据库错误
```bash
cd back-end/seadrone
python3 manage.py flush
python3 manage.py migrate
```

## 🎯 技术栈

**前端：**
- Vue 3
- TypeScript
- Element Plus
- Vite
- Pinia
- Axios

**后端：**
- Django 5.2
- Django REST Framework
- djangorestframework-simplejwt
- django-cors-headers
- SQLite3

## 📝 开发模式

项目支持热更新：

**前端热更新：**
```bash
cd art-design-pro
pnpm dev
# 修改代码后自动刷新
```

**后端自动重载：**
```bash
cd back-end/seadrone
python3 manage.py runserver
# Django 会自动检测文件变化
```

## 📞 获取帮助

1. 查看在线文档：http://localhost:5173/#/docs
2. 查看项目说明：[项目使用说明.md](项目使用说明.md)
3. 检查后端日志：Django 输出显示详细的错误信息

---

**Happy Coding! 🚀**
