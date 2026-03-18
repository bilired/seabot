# 无人船监测系统

一个前后端一体的无人船监测项目，前端基于 Vue 3 + TypeScript，后端基于 Django + DRF。

## 项目状态（2026-03）

当前主干已包含以下能力：

- 用户注册、登录、JWT 鉴权
- 用户管理（列表、创建、编辑、注销）
- 个人中心：头像上传、基础信息持久化（刷新不丢失）
- 独立修改密码页（旧密码 + 短信验证码 + 新密码二次确认）
- 无人船设备管理
- 图片上传与图片传输历史管理（查询、查看、删除、批量删除）
- 水质/营养盐分析数据接口与上传接口

## 目录结构

```text
seabot/
├── art-design-pro/                  # 前端（Vue 3 + Vite + Element Plus）
├── back-end/
│   ├── test_upload_boat_images.py   # 本地图片批量上传测试脚本
│   └── seadrone/
│       ├── accounts/                # 认证、用户、设备、图片历史等 API
│       ├── monitoring/              # 监测数据与船端网关相关 API
│       ├── manage.py
│       └── db.sqlite3
├── README.md
└── start.sh
```

## 本地开发启动

### 1) 后端

```bash
cd /Users/hanksgao/Desktop/seabot/back-end/seadrone

# 使用项目虚拟环境
source /Users/hanksgao/Desktop/seabot/.venv/bin/activate

# 迁移数据库
/Users/hanksgao/Desktop/seabot/.venv/bin/python manage.py migrate

# 启动服务
/Users/hanksgao/Desktop/seabot/.venv/bin/python manage.py runserver 0.0.0.0:8000
```

### 2) 前端

```bash
cd /Users/hanksgao/Desktop/seabot/art-design-pro

# 安装依赖（首次）
pnpm install

# 启动开发服务
pnpm dev
```

如果你的环境没有 `pnpm`，可改用：

```bash
npm install
npm run dev
```

## 访问地址

- 前端：`http://localhost:5173`
- 后端 API 根：`http://localhost:8000/api/`
- Django Admin：`http://localhost:8000/admin/`

## 常用账号初始化

创建后台管理员：

```bash
cd /Users/hanksgao/Desktop/seabot/back-end/seadrone
/Users/hanksgao/Desktop/seabot/.venv/bin/python manage.py createsuperuser
```

## 关键 API 速查

### 认证与用户

- `POST /api/register/`
- `POST /api/login/`
- `GET /api/user/info/`
- `POST /api/user/profile/update/`
- `POST /api/user/avatar/upload/`

### 修改密码（独立流程）

- `POST /api/user/password/sms/send/`
- `POST /api/user/password/sms/verify/`
- `POST /api/user/password/change/`

### 设备与图片历史

- `GET /api/drone/list/`
- `POST /api/drone/create/`
- `POST /api/drone/update/`
- `POST /api/drone/delete/`
- `POST /api/drone/batch-delete/`
- `POST /api/drone/upload-image/`
- `GET /api/drone/image-history/list/`
- `POST /api/drone/image-history/delete/`
- `POST /api/drone/image-history/batch-delete/`

### 监测数据

- `GET /api/analysis/water-quality/`
- `GET /api/analysis/nutrient/`
- `POST /api/upload/water-quality/`
- `POST /api/upload/nutrient/`
- `POST /api/upload/ship-packet/`

## 图片上传测试（本地目录 -> 后端）

脚本：`back-end/test_upload_boat_images.py`

示例：

```bash
/Users/hanksgao/Desktop/seabot/.venv/bin/python /Users/hanksgao/Desktop/seabot/back-end/test_upload_boat_images.py \
	--base-url http://127.0.0.1:8000/api \
	--username your_user \
	--password your_pass \
	--image-dir ~/Desktop/boat-image \
	--ship-model DL-3022 \
	--check-history
```

## 常见问题

### 1) `migrate` 提示 models changed but no migration

```bash
cd /Users/hanksgao/Desktop/seabot/back-end/seadrone
/Users/hanksgao/Desktop/seabot/.venv/bin/python manage.py makemigrations accounts
/Users/hanksgao/Desktop/seabot/.venv/bin/python manage.py migrate
```

### 2) 个人中心刷新后数据丢失

请确认以下三点：

- 已应用包含 `UserProfile` 扩展字段的迁移（`0011`）
- 后端已重启到最新代码
- 前端保存时接口返回成功（页面会提示“保存成功”）

可用以下命令检查迁移：

```bash
/Users/hanksgao/Desktop/seabot/.venv/bin/python /Users/hanksgao/Desktop/seabot/back-end/seadrone/manage.py showmigrations accounts
```

## 相关文档

- `项目使用说明.md`
- `back-end/Python代码说明.md`
- `md/` 目录下的专题文档（部署、联调、故障排查等）
