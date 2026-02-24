<template>
  <div class="docs-container">
    <div class="docs-header">
      <h1>📚 项目文档中心</h1>
      <p class="subtitle">无人船监测系统 - 快速参考指南</p>
    </div>

    <div class="docs-content">
      <!-- 快速导航 -->
      <div class="quick-nav">
        <div class="nav-item" @click="activeTab = 'quick-start'">
          <div class="icon">🚀</div>
          <h3>快速开始</h3>
        </div>
        <div class="nav-item" @click="activeTab = 'api-docs'">
          <div class="icon">📡</div>
          <h3>API 文档</h3>
        </div>
        <div class="nav-item" @click="activeTab = 'python-guide'">
          <div class="icon">🐍</div>
          <h3>Python 说明</h3>
        </div>
        <div class="nav-item" @click="activeTab = 'troubleshooting'">
          <div class="icon">🔧</div>
          <h3>常见问题</h3>
        </div>
      </div>

      <!-- 快速开始 -->
      <div v-if="activeTab === 'quick-start'" class="tab-content">
        <h2>🚀 快速开始</h2>
        
        <div class="section">
          <h3>1. 启动后端服务</h3>
          <div class="code-block">
            <pre>cd seabot/back-end/seadrone
source ../../.venv/bin/activate
python3 manage.py runserver 0.0.0.0:8000</pre>
            <button class="copy-btn" @click="copyCode('code1')">📋 复制</button>
          </div>
          <p class="info">✅ 服务启动后访问: http://localhost:8000</p>
        </div>

        <div class="section">
          <h3>2. 启动前端服务</h3>
          <div class="code-block">
            <pre>cd seabot/art-design-pro
pnpm dev</pre>
            <button class="copy-btn" @click="copyCode('code2')">📋 复制</button>
          </div>
          <p class="info">✅ 前端访问: http://localhost:5173</p>
        </div>

        <div class="section">
          <h3>3. 创建示例数据</h3>
          <div class="code-block">
            <pre>cd seabot/back-end/seadrone
source ../../.venv/bin/activate
python3 create_monitoring_data.py
python3 create_dashboard_data.py
python3 create_sample_devices.py</pre>
            <button class="copy-btn" @click="copyCode('code3')">📋 复制</button>
          </div>
        </div>

        <div class="section">
          <h3>🖥️ 重要地址</h3>
          <ul class="link-list">
            <li>
              <a href="http://localhost:5173" target="_blank">🎨 前端应用</a>
              <span class="port">:5173</span>
            </li>
            <li>
              <a href="http://localhost:8000/api/" target="_blank">📡 后端 API</a>
              <span class="port">:8000</span>
            </li>
            <li>
              <a href="http://localhost:8000/admin/" target="_blank">⚙️ 后台管理</a>
              <span class="port">:8000/admin</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- API 文档 -->
      <div v-if="activeTab === 'api-docs'" class="tab-content">
        <h2>📡 API 接口文档</h2>

        <div class="section">
          <h3>🔐 用户认证</h3>
          
          <div class="endpoint">
            <div class="method post">POST</div>
            <div class="path">/api/register/</div>
          </div>
          <p>用户注册</p>
          <div class="code-block">
            <pre>{
  "username": "user123",
  "password": "password123",
  "email": "user@example.com"
}</pre>
          </div>

          <div class="endpoint">
            <div class="method post">POST</div>
            <div class="path">/api/login/</div>
          </div>
          <p>用户登录，返回 JWT Token</p>

          <div class="endpoint">
            <div class="method get">GET</div>
            <div class="path">/api/user/info/</div>
          </div>
          <p>获取用户信息 (需要认证)</p>
        </div>

        <div class="section">
          <h3>📊 仪表板数据</h3>
          
          <div class="endpoint">
            <div class="method get">GET</div>
            <div class="path">/api/dashboard/stats/</div>
          </div>
          <p>获取仪表板统计数据 (需要认证)</p>

          <div class="endpoint">
            <div class="method get">GET</div>
            <div class="path">/api/dashboard/sales/</div>
          </div>
          <p>获取销售数据 (需要认证)</p>

          <div class="endpoint">
            <div class="method get">GET</div>
            <div class="path">/api/dashboard/growth/</div>
          </div>
          <p>获取用户增长数据 (需要认证)</p>
        </div>

        <div class="section">
          <h3>📈 监测数据</h3>
          
          <div class="endpoint">
            <div class="method get">GET</div>
            <div class="path">/api/analysis/water-quality/</div>
          </div>
          <p>获取水质监测数据 (无需认证)</p>

          <div class="endpoint">
            <div class="method get">GET</div>
            <div class="path">/api/analysis/nutrient/</div>
          </div>
          <p>获取营养盐数据 (无需认证)</p>

          <div class="endpoint">
            <div class="method post">POST</div>
            <div class="path">/api/upload/water-quality/</div>
          </div>
          <p>上传水质数据 (无需认证)</p>

          <div class="endpoint">
            <div class="method post">POST</div>
            <div class="path">/api/upload/nutrient/</div>
          </div>
          <p>上传营养盐数据 (无需认证)</p>
        </div>

        <div class="section">
          <h3>🚤 设备管理</h3>
          
          <div class="endpoint">
            <div class="method get">GET</div>
            <div class="path">/api/drone/list/</div>
          </div>
          <p>获取设备列表 (需要认证)</p>

          <div class="endpoint">
            <div class="method post">POST</div>
            <div class="path">/api/drone/create/</div>
          </div>
          <p>创建设备 (需要认证)</p>

          <div class="endpoint">
            <div class="method post">POST</div>
            <div class="path">/api/drone/delete/</div>
          </div>
          <p>删除设备 (需要认证)</p>

          <div class="endpoint">
            <div class="method post">POST</div>
            <div class="path">/api/drone/batch-delete/</div>
          </div>
          <p>批量删除设备 (需要认证)</p>
        </div>
      </div>

      <!-- Python 说明 -->
      <div v-if="activeTab === 'python-guide'" class="tab-content">
        <h2>🐍 Python 后端说明</h2>

        <div class="section">
          <h3>📁 项目结构</h3>
          <div class="code-block">
            <pre>back-end/seadrone/
