<template>
  <div class="dashboard-view">
    <!-- 顶部概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card glass">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <span class="label">总监测数据</span>
          <span class="value">12,458</span>
          <span class="trend up">+15% 较昨日</span>
        </div>
      </div>
      <div class="stat-card glass">
        <div class="stat-icon">⚠️</div>
        <div class="stat-info">
          <span class="label">敏感舆情</span>
          <span class="value warning">126</span>
          <span class="trend down">-2% 较昨日</span>
        </div>
      </div>
      <div class="stat-card glass">
        <div class="stat-icon">❤️</div>
        <div class="stat-info">
          <span class="label">情感指数</span>
          <span class="value positive">8.4</span>
          <span class="trend up">积极向好</span>
        </div>
      </div>
      <div class="stat-card glass">
        <div class="stat-icon">⚡</div>
        <div class="stat-info">
          <span class="label">实时热度</span>
          <span class="value">High</span>
          <span class="trend">监测中</span>
        </div>
      </div>
    </div>

    <!-- 主要图表区域 -->
    <div class="charts-grid">
      <div class="chart-wrapper wide">
        <ChartCard title="7日舆情声量趋势" :options="trendChartOptions" />
      </div>
      <div class="chart-wrapper">
        <ChartCard title="情感分布占比" :options="pieChartOptions" />
      </div>
    </div>

    <!-- 底部列表 -->
    <div class="recent-list glass">
      <div class="recent-header">
        <h3>Monitor Feed 实时动态</h3>
        <div class="feed-controls">
          <span class="feed-updated" v-if="lastUpdatedAt">更新于 {{ formatRelativeTime(lastUpdatedAt) }}</span>
          <button class="refresh-btn" :disabled="feedLoading" @click="refreshMonitorFeed">
            <span class="refresh-icon" :class="{ spinning: feedLoading }">⟳</span>
            {{ feedLoading ? '刷新中' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- 列表容器 -->
      <div v-if="feedItems && feedItems.length > 0" class="list-wrapper">
        <div class="list-item" v-for="(item, index) in feedItems" :key="item.id">
          <span class="platform-tag">{{ item.platformLabel }}</span>
          <span class="content">{{ item.content }}</span>
          <span class="time">{{ item.timeLabel }}</span>
          <span class="author" :class="{ muted: !item.authorLabel }">
            {{ item.authorLabel || '匿名' }}
          </span>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-else-if="feedLoading" class="feed-state">
        <div class="loading-spinner"></div>
        <p>正在获取最新动态...</p>
      </div>

      <!-- 无数据状态 -->
      <div v-else class="feed-state">
        <p>暂无数据动态</p>
        <p class="hint">请先在数据采集界面生成数据</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'
import ChartCard from '../components/ChartCard.vue'

// Mock Data Options for Charts
const trendChartOptions = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    textStyle: { color: '#fff' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    axisLine: { lineStyle: { color: '#555' } },
    axisLabel: { color: '#aaa' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#333' } },
    axisLabel: { color: '#aaa' }
  },
  series: [
    {
      name: '声量',
      type: 'line',
      stack: 'Total',
      smooth: true,
      lineStyle: { width: 3, color: '#FFD700' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(255, 215, 0, 0.5)' }, { offset: 1, color: 'rgba(255, 215, 0, 0)' }]
        }
      },
      emphasis: { focus: 'series' },
      data: [120, 132, 101, 134, 90, 230, 210]
    },
    {
      name: '负面',
      type: 'line',
      stack: 'Total',
      smooth: true,
      lineStyle: { width: 3, color: '#FF4500' },
      areaStyle: { opacity: 0 },
      data: [20, 32, 11, 34, 10, 30, 20]
    }
  ]
}))

const pieChartOptions = computed(() => ({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    bottom: '5%',
    left: 'center',
    textStyle: { color: '#aaa' }
  },
  series: [
    {
      name: 'Sentiment',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#050510',
        borderWidth: 2
      },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 20, fontWeight: 'bold', color: '#fff' }
      },
      labelLine: { show: false },
      data: [
        { value: 1048, name: '积极', itemStyle: { color: '#91CC75' } },
        { value: 735, name: '中性', itemStyle: { color: '#5470C6' } },
        { value: 580, name: '消极', itemStyle: { color: '#EE6666' } }
      ]
    }
  ]
}))

