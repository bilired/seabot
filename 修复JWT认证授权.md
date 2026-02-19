# 修复：JWT 认证授权问题

## 🐛 问题诊断

获取用户信息时返回 **401 Unauthorized** 错误，说明 JWT token 没有被正确识别。

## ✅ 修复内容

### 1. 前端 Authorization 请求头格式 ❌ → ✅
**文件**: `art-design-pro/src/utils/http/index.ts`

**错误格式**：
```typescript
// ❌ 错误 - 只发送了 token
request.headers.set('Authorization', accessToken)
// 实际发送：Authorization: eyJhbGc...
```

**正确格式**：
```typescript
// ✅ 正确 - 加上 Bearer 前缀
request.headers.set('Authorization', `Bearer ${accessToken}`)
// 实际发送：Authorization: Bearer eyJhbGc...
```

Django JWT 认证默认期望的格式是 `Bearer {token}`。

### 2. Django JWT 详细配置
**文件**: `back-end/seadrone/seadrone/settings.py`

添加了 JWT 的具体配置，包括 token 有效期：
```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),    # Access token 1小时过期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),    # Refresh token 7天过期
    'ALGORITHM': 'HS256',                            # 加密算法
    'SIGNING_KEY': SECRET_KEY,                       # 使用 Django 的 SECRET_KEY
}
```

## 🚀 需要做的事

### 第 1 步：重启 Django 服务器

停止现有服务：
```bash
# 按 CTRL+C 停止
```

重新启动：
```bash
cd /Users/hanksgao/Desktop/art-design-menu/back-end/seadrone
python manage.py runserver 0.0.0.0:8000
```

### 第 2 步：清除前端缓存并重新加载

```bash
# 前端浏览器中：
# Mac: Cmd + Shift + R
# Windows/Linux: Ctrl + Shift + R
```

或打开开发者工具清除缓存：
- F12 打开开发者工具
- 右键点击刷新按钮 → "清空缓存并硬刷新"

### 第 3 步：重新测试登录

1. 访问 `http://localhost:3006/login`
2. 输入用户名和密码
3. 拖动验证码
4. 点击登录

**期望的网络请求流程**：
```
1. POST /api/login/ 
   ✅ 200 OK - 返回 { token, refreshToken }

2. GET /api/user/info/
   ✅ 200 OK - 返回 { userId, userName, email, ... }

3. 动态路由注册
   ✅ 成功 - 跳转到首页
```

## 🔍 调试方法

### 查看实际发送的请求头

在浏览器开发者工具中：
1. F12 打开开发者工具
2. 切换到 **Network** 标签
3. 登录并观察请求
4. 点击 `GET /api/user/info/` 请求
5. 切换到 **Request Headers** 标签
6. 查找 `Authorization` 字段

**应该看到**：
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**如果看到**：
```
Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  // ❌ 没有 Bearer
```

说明前端代码没有生效，需要硬刷新浏览器。

### 在后端日志查看认证信息

Django 控制台会显示类似：
```
[23/Jan/2026 10:30:45] "GET /api/user/info/ HTTP/1.1" 401 ...  // ❌ 认证失败
[23/Jan/2026 10:30:50] "GET /api/user/info/ HTTP/1.1" 200 ...  # ✅ 认证成功
```

## 📋 常见问题

### 问题 1：仍然返回 401
**原因**：
- Django 服务器没有重启，新配置没有加载
- 浏览器缓存没有清除
- token 格式仍然有问题

**解决**：
1. 硬刷新浏览器 (Cmd+Shift+R)
2. 检查开发者工具中的 Authorization 请求头
3. 重启 Django 服务器

### 问题 2：登录成功但 token 没有保存
**原因**：
- 前端 store 中的 token 没有被正确保存

**调试**：
```javascript
// 在浏览器控制台执行：
localStorage.getItem('user')  // 查看存储的用户信息
```

### 问题 3：JWT token 过期
**症状**：
- 登录后一段时间再操作就返回 401

**解决**：
- 实现 refresh token 逻辑（用 refresh token 获取新的 access token）

## 🔐 JWT Token 说明

### Token 包含的信息

JWT 是分为三部分用 `.` 分隔：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNjczOTI0NjQ1fQ.
w5K_-XmC_QqXXXXXXXXXXXXXXXXXXXXXXXX
```

- **第 1 部分**：Header - 算法信息
- **第 2 部分**：Payload - 用户信息 (Base64 编码)
- **第 3 部分**：Signature - 签名

可以在 [jwt.io](https://jwt.io) 网站解码查看。

### Token 生命周期

```
登录成功
   ↓
返回 access_token (有效期：1小时) 和 refresh_token (有效期：7天)
   ↓
前端存储两个 token
   ↓
后续请求用 access_token
   ↓
access_token 过期
   ↓
用 refresh_token 获取新的 access_token
   ↓
继续使用新的 access_token
```

## 下一步优化

当前已实现：
- ✅ JWT 登录
- ✅ 用户信息获取
- ✅ Bearer token 发送

可以进一步实现：
- 🔄 Token 刷新逻辑 (使用 refresh token)
- 🔐 权限验证（roles 和 permissions）
- 📝 日志记录
- 🛡️ Token 黑名单（登出时）

祝测试顺利！🎉
