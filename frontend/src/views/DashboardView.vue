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
      <div class="list-wrapper" v-if="feedItems.length > 0">
        <div class="list-item" v-for="item in feedItems" :key="item.id">
          <span class="platform-tag">{{ item.platformLabel }}</span>
          <span class="content">{{ item.content }}</span>
          <span class="time">{{ item.timeLabel }}</span>
          <span class="sentiment" :class="item.sentimentClass">{{ item.sentimentLabel }}</span>
        </div>
      </div>
      <div v-else-if="feedLoading" class="feed-state">
        <div class="loading-spinner"></div>
        <p>正在获取最新动态...</p>
      </div>
      <div v-else class="feed-state">
        <p>暂无数据动态</p>
        <p class="hint">请先在数据采集界面生成数据</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import ChartCard from '../components/ChartCard.vue'

// Mock Data Options for Charts
const trendChartOptions = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(0,0,0,0.7)',
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

const inferPlatformFromPath = (path) => {
  return normalizePlatform(path)
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

const parseSentiment = (row) => {
  const raw = row?.sentiment || row?.sentiment_label || row?.emotion || row?.sentimentType
  if (!raw) return { label: '未知', klass: 'neutral' }
  const value = String(raw).toLowerCase()
  if (value.includes('positive') || value.includes('积极') || value.includes('正面')) {
    return { label: '积极', klass: 'positive' }
  }
  if (value.includes('negative') || value.includes('消极') || value.includes('负面')) {
    return { label: '消极', klass: 'negative' }
  }
  if (value.includes('neutral') || value.includes('中性')) {
    return { label: '中性', klass: 'neutral' }
  }
  return { label: String(raw), klass: 'neutral' }
}

const getRecordTime = (row, fallbackSeconds) => {
  const candidates = ['created_time', 'created_at', 'publish_time', 'time', 'timestamp']
  for (const key of candidates) {
    if (row && row[key]) {
      const parsed = toMillis(row[key])
      if (parsed) return parsed
    }
  }
  return toMillis(fallbackSeconds)
}

const buildFeedItems = (file, rows) => {
  const platformKey = normalizePlatform(rows?.[0]?.platform || inferPlatformFromPath(file?.path || ''))
  return rows.map((row, index) => {
    const sentiment = parseSentiment(row)
    const recordTime = getRecordTime(row, file?.modified_at)
    return {
      id: row?.id || `${file?.path || 'data'}-${index}`,
      platformLabel: getPlatformLabel(platformKey),
      content: pickContent(row),
      timeLabel: formatRelativeTime(recordTime),
      sentimentLabel: sentiment.label,
      sentimentClass: sentiment.klass,
      sortTime: recordTime || 0
    }
  })
}

const fetchMonitorFeed = async ({ withLoading = true } = {}) => {
  if (withLoading) {
    feedLoading.value = true
  }
  try {
    const filesRes = await axios.get('/api/data/files')
    const files = Array.isArray(filesRes.data?.files) ? filesRes.data.files : []
    if (files.length === 0) {
      feedItems.value = []
      lastUpdatedAt.value = new Date()
      return
    }
    const targetFiles = files.slice(0, 3)
    const previews = await Promise.all(
      targetFiles.map(async (file) => {
        try {
          const res = await axios.get(`/api/data/files/${file.path}`, {
            params: { preview: true, limit: 5 }
          })
          const data = Array.isArray(res.data?.data) ? res.data.data : [res.data?.data].filter(Boolean)
          return { file, data }
        } catch (e) {
          return { file, data: [] }
        }
      })
    )
    const merged = previews.flatMap(({ file, data }) => buildFeedItems(file, data))
    feedItems.value = merged
      .sort((a, b) => b.sortTime - a.sortTime)
      .slice(0, 6)
    lastUpdatedAt.value = new Date()
  } catch (e) {
    feedItems.value = []
    lastUpdatedAt.value = new Date()
  } finally {
    if (withLoading) {
      feedLoading.value = false
    }
  }
}

const batchPlatforms = ['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu']

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const waitForCrawlerIdle = async (timeoutMs = 180000) => {
  const startedAt = Date.now()
  while (Date.now() - startedAt < timeoutMs) {
    try {
      const res = await axios.get('/api/crawler/status')
      if (res.data?.status === 'idle') {
        return true
      }
    } catch (e) {
      return false
    }
    await sleep(2000)
  }
  return false
}

const startBatchCrawler = async () => {
  await axios.post('/api/crawler/start', {
    platforms: batchPlatforms,
    crawler_type: 'search'
  })
}

const refreshMonitorFeed = async () => {
  if (feedLoading.value) return
  feedLoading.value = true
  try {
    await startBatchCrawler()
    await waitForCrawlerIdle()
    await fetchMonitorFeed({ withLoading: false })
  } catch (e) {
    await fetchMonitorFeed({ withLoading: false })
  } finally {
    feedLoading.value = false
  }
}

onMounted(() => {
  fetchMonitorFeed()
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
  min-height: 0;
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
  box-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
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

.sentiment {
  font-size: 0.8rem;
}
.sentiment.positive { color: #91CC75; }
.sentiment.neutral { color: #5470C6; }
.sentiment.negative { color: #EE6666; }
</style>
