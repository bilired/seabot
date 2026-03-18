#!/bin/bash

# 无人船监测系统 - 快速启动脚本

echo "🌊 无人船监测系统 - 启动脚本"
echo "======================================"

PROJECT_ROOT="/Users/hanksgao/Desktop/seabot"
VENV_PATH="$PROJECT_ROOT/.venv"

# 激活虚拟环境
activate_venv() {
    source "$VENV_PATH/bin/activate"
}

while true; do
    echo ""
    echo "请选择要启动的服务："
    echo "1) 启动后端服务（Django）"
    echo "2) 启动前端服务（Vue 3）"
    echo "3) 同时启动前后端（需要两个终端）"
    echo "4) 创建示例数据"
    echo "5) 查看数据库内容"
    echo "6) 运行测试"
    echo "0) 退出"
    echo ""
    read -p "请输入选项 (0-6): " choice

    case $choice in
        1)
            echo ""
            echo "🚀 启动后端服务（Django）..."
            echo ""
            cd "$PROJECT_ROOT/back-end/seadrone"
            activate_venv
            python3 manage.py runserver
            ;;
        2)
            echo ""
            echo "🎨 启动前端服务（Vue 3）..."
            echo "访问地址: http://localhost:5173"
            echo ""
            cd "$PROJECT_ROOT/art-design-pro"
            pnpm dev
            ;;
        3)
            echo ""
            echo "⚠️  同时启动前后端需要两个终端"
            echo ""
            echo "请在一个终端运行："
            echo "  cd $PROJECT_ROOT/back-end/seadrone"
            echo "  source ../../.venv/bin/activate"
            echo "  python3 manage.py runserver"
            echo ""
            echo "在另一个终端运行："
            echo "  cd $PROJECT_ROOT/art-design-pro"
            echo "  pnpm dev"
            echo ""
            read -p "按 Enter 启动后端服务（后台）..."
            cd "$PROJECT_ROOT/back-end/seadrone"
            activate_venv
            python3 manage.py runserver &
            echo ""
            echo "✅ 后端已启动，请在另一个终端运行前端服务"
            read -p "按 Enter 返回菜单..."
            ;;
        4)
            echo ""
            echo "📊 创建示例数据..."
            cd "$PROJECT_ROOT/back-end/seadrone"
            activate_venv

            echo "1) 创建仪表板数据..."
            python3 ../create_dashboard_data.py

            echo ""
            echo "2) 创建示例设备..."
            python3 ../create_sample_devices.py

            echo ""
            echo "3) 创建监测数据..."
            python3 create_monitoring_data.py

            echo ""
            echo "✅ 示例数据创建完成！"
            read -p "按 Enter 返回菜单..."
            ;;
        5)
            echo ""
            echo "📋 数据库内容："
            cd "$PROJECT_ROOT/back-end"
            activate_venv
            PYTHONPATH="$PWD/seadrone" python3 check_users.py
            read -p "按 Enter 返回菜单..."
            ;;
        6)
            echo ""
            echo "🧪 运行测试..."
            cd "$PROJECT_ROOT/back-end"

            echo "1) 测试注册功能..."
            bash test_register.sh

            echo ""
            echo "2) 测试数据上传..."
            activate_venv
            python3 test_upload.py

            echo ""
            echo "✅ 测试完成！"
            read -p "按 Enter 返回菜单..."
            ;;
        0)
            echo "👋 已退出"
            exit 0
            ;;
        *)
            echo "❌ 无效的选项"
            ;;
    esac
done
