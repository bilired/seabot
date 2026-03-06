"""
Django 生产环境配置文件
用法：export DJANGO_SETTINGS_MODULE=seadrone.settings_prod
"""

import os
from pathlib import Path
from datetime import timedelta

# ===== 继承基础配置 =====
from .settings import *

# ===== 项目根路径 =====
BASE_DIR = Path(__file__).resolve().parent.parent

# ===== 1. 安全设置 =====
DEBUG = False
ALLOWED_HOSTS = [
    'yunpingtai.cc',
    'www.yunpingtai.cc',
    '127.0.0.1',
    'localhost',
]

# 从环境变量读取密钥（必须设置）
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set!")

# HTTPS 安全配置
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net"),
    "style-src": ("'self'", "'unsafe-inline'", "fonts.googleapis.com"),
}

# CSRF 信任源
CSRF_TRUSTED_ORIGINS = [
    "https://yunpingtai.cc",
    "https://www.yunpingtai.cc",
]

# ===== 2. 数据库配置 =====
# 使用 MySQL 8.0（通过宝塔面板创建）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'seaboat_prod',
        'USER': 'seaboat_user',
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,  # 连接池超时 10 分钟
    }
}

# 可选：如果使用 PostgreSQL（高性能推荐）
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'seaboat_prod',
#         'USER': 'seaboat_user',
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': 'localhost',
#         'PORT': '5432',
#         'CONN_MAX_AGE': 600,
#     }
# }

# ===== 3. 静态文件和媒体文件配置 =====
STATIC_URL = '/static/'
STATIC_ROOT = '/home/wwwroot/yunpingtai.cc/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/wwwroot/yunpingtai.cc/media/'

# ===== 4. 日志配置 =====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'django_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/home/wwwroot/yunpingtai.cc/logs/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'gunicorn_access_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/home/wwwroot/yunpingtai.cc/logs/gunicorn_access.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'gunicorn_error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/home/wwwroot/yunpingtai.cc/logs/gunicorn_error.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['django_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'gunicorn.access': {
            'handlers': ['gunicorn_access_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'gunicorn.error': {
            'handlers': ['gunicorn_error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ===== 5. CORS 配置（生产环境） =====
CORS_ALLOWED_ORIGINS = [
    "https://yunpingtai.cc",
    "https://www.yunpingtai.cc",
    "http://localhost:5173",  # 本地开发调试用
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# ===== 6. JWT 配置 =====
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=24),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ===== 7. REST Framework 配置 =====
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# ===== 8. 国际化和时区 =====
LANGUAGE_CODE = 'zh-hans'  # 简体中文
TIME_ZONE = 'Asia/Shanghai'  # 中国时区
USE_I18N = True
USE_TZ = True

# ===== 9. 会话和 Cookie =====
SESSION_COOKIE_AGE = 1209600  # 2 周
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ===== 10. 文件上传限制 =====
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500 MB
FILE_UPLOAD_PERMISSIONS = 0o644

# ===== 11. 邮件配置（可选） =====
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yunpingtai.cc')
