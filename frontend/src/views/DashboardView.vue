<template>
  <div class="dashboard-wrapper">
    <!-- Ambient Background Effects -->
    <div class="ambient-background">
      <div class="blue-halo"></div>
      <div class="grid-background"></div>
      <div class="particles">
        <div class="particle" v-for="i in 8" :key="i" :style="{ animationDelay: `${i * 1.5}s` }"></div>
      </div>
    </div>

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

      <!-- 分页控制 -->
      <div v-if="feedItems && feedItems.length > 0" class="pagination-wrapper">
        <div class="pagination-info">
          <span class="pagination-text">共 {{ totalCount }} 条数据</span>
          <span class="pagination-divider">|</span>
          <span class="pagination-text">第 {{ currentPage }} / {{ totalPages }} 页</span>
        </div>
        <div class="pagination-controls">
          <button
            class="pagination-btn"
            :disabled="currentPage === 1"
            @click="goToPage(1)"
          >
            首页
          </button>
          <button
            class="pagination-btn"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            上一页
          </button>
          <div class="pagination-numbers">
            <button
              v-for="page in displayedPages"
              :key="page"
              class="pagination-number"
              :class="{ active: page === currentPage, ellipsis: page === '...' }"
              :disabled="page === '...'"
              @click="page !== '...' && goToPage(page)"
            >
              {{ page }}
            </button>
          </div>
          <button
            class="pagination-btn"
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            下一页
          </button>
          <button
            class="pagination-btn"
            :disabled="currentPage === totalPages"
            @click="goToPage(totalPages)"
          >
            末页
          </button>
        </div>
      </div>
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
    backgroundColor: 'rgba(10, 10, 15, 0.95)',
    borderColor: 'rgba(0, 204, 255, 0.3)',
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
    axisLine: { lineStyle: { color: 'rgba(0, 204, 255, 0.2)' } },
    axisLabel: { color: '#aaaaaa' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: 'rgba(0, 204, 255, 0.1)' } },
    axisLabel: { color: '#aaaaaa' }
  },
  series: [
    {
      name: '声量',
      type: 'line',
      stack: 'Total',
      smooth: true,
      lineStyle: { width: 3, color: '#00ccff' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: 'rgba(0, 204, 255, 0.5)' }, { offset: 1, color: 'rgba(0, 204, 255, 0)' }]
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
      lineStyle: { width: 3, color: '#ff6b6b' },
      areaStyle: { opacity: 0 },
      data: [20, 32, 11, 34, 10, 30, 20]
    }
  ]
}))

const pieChartOptions = computed(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(10, 10, 15, 0.95)',
    borderColor: 'rgba(0, 204, 255, 0.3)',
    textStyle: { color: '#fff' }
  },
  legend: {
    bottom: '5%',
    left: 'center',
    textStyle: { color: '#aaaaaa' }
  },
  series: [
    {
      name: 'Sentiment',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#000000',
        borderWidth: 2
      },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 20, fontWeight: 'bold', color: '#fff' }
      },
      labelLine: { show: false },
      data: [
        { value: 1048, name: '积极', itemStyle: { color: '#00ff88' } },
        { value: 735, name: '中性', itemStyle: { color: '#0066ff' } },
        { value: 580, name: '消极', itemStyle: { color: '#ff6b6b' } }
      ]
    }
  ]
}))

const feedItems = ref([])
const feedLoading = ref(false)
const lastUpdatedAt = ref(null)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(100)
const totalCount = ref(0)
const totalPages = ref(1)

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

// 分页计算属性 - 显示页码范围（带省略号）
const displayedPages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  const delta = 2 // 当前页前后显示的页数

  // 总是显示第一页
  pages.push(1)

  // 如果第一页不是当前页且距离较远，添加省略号
  if (current > delta + 3) {
    pages.push('...')
  }

  // 当前页附近的页码
  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    pages.push(i)
  }

  // 如果最后一页不是当前页且距离较远，添加省略号
  if (current < total - delta - 2) {
    pages.push('...')
  }

  // 总是显示最后一页
  if (total > 1) {
    pages.push(total)
  }

  return pages
})

// 页面跳转函数
const goToPage = async (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  // 滚动到列表顶部
  const listWrapper = document.querySelector('.list-wrapper')
  if (listWrapper) {
    listWrapper.scrollTop = 0
  }
  // 获取该页数据
  await fetchMonitorFeedPage()
}

