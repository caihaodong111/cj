#!/bin/bash
# 平台官方Logo下载脚本
# 使用方法: cd frontend/src/assets/platform-logos && bash download-logos.sh

cd "$(dirname "$0")"

echo "开始下载各平台官方Logo..."

# 小红书logo - 从Wikimedia下载
echo "下载小红书logo..."
curl -L -o xhs-logo.png "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Xiaohongshu_LOGO.png/240px-Xiaohongshu_LOGO.png"

# 抖音logo
echo "下载抖音logo..."
# 抖音没有公开的高清logo下载，这里使用官方favicon
curl -L -o douyin-logo.png "https://www.douyin.com/favicon.ico"

# 快手logo
echo "下载快手logo..."
curl -L -o kuaishou-logo.png "https://www.kuaishou.com/favicon.ico"

# B站logo
echo "下载Bilibili logo..."
curl -L -o bilibili-logo.png "https://www.bilibili.com/images/favicon.ico"

# 微博logo
echo "下载微博logo..."
curl -L -o weibo-logo.png "https://weibo.com/favicon.ico"

# 贴吧logo
echo "下载贴吧logo..."
curl -L -o tieba-logo.png "https://tieba.baidu.com/favicon.ico"

# 知乎logo
echo "下载知乎logo..."
curl -L -o zhihu-logo.png "https://static.zhihu.com/heifetz/favicon.ico"

echo "下载完成！"
echo "注意：部分logo可能需要手动下载，请参考以下链接："
echo ""
echo "1. 小红书: https://www.xiaohongshu.com/"
echo "2. 抖音: https://www.douyin.com/"
echo "3. 快手: https://www.kuaishou.com/"
echo "4. B站: https://www.bilibili.com/"
echo "5. 微博: https://weibo.com/"
echo "6. 贴吧: https://tieba.baidu.com/"
echo "7. 知乎: https://www.zhihu.com/"
echo ""
echo "建议：访问各平台官网，右键保存logo图标到本目录"
