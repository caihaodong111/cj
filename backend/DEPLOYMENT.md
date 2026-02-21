# MediaCrawler Backend - 生产环境部署指南

服务器信息：`39.105.122.26`

## 部署前准备

### 1. 服务器环境要求

- 操作系统：Linux (Ubuntu/CentOS/AlmaLinux)
- Docker：>= 20.10
- Docker Compose：>= 2.0
- MySQL：>= 5.7 (需要预先安装)
- 内存：建议 >= 4GB
- 磁盘：建议 >= 20GB

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

确保 MySQL 已安装并运行：

```bash
# 检查 MySQL 状态
sudo systemctl status mysql

# 创建数据库和用户（如果还没有）
mysql -u root -p
```

```sql
CREATE DATABASE lxr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lxr'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON lxr.* TO 'lxr'@'%';
FLUSH PRIVILEGES;
```

## 部署步骤

### 1. 上传项目文件到服务器

```bash
# 在本地，将 backend 目录上传到服务器
scp -r backend/ root@39.105.122.26:/opt/mediacrawler/backend

# 或使用 rsync
rsync -avz --progress backend/ root@39.105.122.26:/opt/mediacrawler/backend
```

### 2. 配置环境变量

在服务器上：

```bash
cd /opt/mediacrawler/backend

# 生成安全的 SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 复制并编辑环境配置
cp .env.production .env
nano .env  # 或使用 vim
```

**必须修改的配置项：**

```bash
# .env 文件关键配置
DJANGO_SECRET_KEY=<使用上面生成的密钥>
DJANGO_SECRET_KEY=your_secure_random_secret_key_here
DB_PASSWORD=your_actual_mysql_password
```

### 3. 一键部署

```bash
# 赋予执行权限
chmod +x deploy.sh

# 执行完整部署
./deploy.sh deploy
```

部署脚本会自动完成以下操作：
1. 构建 Docker 镜像
2. 启动服务
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

### 2. 检查健康状态

```bash
./deploy.sh health
```

或直接访问：`http://39.105.122.26:8000/api/health`

### 3. 查看日志

```bash
# 实时查看日志
./deploy.sh logs

# 或使用 docker compose
docker compose logs -f backend
```

## 服务访问地址

| 服务 | 地址 |
|------|------|
| API 根路径 | http://39.105.122.26:8000/ |
| 健康检查 | http://39.105.122.26:8000/api/health |
| 管理后台 | http://39.105.122.26:8000/admin/ |
| API 文档 | http://39.105.122.26:8000/api/docs |

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

# 进入容器 Shell
./deploy.sh shell

# 进入数据库 Shell
./deploy.sh dbshell

# 运行迁移
./deploy.sh migrate

# 清理（删除所有容器和卷）
./deploy.sh clean
```

## 使用 Docker Compose 命令

```bash
# 查看日志
docker compose logs -f backend

# 重启单个服务
docker compose restart backend

# 进入容器
docker compose exec backend bash

# 在容器中执行命令
docker compose exec backend python manage.py shell

# 查看资源使用
docker compose stats
```

## Nginx 反向代理配置（可选）

如果需要使用域名和 HTTPS，配置 Nginx：

```nginx
# /etc/nginx/sites-available/mediacrawler
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /static/ {
        alias /opt/mediacrawler/backend/staticfiles/;
    }

    # 媒体文件
    location /media/ {
        alias /opt/mediacrawler/backend/media/;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/mediacrawler /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL 证书配置（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker compose logs backend

# 检查数据库连接
docker compose exec backend python manage.py check
```

### 数据库连接失败

1. 检查 MySQL 是否运行
2. 确认防火墙允许 3306 端口
3. 验证 .env 中的数据库配置

### Playwright 浏览器问题

```bash
# 重新安装浏览器依赖
docker compose exec backend playwright install-deps chromium
```

## 安全建议

1. 修改默认的 SECRET_KEY
2. 使用强密码
3. 配置防火墙只开放必要端口
4. 定期更新系统和 Docker 镜像
5. 启用 HTTPS
6. 配置日志轮转

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并部署
./deploy.sh deploy
```

## 备份

```bash
# 数据库备份
mysqldump -u lxr -p lxr > backup_$(date +%Y%m%d).sql

# 恢复
mysql -u lxr -p lxr < backup_20250217.sql
```