// 获取指定页的数据
const fetchMonitorFeedPage = async ({ withLoading = true, signal = null } = {}) => {
  // 如果请求已被取消，直接返回
  if (signal?.aborted) return

  if (withLoading) {
    feedLoading.value = true
  }
  try {
    const res = await axios.get('/api/monitor/feed', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      },
      signal
    })
    // 请求完成后再次检查是否被取消
    if (signal?.aborted) return

    const items = Array.isArray(res.data?.items) ? res.data.items : []
    console.log('API Response success:', items.length, 'items')

    // 更新分页信息
    if (res.data?.pagination) {
      totalCount.value = res.data.pagination.total_count || 0
      totalPages.value = res.data.pagination.total_pages || 1
    }

    const merged = buildFeedItems(items)
    console.log('buildFeedItems result:', merged.length, 'items')

    feedItems.value = merged

    lastUpdatedAt.value = res.data?.fetched_at || new Date()
    console.log('fetchMonitorFeed complete, feedItems.value.length:', feedItems.value.length)
  } catch (e) {
    // 如果是主动取消的错误，不处理
    if (e.name === 'CanceledError' || e.code === 'ERR_CANCELED') return
    if (signal?.aborted) return

    // 只在组件未卸载时更新状态
    feedItems.value = []
    totalCount.value = 0
    totalPages.value = 1
    lastUpdatedAt.value = new Date()
    console.log('fetchMonitorFeed error:', e.message)
  } finally {
    if (withLoading && !signal?.aborted) {
      feedLoading.value = false
    }
  }
}

// 刷新数据（重置到第一页）
const fetchMonitorFeed = async ({ withLoading = true, signal = null } = {}) => {
  currentPage.value = 1
  await fetchMonitorFeedPage({ withLoading, signal })
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
  position: relative;
  z-index: 1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
  overflow-y: auto;
  scroll-behavior: smooth;
}

/* Cyberpunk Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--cyan-primary);
  border-radius: 4px;
  box-shadow: 0 0 10px var(--cyan-primary);
  transition: all 0.3s;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--blue-secondary);
  box-shadow: 0 0 15px var(--blue-secondary);
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
  border-radius: 20px;
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid var(--border-cyan);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow:
    0 0 40px rgba(0, 204, 255, 0.1),
    0 4px 24px rgba(0, 0, 0, 0.4);
}

.stat-card:hover {
  transform: translateY(-5px);
  border-color: var(--glow-cyan);
  box-shadow:
    0 0 60px rgba(0, 204, 255, 0.2),
    0 8px 32px rgba(0, 0, 0, 0.6);
}

.stat-icon {
  font-size: 2.5rem;
  background: rgba(0, 204, 255, 0.08);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid rgba(0, 204, 255, 0.2);
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.2);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-info .label {
  font-size: 0.75rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 500;
}

.stat-info .value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-white);
  margin: 0.2rem 0;
  letter-spacing: 1px;
}

.stat-info .value.warning {
  color: #ff6b6b;
  text-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
}

.stat-info .value.positive {
  color: var(--green-status);
  text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
}

.stat-info .trend {
  font-size: 0.75rem;
  color: var(--text-dim);
  letter-spacing: 0.5px;
}

.stat-info .trend.up {
  color: var(--green-status);
}

.stat-info .trend.down {
  color: #ff6b6b;
}

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
  border-radius: 20px;
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid var(--border-cyan);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 300px;
  box-shadow:
    0 0 40px rgba(0, 204, 255, 0.1),
    0 4px 24px rgba(0, 0, 0, 0.4);
}

.recent-list h3 {
  margin: 0;
  font-size: 1rem;
  color: var(--cyan-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 600;
  text-shadow: 0 0 20px rgba(0, 204, 255, 0.5);
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
  color: var(--text-dim);
  letter-spacing: 0.5px;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  border: 1px solid var(--border-cyan);
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.3), rgba(0, 204, 255, 0.15));
  color: var(--cyan-primary);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-weight: 500;
  letter-spacing: 0.5px;
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.2);
}

.refresh-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.4), rgba(0, 204, 255, 0.25));
  border-color: var(--glow-cyan);
  box-shadow: 0 0 30px rgba(0, 204, 255, 0.4);
  transform: translateY(-2px);
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
  color: var(--text-dim);
  padding: 1rem 0;
  flex: 1;
}

.feed-state .hint {
  font-size: 0.8rem;
  color: var(--text-dim);
  opacity: 0.7;
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
  background: rgba(0, 204, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(0, 204, 255, 0.1);
  opacity: 0;
  transform: translateX(-20px);
  animation: fadeSlideIn 0.4s ease-out forwards;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeSlideIn {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.list-item:hover {
  background: rgba(0, 204, 255, 0.08);
  border-color: var(--border-cyan);
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.15);
}

.platform-tag {
  background: rgba(0, 102, 255, 0.2);
  color: var(--cyan-primary);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.5px;
  border: 1px solid rgba(0, 204, 255, 0.2);
  text-transform: uppercase;
}

.content {
  flex: 1;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-light);
}

.time {
  font-size: 0.8rem;
  color: var(--text-dim);
  font-weight: 500;
}

.author {
  font-size: 0.8rem;
  color: var(--text-light);
  font-weight: 500;
}

.author.muted {
  color: var(--text-dim);
}

/* 加载动画 */
.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--cyan-primary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.5);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Cyberpunk Style - CSS Variables */
:root {
  --cyan-primary: #00ccff;
  --blue-secondary: #0066ff;
  --orange-gold: #ffae00;
  --green-status: #00ff88;
  --text-white: #FFFFFF;
  --text-gray: #888888;
  --text-light: #aaaaaa;
  --text-dim: #666666;
  --bg-pure-black: #000000;
  --bg-glass: rgba(255, 255, 255, 0.03);
  --border-cyan: rgba(0, 204, 255, 0.2);
  --glow-cyan: rgba(0, 204, 255, 0.4);
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background: var(--bg-pure-black);
  color: var(--text-white);
}