const feedItems = ref([])
const feedLoading = ref(false)
const lastUpdatedAt = ref(null)

// 请求管理：使用 AbortController 控制请求取消
const abortController = ref(null)
const refreshRequestId = ref(0)
const isMounted = ref(true)

const platformLabels = {
  xhs: '小红书',
  dy: '抖音',
  ks: '快手',
  bili: 'B站',
  wb: '微博',
  tieba: '贴吧',
  zhihu: '知乎'
}

const platformAliases = {
  xhs: ['xhs', 'xiaohongshu', 'redbook'],
  dy: ['dy', 'douyin', 'tiktok'],
  ks: ['ks', 'kuaishou'],
  bili: ['bili', 'bilibili'],
  wb: ['wb', 'weibo'],
  tieba: ['tieba', 'baidutieba'],
  zhihu: ['zhihu']
}

const normalizePlatform = (value) => {
  if (!value) return 'data'
  const normalized = String(value).toLowerCase()
  for (const [platform, aliases] of Object.entries(platformAliases)) {
    if (aliases.some(alias => normalized.includes(alias))) {
      return platform
    }
  }
  return normalized
}

const getPlatformLabel = (platformKey) => {
  return platformLabels[platformKey] || platformKey || '数据源'
}

const toMillis = (value) => {
  if (!value) return null
  if (value instanceof Date) return value.getTime()
  if (typeof value === 'number') {
    return value < 1e12 ? value * 1000 : value
  }
  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return null
    const numeric = Number(trimmed)
    if (!Number.isNaN(numeric)) {
      return numeric < 1e12 ? numeric * 1000 : numeric
    }
    const parsed = Date.parse(trimmed)
    return Number.isNaN(parsed) ? null : parsed
  }
  return null
}

const formatRelativeTime = (value) => {
  const ts = toMillis(value)
  if (!ts) return '刚刚'
  const diff = Date.now() - ts
  if (diff < 60 * 1000) return '刚刚'
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}分钟前`
  if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`
}

const pickContent = (row) => {
  if (!row) return '暂无内容'
  if (typeof row === 'string') return row
  const candidates = [
    'content',
    'title',
    'desc',
    'content_text',
    'text',
    'note_desc',
    'summary',
    'message',
    'comment'
  ]
  for (const key of candidates) {
    if (row[key]) return String(row[key])
  }
  const firstString = Object.values(row).find(val => typeof val === 'string' && val.trim())
  if (firstString) return firstString
  try {
    return JSON.stringify(row)
  } catch (e) {
    return '暂无内容'
  }
}

const getRecordTime = (row, fallbackSeconds) => {
  const candidates = ['created_time', 'create_time', 'created_at', 'publish_time', 'time', 'timestamp']
  for (const key of candidates) {
    if (row && row[key]) {
      const parsed = toMillis(row[key])
      if (parsed) return parsed
    }
  }
  return toMillis(fallbackSeconds)
}

const buildFeedItems = (rows) => {
  if (!rows || !Array.isArray(rows)) {
    console.log('buildFeedItems: invalid rows', rows)
    return []
  }
  console.log('buildFeedItems: processing', rows.length, 'items')
  return rows.map((row, index) => {
    const platformKey = normalizePlatform(row?.platform)
    const recordTime = row?.created_at || getRecordTime(row)
    const item = {
      id: row?.id || `${platformKey || 'data'}-${index}`,
      platformLabel: row?.platform_name || getPlatformLabel(platformKey),
      content: row?.content || pickContent(row),
      timeLabel: formatRelativeTime(recordTime),
      authorLabel: row?.author || '',
      url: row?.url || '',
      sortTime: recordTime || 0
    }
    console.log('buildFeedItems: built item', index, item)
    return item
  })
}

