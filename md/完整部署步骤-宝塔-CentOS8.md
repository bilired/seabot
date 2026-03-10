# SeaBoat 完整部署步骤（宝塔 + CentOS 8）

本文档基于以下实际环境整理：

- 面板：宝塔面板
- 系统：CentOS 8.x
- 项目目录：`/www/wwwroot/seabot`
- 前端：Vue3 + Vite（静态文件）
- 后端：Django + Gunicorn
- 数据库：MySQL 8

> 重点说明：此项目不是 PHP 项目。宝塔里可以用“添加 PHP 站点”创建网站壳，但实际要按“静态前端 + Python 后端”部署，PHP 不参与运行。

---

## 1. 在宝塔面板创建站点

1. 打开 `网站` -> `添加站点`
2. 填你的域名（如 `yunpingtai.cc`、`www.yunpingtai.cc`）
3. 根目录先可设为：`/www/wwwroot/seabot/art-design-pro/dist`
4. PHP 版本选择“纯静态”或不启用 PHP
5. 提交创建

可选：在该站点申请 SSL（Let's Encrypt），后续 Nginx 配置可再加 443。

---

## 2. 在宝塔创建 MySQL 数据库

1. 打开 `数据库` -> `MySQL` -> `添加数据库`
2. 建议：
- 数据库名：`seaboat_prod`
- 用户名：`seaboat_user`
- 密码：强密码（保存好）
- 权限：本机

---

## 3. 上传项目代码到服务器

项目最终应位于：`/www/wwwroot/seabot`

示例（SSH）：

```bash
cd /www/wwwroot
# 二选一
# git clone <你的仓库地址> seabot
# 或宝塔文件管理上传压缩包并解压成 seabot
```

---

## 4. 安装系统依赖

```bash
dnf install -y gcc gcc-c++ make git wget curl \
openssl-devel bzip2-devel libffi-devel zlib-devel \
xz-devel readline-devel sqlite-devel tk-devel \
mysql-devel pkgconfig
```

检查基础版本：

```bash
python --version
node -v
pnpm -v
mysql --version
nginx -v 2>&1
```

---

## 5. 创建 Python 虚拟环境（避开 /www noexec 坑）

部分宝塔机器 `/www` 挂载了 `noexec`，会导致 `/www/.../venv/bin/python: Permission denied`。

先检查：

```bash
mount | grep " /www "
```

如果包含 `noexec`，请把虚拟环境放到 `/opt`（推荐）：

```bash
/usr/bin/python -m venv /opt/seabot-venv
source /opt/seabot-venv/bin/activate
```

如果不含 `noexec`，可放项目内：

```bash
cd /www/wwwroot/seabot
python -m venv venv
source /www/wwwroot/seabot/venv/bin/activate
```

统一安装依赖：

```bash
pip install -U pip setuptools wheel
pip install -r /www/wwwroot/seabot/back-end/requirements.txt
```

验证：

```bash
python -V
pip list | grep -E "Django|djangorestframework|simplejwt|cors-headers|gunicorn|mysqlclient"
```

---

## 6. 准备环境变量 `.env`

```bash
cd /www/wwwroot/seabot
cp -n .env.example .env
```

编辑 `.env`，至少确认这些键：

```env
SECRET_KEY=<用 python 生成>
DB_PASSWORD=<数据库密码>
DB_NAME=seaboat_prod
DB_USER=seaboat_user
DB_HOST=127.0.0.1
DB_PORT=3306
DJANGO_SETTINGS_MODULE=seadrone.settings_prod
PROJECT_ROOT=/www/wwwroot/seabot
```

生成 `SECRET_KEY`：

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 7. 后端初始化（迁移、静态、管理员）

```bash
# 激活虚拟环境（按你的实际路径）
# source /opt/seabot-venv/bin/activate
# 或 source /www/wwwroot/seabot/venv/bin/activate

cd /www/wwwroot/seabot
set -a
source .env
set +a

export DJANGO_SETTINGS_MODULE=seadrone.settings_prod
export PROJECT_ROOT=/www/wwwroot/seabot

mkdir -p /www/wwwroot/seabot/logs
mkdir -p /www/wwwroot/seabot/media
touch /www/wwwroot/seabot/logs/django.log \
      /www/wwwroot/seabot/logs/gunicorn_access.log \
      /www/wwwroot/seabot/logs/gunicorn_error.log

cd /www/wwwroot/seabot/back-end/seadrone
python manage.py migrate --settings=seadrone.settings_prod
python manage.py collectstatic --noinput --settings=seadrone.settings_prod
python manage.py createsuperuser --settings=seadrone.settings_prod
```

