#!/bin/bash
# 测试注册功能的脚本

echo "=========================================="
echo "🧪 测试用户注册功能"
echo "=========================================="

API_URL="http://localhost:8000"

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "❌ 未找到可用的 Python 解释器（python3 或 python）"
  exit 1
fi

RUN_ID=$(date +%s)
NEW_USER="newuser_${RUN_ID}"
NEW_EMAIL="${NEW_USER}@example.com"
TEST_USER="testaccount_${RUN_ID}"
TEST_EMAIL="${TEST_USER}@example.com"

# 测试 1: 成功注册
echo ""
echo "测试 1: 注册新用户"
echo "----------------------------------------"
curl -X POST "${API_URL}/api/register/" \
  -H "Content-Type: application/json" \
  -d "{\"userName\": \"${NEW_USER}\", \"password\": \"password123\", \"confirmPassword\": \"password123\", \"email\": \"${NEW_EMAIL}\"}" | "$PYTHON_BIN" -m json.tool

# 测试 2: 尝试用相同用户名注册（应该失败）
echo ""
echo ""
echo "测试 2: 尝试注册相同的用户名（应该失败）"
echo "----------------------------------------"
curl -X POST "${API_URL}/api/register/" \
  -H "Content-Type: application/json" \
  -d "{\"userName\": \"${NEW_USER}\", \"password\": \"password456\", \"confirmPassword\": \"password456\", \"email\": \"different_${RUN_ID}@example.com\"}" | "$PYTHON_BIN" -m json.tool

# 测试 3: 密码不一致（应该失败）
echo ""
echo ""
echo "测试 3: 密码不一致（应该失败）"
echo "----------------------------------------"
curl -X POST "${API_URL}/api/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "anotheruser",
    "password": "password123",
    "confirmPassword": "different123",
    "email": "another@example.com"
  }' | "$PYTHON_BIN" -m json.tool

# 测试 4: 用短密码（应该失败）
echo ""
echo ""
echo "测试 4: 用短密码（应该失败）"
echo "----------------------------------------"
curl -X POST "${API_URL}/api/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "shortpwd",
    "password": "123",
    "confirmPassword": "123",
    "email": "short@example.com"
  }' | "$PYTHON_BIN" -m json.tool

# 测试 5: 成功注册另一个用户并立即登录
echo ""
echo ""
echo "测试 5: 注册新用户并立即登录"
echo "----------------------------------------"

# 先注册
echo "📝 注册用户: ${TEST_USER}"
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/api/register/" \
  -H "Content-Type: application/json" \
  -d "{\"userName\": \"${TEST_USER}\", \"password\": \"testpass123\", \"confirmPassword\": \"testpass123\", \"email\": \"${TEST_EMAIL}\"}")

echo "$REGISTER_RESPONSE" | "$PYTHON_BIN" -m json.tool

# 然后尝试登录
echo ""
echo "🔐 使用新注册的账号登录"
curl -X POST "${API_URL}/api/login/" \
  -H "Content-Type: application/json" \
  -d "{\"userName\": \"${TEST_USER}\", \"password\": \"testpass123\"}" | "$PYTHON_BIN" -m json.tool

echo ""
echo ""
echo "=========================================="
echo "✅ 测试完成"
echo "=========================================="