const fetchMonitorFeed = async ({ withLoading = true, signal = null } = {}) => {
  // 如果请求已被取消，直接返回
  if (signal?.aborted) return

  if (withLoading) {
    feedLoading.value = true
  }
  try {
    const res = await axios.get('/api/monitor/feed', {
      params: { limit: 20, per_platform: 10 },
      signal
    })
    // 请求完成后再次检查是否被取消
    if (signal?.aborted) return

    const items = Array.isArray(res.data?.items) ? res.data.items : []
    console.log('API Response success:', items.length, 'items')

    const merged = buildFeedItems(items)
    console.log('buildFeedItems result:', merged.length, 'items')

    feedItems.value = merged
      .sort((a, b) => b.sortTime - a.sortTime)
      .slice(0, 20)

    lastUpdatedAt.value = res.data?.fetched_at || new Date()
    console.log('fetchMonitorFeed complete, feedItems.value.length:', feedItems.value.length)
  } catch (e) {
    // 如果是主动取消的错误，不处理
    if (e.name === 'CanceledError' || e.code === 'ERR_CANCELED') return
    if (signal?.aborted) return

    // 只在组件未卸载时更新状态
    feedItems.value = []
    lastUpdatedAt.value = new Date()
    console.log('fetchMonitorFeed error:', e.message)
  } finally {
    if (withLoading && !signal?.aborted) {
      feedLoading.value = false
    }
  }
}

const batchPlatforms = ['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu']

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const waitForCrawlerIdle = async (timeoutMs = 180000, signal = null) => {
  const startedAt = Date.now()
  while (Date.now() - startedAt < timeoutMs) {
    if (signal?.aborted) return false
    try {
      const res = await axios.get('/api/crawler/status', { signal })
      if (res.data?.status === 'idle') {
        return true
      }
    } catch (e) {
      if (e.name === 'CanceledError' || e.code === 'ERR_CANCELED') return false
      return false
    }
    await sleep(2000)
  }
  return false
}

const startBatchCrawler = async (signal = null) => {
  await axios.post('/api/crawler/start', {
    platforms: batchPlatforms,
    crawler_type: 'search',
    login_type: 'cookie',
    headless: true
  }, { signal })
}

const refreshMonitorFeed = async () => {
  if (feedLoading.value) return

  // 创建新的 AbortController 和请求 ID
  const controller = new AbortController()
  abortController.value = controller
  const currentRequestId = ++refreshRequestId.value

  feedLoading.value = true
  console.log('refreshMonitorFeed started')

  try {
    // 启动爬虫
    await startBatchCrawler(controller.signal)
    if (controller.signal.aborted) return

    // 等待爬虫完成
    await waitForCrawlerIdle(180000, controller.signal)
    if (controller.signal.aborted) return

    // 获取最新数据
    await fetchMonitorFeed({ withLoading: false, signal: controller.signal })
  } catch (e) {
    // 如果是取消操作，不处理
    if (e.name === 'CanceledError' || e.code === 'ERR_CANCELED') return
    if (controller.signal.aborted) return

    // 其他错误，仍然尝试获取数据
    await fetchMonitorFeed({ withLoading: false, signal: controller.signal })
  } finally {
    // 只有当前请求且组件仍挂载时才清理状态
    if (currentRequestId === refreshRequestId.value && !controller.signal.aborted && isMounted.value) {
      feedLoading.value = false
      abortController.value = null
      // 只有刷新完成时才清理 localStorage
      localStorage.removeItem('dashboard-refresh-running')
      localStorage.removeItem('dashboard-refresh-start-time')
    }
  }
}

const checkCrawlerAndFetch = async () => {
  try {
    const res = await axios.get('/api/crawler/status')
    if (res.data?.status === 'idle') {
      // 爬虫已完成，获取数据
      await fetchMonitorFeed()
    } else {
      // 爬虫还在运行，继续等待
      feedLoading.value = true
      const controller = new AbortController()
      abortController.value = controller
      const currentRequestId = ++refreshRequestId.value

      try {
        await waitForCrawlerIdle(180000, controller.signal)
        if (!controller.signal.aborted) {
          await fetchMonitorFeed({ withLoading: false, signal: controller.signal })
        }
      } catch (e) {
        // 忽略错误
      } finally {
        if (currentRequestId === refreshRequestId.value && !controller.signal.aborted) {
          feedLoading.value = false
          abortController.value = null
        }
      }
    }
  } catch (e) {
    // 出错则重新获取
    await fetchMonitorFeed()
  }
}