├── accounts/        # 用户认证应用
│   ├── models.py   # 数据模型
│   ├── views.py    # API 视图
│   └── urls.py     # 路由配置
├── monitoring/      # 监测数据应用
│   ├── models.py   # WaterQualityData, NutrientData
│   ├── views.py    # 数据接口
│   └── urls.py     # 路由配置
├── manage.py       # Django 管理脚本
└── db.sqlite3      # SQLite 数据库</pre>
          </div>
        </div>

        <div class="section">
          <h3>📚 主要应用</h3>
          
          <div class="app-card">
            <h4>accounts 应用</h4>
            <p><strong>用途：</strong> 用户认证和仪表板数据</p>
            <p><strong>模型：</strong></p>
            <ul>
              <li>DashboardStats - 仪表板统计</li>
              <li>UserActivity - 用户活动日志</li>
              <li>DroneDevice - 设备管理</li>
              <li>MonthlySalesData - 销售数据</li>
              <li>UserGrowthData - 增长数据</li>
            </ul>
          </div>

          <div class="app-card">
            <h4>monitoring 应用</h4>
            <p><strong>用途：</strong> 传感器数据管理</p>
            <p><strong>模型：</strong></p>
            <ul>
              <li>WaterQualityData - 水质监测</li>
              <li>NutrientData - 营养盐数据</li>
            </ul>
          </div>
        </div>

        <div class="section">
          <h3>🔧 常用命令</h3>
          <div class="code-block">
            <pre># 创建迁移文件
python3 manage.py makemigrations

# 应用迁移
python3 manage.py migrate

# 创建超级用户
python3 manage.py createsuperuser

# 进入 Django Shell
python3 manage.py shell

# 清空数据库
python3 manage.py flush</pre>
          </div>
        </div>
      </div>

      <!-- 常见问题 -->
      <div v-if="activeTab === 'troubleshooting'" class="tab-content">
        <h2>🔧 常见问题排查</h2>

        <div class="faq-item">
          <h3>❌ 端口 8000 已被占用</h3>
          <div class="solution">
            <p><strong>解决方案：</strong></p>
            <div class="code-block">
              <pre>lsof -i :8000
kill -9 &lt;PID&gt;

# 或使用不同端口
python3 manage.py runserver 8001</pre>
            </div>
          </div>
        </div>

        <div class="faq-item">
          <h3>❌ 数据库错误</h3>
          <div class="solution">
            <p><strong>解决方案：</strong></p>
            <div class="code-block">
              <pre>rm db.sqlite3
python3 manage.py migrate
python3 create_monitoring_data.py</pre>
            </div>
          </div>
        </div>

        <div class="faq-item">
          <h3>❌ 401 未授权错误</h3>
          <div class="solution">
            <p><strong>原因：</strong> 请求没有发送有效的 JWT Token</p>
            <p><strong>解决方案：</strong></p>
            <ul>
              <li>登录后获取 Token</li>
              <li>在请求头中添加: Authorization: Bearer {token}</li>
              <li>监测数据接口不需要认证</li>
            </ul>
          </div>
        </div>

        <div class="faq-item">
          <h3>❌ CORS 错误</h3>
          <div class="solution">
            <p><strong>解决方案：</strong> 检查 settings.py 中的 CORS_ALLOWED_ORIGINS</p>
            <div class="code-block">
              <pre>CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]</pre>
            </div>
          </div>
        </div>

        <div class="faq-item">
          <h3>✅ 一切正常但页面无数据</h3>
          <div class="solution">
            <p><strong>解决方案：</strong></p>
            <ul>
              <li>确保后端服务正在运行 (port 8000)</li>
              <li>创建示例数据</li>
              <li>检查浏览器控制台是否有错误</li>
              <li>清除浏览器缓存和 localStorage</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="docs-footer">
      <p>💡 更多详细信息请查看项目根目录的 <code>项目使用说明.md</code> 和 <code>back-end/Python代码说明.md</code></p>
      <p>📧 如有问题，请联系开发团队</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('quick-start')

