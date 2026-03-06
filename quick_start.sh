#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/back-end/seadrone"
FRONTEND_DIR="$PROJECT_ROOT/art-design-pro"
VENV_PATH="$PROJECT_ROOT/.venv"
RUN_DIR="$PROJECT_ROOT/.run"
LOG_DIR="$PROJECT_ROOT/logs"

BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"
BACKEND_LOG_FILE="$LOG_DIR/backend.log"
FRONTEND_LOG_FILE="$LOG_DIR/frontend.log"

usage() {
  cat <<EOF
用法: bash quick_start.sh [命令]

命令:
  start    启动前后端（默认）
  stop     停止前后端
  restart  重启前后端
  status   查看状态
  logs     查看日志（tail -f）
  help     查看帮助
EOF
}

ensure_dirs() {
  mkdir -p "$RUN_DIR" "$LOG_DIR"
}

is_running() {
  local pid_file="$1"

  [[ -f "$pid_file" ]] || return 1

  local pid
  pid="$(cat "$pid_file")"
  [[ -n "$pid" ]] || return 1

  if kill -0 "$pid" >/dev/null 2>&1; then
    return 0
  fi

  rm -f "$pid_file"
  return 1
}

activate_venv_if_exists() {
  if [[ -f "$VENV_PATH/bin/activate" ]]; then
    source "$VENV_PATH/bin/activate"
  else
    echo "⚠️ 未找到 .venv，将使用系统 python3 启动后端"
  fi
}

start_backend() {
  if is_running "$BACKEND_PID_FILE"; then
    echo "✅ 后端已运行 (PID: $(cat "$BACKEND_PID_FILE"))"
    return
  fi

  if [[ ! -f "$BACKEND_DIR/manage.py" ]]; then
    echo "❌ 未找到后端入口: $BACKEND_DIR/manage.py"
    exit 1
  fi

  echo "🚀 启动后端: http://127.0.0.1:8000"
  (
    cd "$BACKEND_DIR"
    activate_venv_if_exists
    nohup python3 manage.py runserver 0.0.0.0:8000 >"$BACKEND_LOG_FILE" 2>&1 &
    echo $! >"$BACKEND_PID_FILE"
  )
}

start_frontend() {
  if is_running "$FRONTEND_PID_FILE"; then
    echo "✅ 前端已运行 (PID: $(cat "$FRONTEND_PID_FILE"))"
    return
  fi

  if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
    echo "❌ 未找到前端入口: $FRONTEND_DIR/package.json"
    exit 1
  fi

  echo "🚀 启动前端: http://127.0.0.1:5173"
  (
    cd "$FRONTEND_DIR"
    if command -v pnpm >/dev/null 2>&1; then
      nohup pnpm dev --host 0.0.0.0 --port 3006 >"$FRONTEND_LOG_FILE" 2>&1 &
    else
      echo "⚠️ 未检测到 pnpm，使用 npm 启动"
      nohup npm run dev -- --host 0.0.0.0 --port 3006 >"$FRONTEND_LOG_FILE" 2>&1 &
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
    echo "✅ 后端运行中 (PID: $(cat "$BACKEND_PID_FILE")) -> http://127.0.0.1:8000"
  else
    echo "❌ 后端未运行"
  fi

  if is_running "$FRONTEND_PID_FILE"; then
    echo "✅ 前端运行中 (PID: $(cat "$FRONTEND_PID_FILE")) -> http://127.0.0.1:3006"
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
  ensure_dirs
  start_backend
  start_frontend
  echo ""
  show_status
  echo ""
  echo "🎉 启动完成"
}

main() {
  local cmd="${1:-start}"

  case "$cmd" in
    start)
      start_all
      ;;
    stop)
      ensure_dirs
      stop_service "前端" "$FRONTEND_PID_FILE"
      stop_service "后端" "$BACKEND_PID_FILE"
      ;;
    restart)
      ensure_dirs
      stop_service "前端" "$FRONTEND_PID_FILE"
      stop_service "后端" "$BACKEND_PID_FILE"
      start_all
      ;;
    status)
      ensure_dirs
      show_status
      ;;
    logs)
      ensure_dirs
      show_logs
      ;;
    help|-h|--help)
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
