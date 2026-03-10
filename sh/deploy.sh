#!/bin/bash

################################################################################
# SeaBoat 自动化部署脚本
# 用途：一键在宝塔面板服务器上部署前后端应用
# 系统：CentOS 8.2.2004 x86_64
# 域名：yunpingtai.cc
# 
# 使用方法：
#   bash deploy.sh
#
# 环境要求：
#   - Python 3.11+（需先在宝塔面板安装）
#   - Node.js 18+（通过宝塔软件商店安装）
#   - MySQL 8.0 / PostgreSQL
#   - Nginx
#
################################################################################

set -e  # 任何命令失败都退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

PROJECT_ROOT="$(pwd)"

# ===== 1. 环境检查 =====
log_info "===== 部署前检查 ====="

# 检查是否在正确目录
if [ ! -f "back-end/seadrone/manage.py" ] || [ ! -f "art-design-pro/package.json" ]; then
    log_error "请在项目根目录执行此脚本！"
    exit 1
fi

if [ ! -f ".env" ]; then
    log_error ".env 不存在，请先在项目根目录配置 .env"
    exit 1
fi

set -a
source .env
set +a

if [ -z "$DB_PASSWORD" ]; then
    log_error "DB_PASSWORD 未设置，请检查 .env"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    log_error "SECRET_KEY 未设置，请检查 .env"
    exit 1
fi

if [ -z "${ALIYUN_SMS_ACCESS_KEY_ID:-}" ]; then
    log_error "ALIYUN_SMS_ACCESS_KEY_ID 未设置，请检查 .env"
    exit 1
fi

if [ -z "${ALIYUN_SMS_ACCESS_KEY_SECRET:-}" ]; then
    log_error "ALIYUN_SMS_ACCESS_KEY_SECRET 未设置，请检查 .env"
    exit 1
fi

if [ -z "${ALIYUN_SMS_SIGN_NAME:-}" ]; then
    log_error "ALIYUN_SMS_SIGN_NAME 未设置，请检查 .env"
    exit 1
fi

if [ -z "${ALIYUN_SMS_TEMPLATE_CODE:-}" ]; then
    log_error "ALIYUN_SMS_TEMPLATE_CODE 未设置，请检查 .env"
    exit 1
fi

# 检查 Python 版本
if ! command -v python3.11 &> /dev/null; then
    log_warn "Python 3.11 未找到，尝试 python3..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3  未安装！"
        exit 1
    fi
    PYTHON_CMD=python3
else
    PYTHON_CMD=python3.11
fi

log_info "使用 Python: $PYTHON_CMD"
$PYTHON_CMD --version

# 检查 Node.js
if ! command -v node &> /dev/null; then
    log_error "Node.js 未安装！请在宝塔软件商店安装 Node.js 18+"
    exit 1
fi
log_info "Node.js 版本: $(node --version)"

# 检查 Nginx
if ! command -v nginx &> /dev/null; then
    log_error "Nginx 未安装！"
    exit 1
fi
log_info "Nginx 已安装"

# ===== 2. 后端部署 =====
log_info "===== 开始后端部署 ====="

# 2.1 创建虚拟环境
if [ ! -d "venv" ]; then
    log_info "创建虚拟环境..."
    $PYTHON_CMD -m venv venv
else
    log_info "虚拟环境已存在"
fi

# 2.2 激活虚拟环境并安装依赖
log_info "激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel

# 安装 Django 依赖
pip install Django==5.2.10
pip install djangorestframework==3.16.1
pip install djangorestframework-simplejwt==5.5.1
pip install django-cors-headers==4.9.0
pip install gunicorn==23.0.0
pip install mysqlclient==2.2.4
pip install psycopg2-binary==2.9.10  # PostgreSQL
pip install alibabacloud_dypnsapi20170525
pip install alibabacloud_credentials
pip install alibabacloud_tea_openapi
pip install alibabacloud_tea_util

# 2.3 后端环境变量
log_info "配置后端环境变量..."
export DJANGO_SETTINGS_MODULE=seadrone.settings_prod
if [ -z "${SMS_MOCK_ENABLED:-}" ]; then
    export SMS_MOCK_ENABLED=false
fi
log_info "已从 .env 加载数据库、Django 密钥与阿里云短信配置（SMS_MOCK_ENABLED=$SMS_MOCK_ENABLED）"

