#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
BACKEND_DIR="$PROJECT_ROOT/back-end/seadrone"
FRONTEND_DIR="$PROJECT_ROOT/art-design-pro"
RUN_DIR="$PROJECT_ROOT/.run"
LOG_DIR="$PROJECT_ROOT/logs"

BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"
BACKEND_LOG_FILE="$LOG_DIR/backend.log"
FRONTEND_LOG_FILE="$LOG_DIR/frontend.log"

PYTHON_PACKAGES=(
  "Django==5.2.10"
  "djangorestframework==3.16.1"
  "djangorestframework-simplejwt==5.5.1"
  "django-cors-headers==4.9.0"
)

usage() {
  cat <<EOF
用法: bash local_deploy.sh [command]

commands:
  start    一键准备并启动前后端（默认）
  stop     停止前后端服务
  restart  重启前后端服务
  status   查看服务状态
  logs     查看日志（tail -f）
EOF
}

ensure_structure() {
  if [[ ! -f "$BACKEND_DIR/manage.py" ]]; then
    echo "❌ 未找到后端入口: $BACKEND_DIR/manage.py"
    exit 1
  fi

  if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
    echo "❌ 未找到前端入口: $FRONTEND_DIR/package.json"
    exit 1
  fi

  mkdir -p "$RUN_DIR" "$LOG_DIR"
}

ensure_venv() {
  if [[ ! -d "$VENV_PATH" ]]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv "$VENV_PATH"
  fi

  source "$VENV_PATH/bin/activate"
  pip install --upgrade pip >/dev/null

  echo "📦 安装后端依赖..."
  pip install "${PYTHON_PACKAGES[@]}" >/dev/null
}

prepare_backend() {
  source "$VENV_PATH/bin/activate"
  echo "🗄️ 执行数据库迁移..."
  (
    cd "$BACKEND_DIR"
    python3 manage.py migrate --noinput
  )
}

prepare_frontend() {
  echo "📦 安装前端依赖..."
  (
    cd "$FRONTEND_DIR"
    if command -v pnpm >/dev/null 2>&1; then
      pnpm install
    else
      npm install
    fi
  )
}

is_running() {
  local pid_file="$1"
  if [[ ! -f "$pid_file" ]]; then
    return 1
  fi

  local pid
  pid="$(cat "$pid_file")"
  if [[ -z "$pid" ]]; then
    return 1
  fi

  if kill -0 "$pid" >/dev/null 2>&1; then
    return 0
  fi

  rm -f "$pid_file"
  return 1
}

start_backend() {
  if is_running "$BACKEND_PID_FILE"; then
    echo "✅ 后端已在运行 (PID: $(cat "$BACKEND_PID_FILE"))"
    return
  fi

  source "$VENV_PATH/bin/activate"
  echo "🚀 启动后端: http://127.0.0.1:8000"
  (
    cd "$BACKEND_DIR"
    nohup python3 manage.py runserver 0.0.0.0:8000 >"$BACKEND_LOG_FILE" 2>&1 &
    echo $! >"$BACKEND_PID_FILE"
  )
}

start_frontend() {
  if is_running "$FRONTEND_PID_FILE"; then
    echo "✅ 前端已在运行 (PID: $(cat "$FRONTEND_PID_FILE"))"
    return
  fi

  echo "🚀 启动前端: http://127.0.0.1:5173"
  (
    cd "$FRONTEND_DIR"
    if command -v pnpm >/dev/null 2>&1; then
      nohup pnpm dev --host 0.0.0.0 --port 5173 >"$FRONTEND_LOG_FILE" 2>&1 &
    else
      nohup npm run dev -- --host 0.0.0.0 --port 5173 >"$FRONTEND_LOG_FILE" 2>&1 &
    fi
    echo $! >"$FRONTEND_PID_FILE"
  )
}

stop_service() {
  local name="$1"
  local pid_file="$2"

  if ! is_running "$pid_file"; then
    echo "ℹ️ $name 未运行"
    return
  fi

  local pid
  pid="$(cat "$pid_file")"
  kill "$pid" >/dev/null 2>&1 || true
  rm -f "$pid_file"
  echo "🛑 已停止 $name (PID: $pid)"
}

show_status() {
  if is_running "$BACKEND_PID_FILE"; then
    echo "✅ 后端运行中 (PID: $(cat "$BACKEND_PID_FILE")) - http://127.0.0.1:8000"
  else
    echo "❌ 后端未运行"
  fi

  if is_running "$FRONTEND_PID_FILE"; then
    echo "✅ 前端运行中 (PID: $(cat "$FRONTEND_PID_FILE")) - http://127.0.0.1:5173"
  else
    echo "❌ 前端未运行"
  fi

  echo "📄 后端日志: $BACKEND_LOG_FILE"
  echo "📄 前端日志: $FRONTEND_LOG_FILE"
}

show_logs() {
  touch "$BACKEND_LOG_FILE" "$FRONTEND_LOG_FILE"
  tail -f "$BACKEND_LOG_FILE" "$FRONTEND_LOG_FILE"
}

start_all() {
  ensure_structure
  ensure_venv
  prepare_backend
  prepare_frontend
  start_backend
  start_frontend
  echo ""
  show_status
  echo ""
  echo "🎉 本地部署完成"
}

main() {
  local cmd="${1:-start}"

  case "$cmd" in
    start)
      start_all
      ;;
    stop)
      ensure_structure
      stop_service "前端" "$FRONTEND_PID_FILE"
      stop_service "后端" "$BACKEND_PID_FILE"
      ;;
    restart)
      ensure_structure
      stop_service "前端" "$FRONTEND_PID_FILE"
      stop_service "后端" "$BACKEND_PID_FILE"
      start_all
      ;;
    status)
      ensure_structure
      show_status
      ;;
    logs)
      ensure_structure
      show_logs
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      echo "❌ 未知命令: $cmd"
      usage
      exit 1
      ;;
  esac
}

main "$@"