onMounted(() => {
  isMounted.value = true
  // 重置加载状态，防止被旧状态阻塞
  feedLoading.value = false
  abortController.value = null

  // 先展示已有 monitor_feed 数据
  fetchMonitorFeed()
})

onBeforeUnmount(() => {
  isMounted.value = false
  // 保存当前刷新状态到 localStorage，以便返回时恢复
  if (feedLoading.value) {
    localStorage.setItem('dashboard-refresh-running', 'true')
    localStorage.setItem('dashboard-refresh-start-time', Date.now().toString())
  } else {
    localStorage.removeItem('dashboard-refresh-running')
    localStorage.removeItem('dashboard-refresh-start-time')
  }
})
</script>

<style scoped>
.dashboard-view {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
  overflow-y: auto;
  /* 优化滚动体验 */
  scroll-behavior: smooth;
}

/* 定义滚动条样式 */
.scrollbar-width: thin;
.scrollbar-color: rgba(255, 215, 0, 0.3) rgba(255, 255, 255, 0.05);

/* Webkit 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 215, 0, 0.3);
  border-radius: 4px;
  transition: background 0.2s;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 215, 0, 0.5);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.stat-card {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  border-radius: 12px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(255, 215, 0, 0.1);
}

.stat-icon {
  font-size: 2.5rem;
  background: rgba(255, 255, 255, 0.05);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-info .label {
  font-size: 0.85rem;
  color: var(--secondary-color);
  text-transform: uppercase;
}

.stat-info .value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0.2rem 0;
}

.stat-info .value.warning { color: #EE6666; }
.stat-info .value.positive { color: #91CC75; }

.stat-info .trend {
  font-size: 0.75rem;
  color: var(--secondary-color);
}

.stat-info .trend.up { color: #91CC75; }
.stat-info .trend.down { color: #EE6666; }

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  min-height: 400px;
}

/* Recent List */
.recent-list {
  padding: 1.5rem;
  border-radius: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 300px;
}

.recent-list h3 {
  margin: 0;
  font-size: 1rem;
  color: var(--primary-color);
}

.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.feed-controls {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.feed-updated {
  font-size: 0.75rem;
  color: var(--secondary-color);
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.7rem;
  border-radius: 6px;
  border: 1px solid rgba(255, 215, 0, 0.35);
  background: rgba(255, 215, 0, 0.12);
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 215, 0, 0.2);
  box-shadow: 0 10px rgba(255, 215, 0, 0.2);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  display: inline-block;
  transition: transform 0.2s;
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

.feed-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  color: var(--secondary-color);
  padding: 1rem 0;
  flex: 1;
}

.feed-state .hint {
  font-size: 0.8rem;
  color: var(--secondary-color);
}

.list-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-height: 200px;
  overflow-y: auto;
  padding-right: 0.35rem;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid transparent;
  opacity: 0;
  transform: translateX(-20px);
  animation: fadeSlideIn 0.4s ease-out forwards;
}

@keyframes fadeSlideIn {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.list-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 215, 0, 0.2);
}

.platform-tag {
  background: rgba(255, 0, 0, 0.2);
  color: #ffcccc;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
}

.content {
  flex: 1;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-color);
}

.time {
  font-size: 0.8rem;
  color: var(--secondary-color);
}

.author {
  font-size: 0.8rem;
  color: var(--text-color);
}

.author.muted {
  color: var(--secondary-color);
}

/* 加载动画 */
.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--primary-color);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 全局样式 */
:root {
  --primary-color: #FFD700;
  --secondary-color: #aaa;
  --text-color: #fff;
  --bg-glass: rgba(255, 255, 255, 0.05);
  --border-color: rgba(255, 215, 0, 0.15);
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 0%);
  color: var(--text-color);
}

.glass {
  background: var(--bg-glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
}
</style>