# 2.4 准备日志目录（必须在 Django 启动前）
log_info "创建日志目录和日志文件..."
mkdir -p "$PROJECT_ROOT/logs"
touch "$PROJECT_ROOT/logs/django.log" "$PROJECT_ROOT/logs/gunicorn_access.log" "$PROJECT_ROOT/logs/gunicorn_error.log"
chmod 755 "$PROJECT_ROOT/logs"
chmod 644 "$PROJECT_ROOT/logs"/*.log

# 2.5 数据库迁移
log_info "执行数据库迁移..."
cd back-end/seadrone
python manage.py migrate --settings=seadrone.settings_prod || {
    log_error "数据库迁移失败！请检查数据库配置"
    exit 1
}

# 2.6 创建超级用户（可选）
log_info "创建超级用户（输入用户名和密码）..."
python manage.py createsuperuser --settings=seadrone.settings_prod || {
    log_warn "超级用户创建失败或已跳过"
}

# 2.7 收集静态文件
log_info "收集静态文件..."
python manage.py collectstatic --noinput --settings=seadrone.settings_prod

# 2.8 测试 Gunicorn
log_info "测试 Gunicorn..."
gunicorn --version
log_info "Gunicorn 可以启动（将由 systemd 服务管理）"

# 返回项目根目录
cd ../..

# ===== 3. 前端部署 =====
log_info "===== 开始前端部署 ====="

cd art-design-pro

# 3.1 安装 Node.js 依赖
log_info "安装 Node.js 依赖（这可能需要几分钟）..."
npm install --registry=https://registry.npmmirror.com || pnpm install

# 3.2 构建生产版本（改为本地执行）
log_info "已跳过服务器构建步骤（npm run build）"
log_info "请先在本地构建并上传 art-design-pro/dist 到服务器"

if [ ! -d "dist" ]; then
    log_error "前端构建失败！请检查编译错误"
    exit 1
fi

log_info "前端构建成功！输出目录：dist/"

cd ..

# ===== 5. Gunicorn systemd 服务 =====
log_info "===== 配置 Gunicorn systemd 服务 ====="

cat > seaboat-gunicorn.service << 'EOF'
[Unit]
Description=SeaBoat Gunicorn Application Server
After=network.target mysql.service

[Service]
Type=notify
User=www
WorkingDirectory=__PROJECT_ROOT__/back-end/seadrone
Environment="PATH=__PROJECT_ROOT__/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=seadrone.settings_prod"
EnvironmentFile=__PROJECT_ROOT__/.env
ExecStart=__PROJECT_ROOT__/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:__PROJECT_ROOT__/gunicorn.sock \
    --access-logfile __PROJECT_ROOT__/logs/gunicorn_access.log \
    --error-logfile __PROJECT_ROOT__/logs/gunicorn_error.log \
    --log-level info \
    seadrone.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

sed -i "s#__PROJECT_ROOT__#$PROJECT_ROOT#g" seaboat-gunicorn.service

log_info "Gunicorn systemd 服务配置已生成：seaboat-gunicorn.service"
log_warn "请手动：sudo cp seaboat-gunicorn.service /etc/systemd/system/"
log_warn "然后执行：sudo systemctl daemon-reload && sudo systemctl enable seaboat-gunicorn"

# ===== 6. Nginx 配置 =====
log_info "===== 配置 Nginx ====="
log_warn "请登录宝塔面板 → 网站 → yunpingtai.cc → 配置文件"
log_warn "将 nginx.conf 的内容复制到 Nginx 配置文件中"
log_warn "或执行：sudo cp nginx.conf /usr/local/nginx/conf/vhost/yunpingtai.cc.conf"

# ===== 7. 部署总结 =====
echo ""
log_info "===== 部署完成 ====="
echo ""
echo "后端："
echo "  - Python 版本: $($PYTHON_CMD --version)"
echo "  - Django 设置: seadrone/settings_prod.py"
echo "  - Gunicorn 服务: seaboat-gunicorn.service"
echo "  - 静态文件: ${PROJECT_ROOT}/static/"
echo ""
echo "前端："
echo "  - Node.js 版本: $(node --version)"
echo "  - 构建输出: art-design-pro/dist/"
echo "  - 配置文件: art-design-pro/.env.production"
echo ""
echo "下一步："
echo "  1. 更新 SECRET_KEY（见上面的输出）"
echo "  2. 复制 Gunicorn systemd 服务文件"
echo "  3. 在宝塔面板配置 Nginx"
echo "  4. 启动 Gunicorn 服务: sudo systemctl start seaboat-gunicorn"
echo "  5. 重载 Nginx: sudo systemctl reload nginx"
echo "  6. 访问 https://yunpingtai.cc 进行测试"
echo ""
echo "日志查看："
echo "  tail -f logs/django.log"
echo "  tail -f logs/gunicorn_access.log"
echo "  sudo journalctl -u seaboat-gunicorn -f"
echo ""

log_info "部署脚本执行完成！"
