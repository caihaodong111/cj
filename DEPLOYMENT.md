# MediaCrawler - 生产环境部署指南

完整项目部署（前端 + 后端）

服务器：`39.105.122.26`

## 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                     Nginx (Frontend)                    │
│                    Port: 80                             │
│              Vue.js + Static Files                      │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                 Django Backend                          │
│                    Port: 8000                           │
│              REST API + Admin Panel                     │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌──────────┐
│ MySQL  │   │ Redis  │   │ Playwright│
│:3306   │   │:6379   │   │ Browser   │
└────────┘   └────────┘   └──────────┘
```

## 部署前准备

### 1. 服务器环境要求

- 操作系统：Linux (Ubuntu/CentOS/AlmaLinux)
- Docker：>= 20.10
- Docker Compose：>= 2.0
- MySQL：>= 5.7 (需要预先安装)
- 内存：建议 >= 4GB
- 磁盘：建议 >= 20GB
- 端口：80, 8000, 3306, 6379

### 2. 安装 Docker 和 Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 验证安装
docker --version
docker compose version
```

### 3. 准备 MySQL 数据库

```bash
# 检查 MySQL 状态
sudo systemctl status mysql

# 创建数据库和用户
mysql -u root -p
```

```sql
CREATE DATABASE lxr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lxr'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON lxr.* TO 'lxr'@'%';
FLUSH PRIVILEGES;
```

### 4. 防火墙配置

```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 3306/tcp  # 如果需要远程访问MySQL

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## 部署步骤

### 1. 上传项目到服务器

```bash
# 在本地执行
scp -r MediaCrawler-main/ root@39.105.122.26:/opt/mediacrawler

# 或使用 rsync
rsync -avz --progress MediaCrawler-main/ root@39.105.122.26:/opt/mediacrawler
```

### 2. 配置环境变量

```bash
# 登录服务器
ssh root@39.105.122.26

# 进入项目目录
cd /opt/mediacrawler

# 复制环境配置模板
cp backend/.env.production .env

# 编辑配置
nano .env  # 或使用 vim
```

**必须修改的配置：**

```bash
# .env 文件关键配置
DJANGO_SECRET_KEY=<使用下面命令生成的密钥>
DB_PASSWORD=your_actual_mysql_password
CORS_ALLOWED_ORIGINS=http://39.105.122.26
```

生成 SECRET_KEY：

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. 一键部署

```bash
# 赋予执行权限（首次）
chmod +x deploy.sh

# 执行完整部署
./deploy.sh deploy
```

部署过程：
1. 构建 Docker 镜像（使用清华源加速）
2. 启动所有服务（前端、后端、Redis）
3. 运行数据库迁移
4. 收集静态文件

### 4. 创建管理员账户

```bash
./deploy.sh createsuperuser
```

按提示输入用户名、邮箱和密码。

## 部署后验证

### 1. 检查服务状态

```bash
./deploy.sh status
```

### 2. 健康检查

```bash
./deploy.sh health
```

### 3. 查看日志

```bash
# 所有服务日志
./deploy.sh logs

# 特定服务日志
./deploy.sh logs backend
./deploy.sh logs frontend
./deploy.sh logs redis
```

## 服务访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端应用** | http://39.105.122.26 | Vue.js 前端界面 |
| **API根路径** | http://39.105.122.26:8000/ | Django API |
| **健康检查** | http://39.105.122.26/api/health | 服务健康状态 |
| **管理后台** | http://39.105.122.26/admin/ | Django Admin |
| **API文档** | http://39.105.122.26:8000/api/docs | API 文档 |

## 常用运维命令

```bash
# 查看帮助
./deploy.sh help

# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 进入后端容器
./deploy.sh shell-backend

# 进入前端容器
./deploy.sh shell-frontend

# 进入数据库Shell
./deploy.sh dbshell

# 运行迁移
./deploy.sh migrate

# 清理（删除所有容器和卷）
./deploy.sh clean
```

## Docker Compose 命令

```bash
# 查看日志
docker compose logs -f

# 重启单个服务
docker compose restart backend

# 进入容器
docker compose exec backend bash

# 查看资源使用
docker compose stats

# 重建单个服务
docker compose up -d --build backend
```

## 网络架构

### 服务间通信

- 前端 (Nginx) 监听 `0.0.0.0:80`
- 前端通过 `http://backend:8000` 代理到后端
- 后端监听 `0.0.0.0:8000`
- 所有服务通过 Docker 网络互联

### 路由配置

| 路径 | 目标 |
|------|------|
| `/` | Frontend (Vue.js) |
| `/api/*` | Backend API |
| `/admin/*` | Django Admin |
| `/static/*` | Backend Static |
| `/media/*` | Backend Media |

## SSL/HTTPS 配置

使用 Let's Encrypt 免费 SSL 证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

修改 `frontend/default.conf` 添加 HTTPS：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... 其他配置
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 故障排查

### 前端无法访问

```bash
# 检查前端状态
docker compose ps frontend
docker compose logs frontend

# 检查 nginx 配置
docker compose exec frontend nginx -t
```

### 后端 API 无法访问

```bash
# 检查后端状态
docker compose ps backend
docker compose logs backend

# 检查数据库连接
docker compose exec backend python manage.py check
```

### 数据库连接失败

1. 检查 MySQL 是否运行：`sudo systemctl status mysql`
2. 验证 .env 中的数据库配置
3. 确认防火墙允许内部网络通信

### 构建速度慢

Dockerfile 已配置清华镜像源加速：
- Python 包：`https://pypi.tuna.tsinghua.edu.cn/simple`
- npm 包：`https://registry.npmmirror.com`
- Alpine/Debian：`mirrors.tuna.tsinghua.edu.cn`

## 性能优化

### Gunicorn 配置

当前配置（backend/Dockerfile）：
- 4 workers
- 2 threads per worker
- 120s timeout

根据服务器配置调整：

```dockerfile
--workers $(($(nproc) * 2)) \
--threads 4 \
```

### Nginx 缓存

已在 `frontend/default.conf` 配置静态文件缓存。

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并部署
./deploy.sh deploy
```

## 数据备份

```bash
# 数据库备份
docker compose exec backend bash -c "mysqldump -u lxr -p\$DB_PASSWORD lxr" > backup_$(date +%Y%m%d).sql

# 恢复
cat backup_20250221.sql | docker compose exec -T backend bash -c "mysql -u lxr -p\$DB_PASSWORD lxr"
```

## 监控

### 查看日志

```bash
# 实时日志
docker compose logs -f

# 日志大小限制（已配置）
# max-size: 10m
# max-file: 3
```

### 资源监控

```bash
# Docker 资源使用
docker compose stats

# 系统资源
htop
```

## 安全建议

1. 修改默认的 SECRET_KEY
2. 使用强密码
3. 配置防火墙只开放必要端口
4. 启用 HTTPS
5. 定期更新系统和 Docker 镜像
6. 限制数据库远程访问
7. 使用非 root 用户运行容器
