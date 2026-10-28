# MediaCrawler Backend - Django API

这是 MediaCrawler 项目的 Django 后端实现。

## 项目结构

```
backend/
├── mediacrawler_config/    # Django 项目配置
│   ├── settings.py          # 项目设置（从 backend/.env 加载配置）
│   ├── urls.py              # URL 路由
│   ├── wsgi.py             # WSGI 配置
│   └── utils/              # 工具模块
│       └── config.py       # 配置访问工具
├── api/                     # API 应用
│   ├── views.py             # API 视图
│   └── serializers.py      # 数据序列化器
├── media_platform/          # 数据模型应用
│   ├── models.py            # Django 数据模型
│   └── admin.py            # Admin 配置
├── manage.py               # Django 管理脚本
├── requirements.txt        # Python 依赖
├── .env                    # 唯一环境变量文件（不提交到版本控制）
├── .gitignore             # Git 忽略文件
└── README.md              # 本文件
```

## 安装

### 1. 创建虚拟环境

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

`pip install` 不会安装 Playwright 所需的浏览器二进制。请在同一个已激活的虚拟环境中执行上述浏览器安装命令，为使用 Playwright 自带浏览器的爬虫模式准备 Chromium；否则首次启动浏览器时可能提示 `Executable doesn't exist`。更新 Playwright 后，请重新执行安装命令以匹配浏览器版本，详见 [Playwright 浏览器安装说明](https://playwright.dev/python/docs/browsers)。

### 3. 配置环境变量

创建 `.env` 并根据需要修改。项目运行时只读取 `backend/.env`：

```bash
touch .env
```

如需启用深度分析，请在 `backend/.env` 中配置：

```env
SILICONFLOW_API_KEY=your_siliconflow_api_key
AI_API_BASE_URL=https://api.siliconflow.cn/v1
AI_CHAT_MODEL=deepseek-ai/DeepSeek-V4-Pro
```

## 环境变量配置

### 核心配置

| 变量 | 说明 | 默认值 |
|--------|------|--------|
| `DJANGO_SECRET_KEY` | Django 密钥 | 固定的开发占位值 `django-insecure-dev-key-change-in-production` |
| `DJANGO_DEBUG` | 调试模式 | `True` |
| `DJANGO_ALLOWED_HOSTS` | 允许的主机 | `localhost,127.0.0.1` |

未设置 `DJANGO_SECRET_KEY` 时，后端使用代码中的固定开发占位值，不会自动生成随机密钥。生产部署前，请按[生成密钥](#生成密钥)中的命令生成独立密钥并写入 `backend/.env` 的 `DJANGO_SECRET_KEY`，避免使用默认值。

### 数据库配置

| 变量 | 说明 | 默认值 |
|--------|------|--------|
| `DB_ENGINE` | 数据库引擎 | `mysql` |
| `DB_NAME` | 数据库名 | `media_crawler`（MySQL 默认） |
| `DB_USER` | 数据库用户 | `root`（MySQL 默认）；PostgreSQL 默认为 `postgres` |
| `DB_PASSWORD` | 数据库密码 | 空 |
| `DB_HOST` | 数据库主机 | `localhost`（MySQL/PostgreSQL） |
| `DB_PORT` | 数据库端口 | `3306` / `5432`（按引擎） |

支持的数据引擎：
- `mysql` - MySQL
- `postgresql` - PostgreSQL
- `postgres` - PostgreSQL（`postgresql` 的兼容别名）

如果没有 `.env`，后端会默认按本地 MySQL 参数加载：`DB_ENGINE=mysql`、`DB_NAME=media_crawler`、`DB_USER=root`、`DB_HOST=localhost`、`DB_PORT=3306`。

首次运行前必须先启动所选数据库服务，并创建 `DB_NAME` 指定的数据库。`python manage.py migrate` 负责在已有数据库中创建和更新表，不会创建 MySQL / PostgreSQL 数据库本身。

例如，使用有建库权限的本地 MySQL 账户连接服务后执行：

```sql
CREATE DATABASE IF NOT EXISTS media_crawler
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

如使用 PostgreSQL，请用有建库权限的账户创建 `media_crawler`（例如 `createdb -U postgres media_crawler`），并填写下面对应的连接配置。运行 Django 的数据库账户需要有目标数据库的建表与读写权限。

示例：

```env
# MySQL
DB_ENGINE=mysql
DB_NAME=media_crawler
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

```env
# PostgreSQL
DB_ENGINE=postgresql
DB_NAME=media_crawler
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 服务器配置

| 变量 | 说明 | 默认值 |
|--------|------|--------|
| `HOST` | 服务器地址 | `0.0.0.0` |
| `PORT` | 服务器端口 | `8000` |

### CORS 配置

| 变量 | 说明 | 默认值 |
|--------|------|--------|
| `CORS_ALLOWED_ORIGINS` | 允许的跨域源 | 按部署域名填写 |

### 日志配置

| 变量 | 说明 | 默认值 |
|--------|------|--------|
| `DJANGO_LOG_LEVEL` | 日志级别 | `INFO` |

### 爬虫配置

| 变量 | 说明 | 默认值 |
|--------|------|--------|
| `CRAWLER_PLATFORM` | 默认平台 | `xhs` |
| `CRAWLER_LOGIN_TYPE` | 默认登录方式 | `qrcode` |
| `CRAWLER_TYPE` | 默认爬虫类型 | `search` |
| `CRAWLER_KEYWORDS` | 搜索关键词 | - |

### 数据存储配置

| 变量 | 说明 | 默认值 |
|--------|------|--------|
| `DATA_DIR` | 数据目录 | `data` |
| `SAVE_DATA_OPTION` | 存储方式 | `db` |

存储方式选项：
- `json` - JSON 文件
- `csv` - CSV 文件
- `excel` - Excel 文件
- `db` - MySQL 数据库
- `mongodb` - MongoDB 数据库

## 数据库迁移

```bash
# 创建迁移文件
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

## 运行开发服务器

```bash
python manage.py runserver 0.0.0.0:8000
```

或使用环境变量指定的端口：

```bash
python manage.py runserver $HOST:$PORT
```

## API 端点

### 健康与配置

| 端点 | 方法 | 描述 |
|--------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/config/platforms` | GET | 获取支持的平台列表 |
| `/api/config/options` | GET | 获取配置选项 |
| `/api/env/check` | GET | 检查环境配置 |

### 爬虫控制

| 端点 | 方法 | 描述 |
|--------|------|------|
| `/api/crawler/start` | POST | 启动爬虫 |
| `/api/crawler/stop` | POST | 停止爬虫 |
| `/api/crawler/status` | GET | 获取爬虫状态 |
| `/api/crawler/logs` | GET | 获取日志 |

### 数据管理

| 端点 | 方法 | 描述 |
|--------|------|------|
| `/api/data/files` | GET | 获取数据文件列表 |
| `/api/data/files/<path>` | GET | 获取文件内容 |
| `/api/data/download/<path>` | GET | 下载文件 |
| `/api/data/stats` | GET | 获取数据统计 |

### 管理后台

- `/admin/` - Django 管理后台

## 数据模型

项目包含以下数据模型：

### Bilibili (bilibili_*)
- `BilibiliVideo` - 视频信息
- `BilibiliVideoComment` - 视频评论
- `BilibiliUpInfo` - UP主信息
- `BilibiliContactInfo` - 联系信息
- `BilibiliUpDynamic` - UP动态

### Douyin (douyin_*)
- `DouyinAweme` - 视频信息
- `DouyinAwemeComment` - 视频评论
- `DyCreator` - 创作者信息

### Kuaishou (kuaishou_*)
- `KuaishouVideo` - 视频信息
- `KuaishouVideoComment` - 视频评论

### Weibo (weibo_*)
- `WeiboNote` - 微博内容
- `WeiboNoteComment` - 评论
- `WeiboCreator` - 创作者信息

### Xiaohongshu (xhs_*)
- `XhsNote` - 笔记内容
- `XhsNoteComment` - 评论
- `XhsCreator` - 创作者信息

### Tieba (tieba_*)
- `TiebaNote` - 帖子内容
- `TiebaComment` - 评论
- `TiebaCreator` - 创作者信息

### Zhihu (zhihu_*)
- `ZhihuContent` - 内容
- `ZhihuComment` - 评论
- `ZhihuCreator` - 创作者信息

## 配置工具使用

```python
# 导入配置工具
from mediacrawler_config.utils.config import config, get_env

# 访问配置
print(config.debug)          # 调试模式
print(config.server.host)      # 服务器地址
print(config.crawler.platform) # 爬虫平台

# 获取环境变量
api_key = get_env('API_KEY', 'default')

# 重新加载配置
config.reload()
```

## 生产环境部署

### 安全设置

在生产环境中，确保设置以下环境变量：

```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-super-secret-key-here
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 生成密钥

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn mediacrawler_config.wsgi:application --bind 0.0.0.0:8000
```

### 使用 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 许可证

本项目基于 NON-COMMERCIAL LEARNING LICENSE 1.1 许可证发布。

## 作者

relakkes@gmail.com

## 原项目

[MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) by NanmiCoder
