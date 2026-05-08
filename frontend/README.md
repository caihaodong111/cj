# MediaCrawler Frontend

`frontend/` 是 MediaCrawler 舆情监测平台的前端模块，基于 `Vue 3 + Vite` 实现，负责数据展示、爬虫操作入口、深度分析可视化和系统设置管理。

完整项目说明见仓库根目录 [README.md](../README.md)。

## 技术栈

- Vue 3
- Vite
- Vue Router
- Element Plus
- ECharts
- Axios

## 页面结构

| 页面 | 路由 | 说明 |
|------|------|------|
| Dashboard | `/dashboard` | 展示各平台敏感数据分布、平台卡片图表、Monitor Feed 实时动态 |
| Data | `/data` | 平台切换、爬虫启动/停止、敏感/全量数据列表、筛选和排序 |
| Analysis | `/analysis` | 关键词云、摘要、风险提示、情绪趋势分析 |
| Settings | `/settings` | Cookie 配置管理和爬虫参数入口 |

## 本地开发

```bash
cd frontend
npm install
npm run dev
```

默认开发地址：`http://127.0.0.1:5173`

## 可用脚本

```bash
npm run dev
npm run build
npm run preview
```

## 开发约定

- `vite.config.js` 已将 `/api` 代理到 `http://127.0.0.1:8000`
- 前端依赖后端接口，开发时建议先启动 Django 服务
- 深度分析页面依赖后端 AI 接口；若未配置 `ZHIPU_API_KEY`，对应能力不可用

## 目录说明

```text
frontend/
├── src/components/     # 通用组件，如图表卡片、爬虫控制组件
├── src/layouts/        # 主布局
├── src/router/         # 前端路由
├── src/views/          # Dashboard / Data / Analysis / Settings
├── src/assets/         # 平台 logo 等静态资源
├── vite.config.js      # 开发代理配置
└── package.json        # 依赖与脚本
```

## 当前工程状态

- 当前仅提供 `dev`、`build`、`preview` 三个脚本
- 还没有 `lint` 脚本
- 还没有前端测试脚本和测试目录
- 如需项目级背景、部署和接口概览，请回到 [README.md](../README.md)
