#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT="/Users/hanksgao/Desktop/seabot"
VENV_PATH="$PROJECT_ROOT/.venv"
BACKEND_PATH="$PROJECT_ROOT/back-end/seadrone"
FRONTEND_PATH="$PROJECT_ROOT/art-design-pro"

# 激活虚拟环境
activate_venv() {
    source "$VENV_PATH/bin/activate"
}

# 显示菜单
show_menu() {
    clear
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}${YELLOW}      🚀 无人船监测系统 - 启动管理${NC}${CYAN}${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}请选择要执行的操作：${NC}"
    echo ""
    echo -e "${YELLOW}1)${NC} 启动后端服务（Django）"
    echo -e "${YELLOW}2)${NC} 启动前端服务（Vue 3）"
    echo -e "${YELLOW}3)${NC} 同时启动前后端（需要两个终端）"
    echo -e "${YELLOW}4)${NC} 创建示例数据"
    echo -e "${YELLOW}5)${NC} 查看数据库内容"
    echo -e "${YELLOW}6)${NC} 运行测试"
    echo -e "${YELLOW}0)${NC} 退出"
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
}

# 启动后端
start_backend() {
    echo -e "${GREEN}▶ 启动 Django 后端服务...${NC}"
    echo ""
    
    cd "$BACKEND_PATH"
    activate_venv

    python3 manage.py runserver
}

# 启动前端
start_frontend() {
    echo -e "${GREEN}▶ 启动 Vue 3 前端服务...${NC}"
    echo -e "${YELLOW}说明：前端将运行在 http://localhost:5173${NC}"
    echo ""
    
    cd "$FRONTEND_PATH"
    
    # 检查 node_modules 是否存在
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}正在安装前端依赖...${NC}"
        pnpm install
    fi
    
    # 检查端口是否被占用
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}❌ 错误: 5173 端口已被占用${NC}"
        echo -e "${YELLOW}请先停止占用该端口的进程，然后重试${NC}"
        return 1
    fi
    
    pnpm dev
}

# 创建示例数据
create_sample_data() {
    echo -e "${GREEN}▶ 创建示例数据...${NC}"
    echo ""
    
    cd "$BACKEND_PATH"
    activate_venv
    
    echo -e "${YELLOW}选择要创建的数据类型：${NC}"
    echo "1) 水质和营养盐监测数据"
    echo "2) 无人船设备数据"
    echo "3) 仪表板统计数据"
    echo "4) 全部创建"
    echo ""
    read -p "请选择 (1-4): " data_choice
    
    case $data_choice in
        1)
            echo -e "${GREEN}创建水质和营养盐数据...${NC}"
            PYTHONPATH="$BACKEND_PATH" python3 ../create_monitoring_data.py
            ;;
        2)
            echo -e "${GREEN}创建无人船设备数据...${NC}"
            PYTHONPATH="$BACKEND_PATH" python3 ../create_sample_devices.py
            ;;
        3)
            echo -e "${GREEN}创建仪表板统计数据...${NC}"
            PYTHONPATH="$BACKEND_PATH" python3 ../create_dashboard_data.py
            ;;
        4)
            echo -e "${GREEN}创建所有示例数据...${NC}"
            PYTHONPATH="$BACKEND_PATH" python3 ../create_monitoring_data.py
            PYTHONPATH="$BACKEND_PATH" python3 ../create_sample_devices.py
            PYTHONPATH="$BACKEND_PATH" python3 ../create_dashboard_data.py
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac
}

# 查看数据库内容
check_database() {
    echo -e "${GREEN}▶ 显示数据库内容...${NC}"
    echo ""
    
    cd "$BACKEND_PATH/seadrone"
    activate_venv
    
    PYTHONPATH="$BACKEND_PATH/seadrone" python3 ../check_database.py
    
    echo ""
    read -p "按 Enter 键返回菜单..."
}

# 运行测试
run_tests() {
    echo -e "${GREEN}▶ 运行测试...${NC}"
    echo ""
    
    cd "$BACKEND_PATH"
    activate_venv
    
    echo -e "${YELLOW}选择要运行的测试：${NC}"
    echo "1) 用户注册测试"
    echo "2) 数据上传测试"
    echo ""
    read -p "请选择 (1-2): " test_choice
    
    case $test_choice in
        1)
            echo -e "${GREEN}运行用户注册测试...${NC}"
            bash test_register.sh
            ;;
        2)
            echo -e "${GREEN}运行数据上传测试...${NC}"
            python3 test_upload.py
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac
}

# 主循环
main() {
    while true; do
        show_menu
        read -p "请输入选项 (0-6): " choice
        
        case $choice in
            1)
                start_backend
                ;;
            2)
                start_frontend
                ;;
            3)
                echo -e "${YELLOW}请在另一个终端窗口中运行此脚本，然后选择选项 1 或 2${NC}"
                echo -e "${GREEN}终端 1: 运行后端服务${NC}"
                echo -e "${GREEN}终端 2: 运行前端服务${NC}"
                read -p "按 Enter 键继续..."
                ;;
            4)
                create_sample_data
                echo ""
                read -p "按 Enter 键返回菜单..."
                ;;
            5)
                check_database
                ;;
            6)
                run_tests
                echo ""
                read -p "按 Enter 键返回菜单..."
                ;;
            0)
                echo -e "${YELLOW}👋 再见！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 无效选择，请重试${NC}"
                sleep 2
                ;;
        esac
    done
}

# 启动主程序
main