const copyCode = (codeId: string) => {
  const codeText = document.querySelector(`#${codeId}`)?.textContent || ''
  navigator.clipboard.writeText(codeText).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}
</script>

<style scoped lang="scss">
.docs-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.docs-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;

  h1 {
    font-size: 32px;
    margin: 0 0 10px 0;
    color: #1f2937;
  }

  .subtitle {
    font-size: 16px;
    color: #6b7280;
    margin: 0;
  }
}

.quick-nav {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;

  .nav-item {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
    }

    .icon {
      font-size: 32px;
      margin-bottom: 10px;
    }

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }
  }
}

.docs-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-content {
  h2 {
    color: #1f2937;
    border-bottom: 3px solid #667eea;
    padding-bottom: 10px;
    margin-bottom: 30px;
  }

  .section {
    margin-bottom: 30px;

    h3 {
      color: #374151;
      font-size: 18px;
      margin-bottom: 15px;
      display: flex;
      align-items: center;

      &::before {
        content: '';
        width: 4px;
        height: 20px;
        background: #667eea;
        border-radius: 2px;
        margin-right: 10px;
      }
    }

    .info {
      background: #f0f9ff;
      border-left: 4px solid #0284c7;
      padding: 10px 15px;
      border-radius: 4px;
      color: #0c4a6e;
      margin-top: 10px;
    }
  }

  .code-block {
    background: #1f2937;
    color: #f3f4f6;
    padding: 15px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 15px 0;
    position: relative;

    pre {
      margin: 0;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.6;
    }

    .copy-btn {
      position: absolute;
      top: 10px;
      right: 10px;
      background: #667eea;
      color: white;
      border: none;
      padding: 6px 12px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      transition: background 0.3s;

      &:hover {
        background: #764ba2;
      }
    }
  }

  .endpoint {
    display: flex;
    align-items: center;
    gap: 15px;
    margin: 20px 0 5px 0;

    .method {
      padding: 6px 12px;
      border-radius: 4px;
      color: white;
      font-weight: bold;
      font-size: 12px;
      min-width: 50px;
      text-align: center;

      &.get {
        background: #3b82f6;
      }

      &.post {
        background: #10b981;
      }

      &.put {
        background: #f59e0b;
      }

      &.delete {
        background: #ef4444;
      }
    }

    .path {
      font-family: 'Courier New', monospace;
      background: #f3f4f6;
      padding: 6px 12px;
      border-radius: 4px;
      color: #1f2937;
      font-weight: 500;
    }
  }

  .app-card {
    background: #f9fafb;
    border-left: 4px solid #667eea;
    padding: 15px;
    border-radius: 6px;
    margin-bottom: 15px;

    h4 {
      margin: 0 0 10px 0;
      color: #1f2937;
    }

    p {
      margin: 5px 0;
      color: #6b7280;

      strong {
        color: #374151;
      }
    }

    ul {
      margin: 10px 0 0 0;
      padding-left: 20px;

      li {
        color: #6b7280;
        margin: 5px 0;
      }
    }
  }

  .faq-item {
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px solid #e5e7eb;

    &:last-child {
      border-bottom: none;
    }

    h3 {
      margin-bottom: 15px;
      color: #1f2937;
    }

    .solution {
      background: #f9fafb;
      padding: 15px;
      border-radius: 6px;
      border-left: 4px solid #667eea;

      p {
        color: #6b7280;
        margin: 10px 0;

        strong {
          color: #374151;
        }
      }

      ul {
        margin: 10px 0;
        padding-left: 20px;

        li {
          color: #6b7280;
          margin: 5px 0;
        }
      }
    }
  }

  .link-list {
    list-style: none;
    padding: 0;

    li {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 15px;
      background: #f3f4f6;
      border-radius: 6px;
      margin-bottom: 10px;

      a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;

        &:hover {
          text-decoration: underline;
        }
      }

      .port {
        background: #667eea;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-family: 'Courier New', monospace;
      }
    }
  }
}

.docs-footer {
  text-align: center;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
  color: #6b7280;

  p {
    margin: 10px 0;

    code {
      background: #f3f4f6;
      padding: 2px 6px;
      border-radius: 3px;
      color: #374151;
    }
  }
}
</style>