/* Dashboard Wrapper with Cyberpunk Background */
.dashboard-wrapper {
  min-height: 100vh;
  background: var(--bg-pure-black);
  position: relative;
  overflow: hidden;
}

/* Ambient Background Effects */
.ambient-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

/* Blue Halo - Top Left Corner */
.blue-halo {
  position: absolute;
  top: -100px;
  left: -100px;
  width: 500px;
  height: 500px;
  background: radial-gradient(ellipse, rgba(0, 102, 255, 0.5) 0%, transparent 70%);
  animation: bluePulse 4s ease-in-out infinite alternate;
}

@keyframes bluePulse {
  0% { opacity: 0.6; transform: scale(1); }
  100% { opacity: 1; transform: scale(1.1); }
}

/* Perspective Grid Background */
.grid-background {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 50%;
  background-image:
    linear-gradient(rgba(0, 204, 255, 0.15) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 204, 255, 0.15) 1px, transparent 1px);
  background-size: 50px 50px;
  transform: perspective(500px) rotateX(60deg);
  transform-origin: bottom center;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% { background-position: 0 0; }
  100% { background-position: 0 50px; }
}

/* Floating Particles */
.particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  bottom: -10px;
  width: 3px;
  height: 3px;
  background: var(--cyan-primary);
  border-radius: 50%;
  opacity: 0;
  animation: particleFloat 15s linear infinite;
}

@keyframes particleFloat {
  0% {
    opacity: 0;
    transform: translateY(0) translateX(0);
  }
  10% {
    opacity: 0.8;
  }
  90% {
    opacity: 0.8;
  }
  100% {
    opacity: 0;
    transform: translateY(-100vh) translateX(50px);
  }
}

/* Distribute particles horizontally */
.particle:nth-child(1) { left: 10%; }
.particle:nth-child(2) { left: 20%; }
.particle:nth-child(3) { left: 30%; }
.particle:nth-child(4) { left: 40%; }
.particle:nth-child(5) { left: 50%; }
.particle:nth-child(6) { left: 60%; }
.particle:nth-child(7) { left: 70%; }
.particle:nth-child(8) { left: 80%; }

.glass {
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(30px) saturate(180%);
  border: 1px solid var(--border-cyan);
  border-radius: 20px;
  box-shadow:
    0 0 40px rgba(0, 204, 255, 0.1),
    0 4px 24px rgba(0, 0, 0, 0.4);
}

/* Pagination Styles */
.pagination-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-cyan);
  flex-wrap: wrap;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-dim);
  font-size: 0.85rem;
}

.pagination-divider {
  color: var(--border-cyan);
}

.pagination-text {
  color: var(--text-light);
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-btn {
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  border: 1px solid var(--border-cyan);
  background: rgba(0, 204, 255, 0.05);
  color: var(--cyan-primary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  font-size: 0.85rem;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.pagination-btn:hover:not(:disabled) {
  background: rgba(0, 204, 255, 0.15);
  border-color: var(--glow-cyan);
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.3);
  transform: translateY(-1px);
}

.pagination-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pagination-numbers {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.pagination-number {
  min-width: 36px;
  height: 36px;
  padding: 0;
  border-radius: 8px;
  border: 1px solid var(--border-cyan);
  background: rgba(0, 204, 255, 0.05);
  color: var(--text-light);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-number:hover:not(:disabled):not(.ellipsis) {
  background: rgba(0, 204, 255, 0.15);
  border-color: var(--glow-cyan);
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.3);
  transform: translateY(-1px);
}

.pagination-number.active {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.4), rgba(0, 204, 255, 0.25));
  border-color: var(--glow-cyan);
  color: var(--text-white);
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.4);
}

.pagination-number.ellipsis {
  border: none;
  background: transparent;
  color: var(--text-dim);
  cursor: default;
}

.pagination-number:disabled {
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .pagination-wrapper {
    flex-direction: column;
    gap: 1rem;
  }

  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }

  .pagination-numbers {
    order: -1;
    width: 100%;
    justify-content: center;
  }
}
</style>