---

## 8. 先手动试跑 Gunicorn

```bash
# 仍在 /www/wwwroot/seabot/back-end/seadrone
gunicorn seadrone.wsgi:application --bind 127.0.0.1:8000 --workers 4
```

无报错即后端可运行，按 `Ctrl + C` 停止。

---

## 9. 配置 systemd 守护 Gunicorn

创建文件：`/etc/systemd/system/seaboat-gunicorn.service`

如果你的虚拟环境在 `/opt/seabot-venv`，用下面这份：

```ini
[Unit]
Description=SeaBoat Gunicorn
After=network.target mysqld.service

[Service]
User=www
Group=www
WorkingDirectory=/www/wwwroot/seabot/back-end/seadrone
Environment="PATH=/opt/seabot-venv/bin"
Environment="DJANGO_SETTINGS_MODULE=seadrone.settings_prod"
Environment="PROJECT_ROOT=/www/wwwroot/seabot"
EnvironmentFile=/www/wwwroot/seabot/.env
ExecStart=/opt/seabot-venv/bin/gunicorn \
  --workers 4 \
  --bind unix:/www/wwwroot/seabot/gunicorn.sock \
  --access-logfile /www/wwwroot/seabot/logs/gunicorn_access.log \
  --error-logfile /www/wwwroot/seabot/logs/gunicorn_error.log \
  seadrone.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
systemctl daemon-reload
systemctl enable seaboat-gunicorn
systemctl start seaboat-gunicorn
systemctl status seaboat-gunicorn --no-pager
```

---

## 10. 构建前端

```bash
cd /www/wwwroot/seabot/art-design-pro
pnpm install
pnpm build
ls -l /www/wwwroot/seabot/art-design-pro/dist/index.html
```

---

## 11. 配置宝塔站点 Nginx

在宝塔：`网站 -> 对应站点 -> 配置文件`，替换为类似如下（按域名改）：

```nginx
server {
    listen 80;
    server_name yunpingtai.cc www.yunpingtai.cc;

    root /www/wwwroot/seabot/art-design-pro/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://unix:/www/wwwroot/seabot/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /media/ {
        alias /www/wwwroot/seabot/media/;
    }

    location /static/ {
        alias /www/wwwroot/seabot/static/;
    }
}
```

保存后：

```bash
nginx -t
systemctl reload nginx
```

---

## 12. 验证部署

```bash
# Gunicorn 服务状态
systemctl status seaboat-gunicorn --no-pager

# Nginx 状态
systemctl status nginx --no-pager

# 看日志
tail -n 100 /www/wwwroot/seabot/logs/django.log
journalctl -u seaboat-gunicorn -n 100 --no-pager
```

浏览器访问：

- 前端首页：`http://你的域名`（或 https）
- Django Admin：`http://你的域名/admin`

---

## 13. 常见问题速查

### 13.1 `Permission denied: /www/wwwroot/.../venv/bin/python`

原因：`/www` 分区 `noexec`。

处理：把虚拟环境放到 `/opt/seabot-venv`，并在 systemd 的 `PATH` 与 `ExecStart` 使用 `/opt/seabot-venv/bin/...`。

### 13.2 `ModuleNotFoundError: alibabacloud_dypnsapi20170525`

原因：装错包（`dysms` 与 `dypns` 混淆）。

处理：

```bash
pip install -U alibabacloud_dypnsapi20170525 alibabacloud_credentials alibabacloud_tea_openapi alibabacloud_tea_util
```

### 13.3 `Unable to configure handler 'django_file'`

原因：日志目录不存在或 `PROJECT_ROOT` 未设置。

处理：

```bash
export PROJECT_ROOT=/www/wwwroot/seabot
mkdir -p /www/wwwroot/seabot/logs
```

### 13.4 宝塔里显示“PHP项目”是否有问题

没有问题，站点只是壳。关键是 Nginx 配置是否指向前端静态 + `/api/` 反代 Gunicorn。

---

## 14. 运维常用命令

```bash
# 重启后端
systemctl restart seaboat-gunicorn

# 重载 Nginx
systemctl reload nginx

# 看 Gunicorn 实时日志
journalctl -u seaboat-gunicorn -f

# 前端更新
cd /www/wwwroot/seabot/art-design-pro
pnpm build

# 后端更新
cd /www/wwwroot/seabot
# git pull 后
source /opt/seabot-venv/bin/activate  # 若你用 /opt venv
pip install -r back-end/requirements.txt
cd back-end/seadrone
python manage.py migrate --settings=seadrone.settings_prod
systemctl restart seaboat-gunicorn
```
