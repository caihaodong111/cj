<template>
  <div class="data-wrapper">
    <!-- Ambient Background Effects -->
    <div class="ambient-background">
      <div class="nebula blue"></div>
      <div class="nebula gold"></div>
      <div class="breathing-line gold-1"></div>
      <div class="breathing-line gold-2"></div>
      <div class="scan-grid"></div>
      <div class="particles">
        <div class="particle" v-for="i in 8" :key="i" :style="{ animationDelay: `${i * 1.5}s` }"></div>
      </div>
    </div>

    <div class="data-view">
      <header class="page-header entrance-slide-in">
        <div class="title-area">
          <h1 class="ios-title">DATA SOURCE<span class="subtitle">数据源概览</span></h1>
        </div>
        <div class="header-actions">
          <button class="crawler-btn" type="button" @click="crawlerDialogVisible = true">
            <span class="btn-dot"></span>
            爬虫控制
          </button>
        </div>
      </header>

      <div class="kpi-selector-container">
        <button
          type="button"
          class="kpi-card ios-glass active hero-card entrance-scale-up"
          @click="drawerVisible = true"
        >
          <div class="border-glow gold-tint"></div>
          <div class="active-glow"></div>
          <div
            class="kpi-icon-box"
            :class="{
              'is-brand-logo': isBrandLogo(currentPlatform),
              'has-logo': getPlatformLogo(currentPlatform)
            }"
          >
            <img v-if="getPlatformLogo(currentPlatform)" :src="getPlatformLogo(currentPlatform)" :alt="getPlatformLabel(currentPlatform)" class="platform-logo-img" />
            <span v-else class="status-icon">{{ getPlatformIcon(currentPlatform) }}</span>
          </div>
          <div class="kpi-content">
            <div class="selector-label-row">
              <label>当前数据渠道</label>
              <span class="tap-hint">点击切换 →</span>
            </div>
            <div class="main-value" :class="{ 'brand-xhs': isBrandLogo(currentPlatform) }">
              {{ getDisplayLabel(currentPlatform) || currentPlatformStats.label || getPlatformLabel(currentPlatform) || '未选择' }}
            </div>
            <div class="status-mini-tags">
              <span class="tag total">总数 {{ currentTotalCount }}</span>
              <span class="tag sensitive">敏感 {{ currentSensitiveCount }}</span>
            </div>
          </div>
        </button>
      </div>

      <section class="data-table-section ios-glass entrance-scale-up-delay-4">
        <!-- Tabs -->
        <div class="custom-tabs">
          <button
            type="button"
            class="tab-item"
            :class="{ active: activeTab === 'sensitive' }"
            @click="activeTab = 'sensitive'"
          >
            敏感数据列表
            <span class="tab-indicator" v-show="activeTab === 'sensitive'"></span>
          </button>
          <button
            type="button"
            class="tab-item"
            :class="{ active: activeTab === 'all' }"
            @click="activeTab = 'all'"
          >
            所有数据信息列表
            <span class="tab-indicator" v-show="activeTab === 'all'"></span>
          </button>
        </div>

        <!-- Filter Bar -->
        <div class="filter-bar">
          <div class="filter-row">
            <!-- Search Input -->
            <div class="filter-item filter-search">
              <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="11" cy="11" r="8"/>
                <path d="M21 21l-4.35-4.35"/>
              </svg>
              <input
                v-model="searchKeyword"
                type="text"
                placeholder="搜索内容、昵称、ID..."
                class="filter-input"
                @keyup.enter="currentPage = 1"
              />
              <button
                v-if="searchKeyword"
                type="button"
                class="clear-btn"
                @click="searchKeyword = ''"
              >×</button>
            </div>

            <!-- Sentiment Filter -->
            <div class="filter-item">
              <select v-model="sentimentFilter" class="filter-select">
                <option value="all">全部情绪</option>
                <option value="positive">正面</option>
                <option value="negative">负面</option>
                <option value="neutral">中性</option>
                <option value="sensitive">敏感</option>
              </select>
            </div>

            <!-- Sensitive Filter -->
            <div class="filter-item">
              <select v-model="sensitiveFilter" class="filter-select">
                <option value="all">全部状态</option>
                <option value="sensitive">仅敏感</option>
                <option value="non-sensitive">非敏感</option>
              </select>
            </div>

            <!-- Interactions Filter -->
            <div class="filter-item">
              <select v-model="interactionsFilter" class="filter-select">
                <option value="all">全部互动</option>
                <option value="high">高互动 (1000+)</option>
                <option value="medium">中互动 (100-999)</option>
                <option value="low">低互动 (&lt;100)</option>
              </select>
            </div>

            <!-- Reset Button -->
            <button
              type="button"
              class="filter-reset"
              @click="resetFilters"
            >
              重置
            </button>
          </div>

          <!-- Result Count -->
          <div class="filter-info">
            <span v-if="searchKeyword || sentimentFilter !== 'all' || sensitiveFilter !== 'all' || interactionsFilter !== 'all'" class="filter-active">
              筛选中
            </span>
          </div>
        </div>
        <!-- Data Table -->
        <el-table
          :data="pagedRows"
          :row-key="getRowKey"
          class="data-table table-entrance"
          stripe
          v-loading="loadingPreview"
          :height="520"
          :empty-text="orderedRows.length === 0 ? '暂无数据' : '没有符合筛选条件的数据'"
        >
          <!-- CONTENT ID Column -->
          <el-table-column label="CONTENT ID" width="150" sortable :sort-by="(row) => row.content_id || row.note_id || row.aweme_id || row.video_id || ''">
            <template #default="{ row }">
              <span class="content-id mono" :title="getContentId(row)">
                {{ truncateContentId(getContentId(row)) }}
              </span>
            </template>
          </el-table-column>

          <!-- CREATE TIME Column -->
          <el-table-column label="CREATE TIME" prop="create_time" sortable :sort-by="(row) => row.create_time || row.created_time || 0">
            <template #default="{ row }">
              <span class="mono">{{ formatTimestamp(row.create_time || row.created_time) }}</span>
            </template>
          </el-table-column>

          <!-- IP LOCATION Column -->
          <el-table-column label="IP LOCATION" prop="ip_location" sortable :sort-by="(row) => row.ip_location || ''">
            <template #default="{ row }">
              <span>{{ row.ip_location || '-' }}</span>
            </template>
          </el-table-column>

          <!-- CONTENT Column -->
          <el-table-column label="CONTENT" min-width="200">
            <template #default="{ row, $index }">
              <div
                class="cell-content"
                :class="{ expanded: isCellExpanded(row, 'CONTENT'), expandable: isExpandable(row.content) }"
                :title="!isCellExpanded(row, 'CONTENT') && isExpandable(row.content) ? row.content : ''"
                @click="isExpandable(row.content) && toggleCell(row, 'CONTENT')"
              >
                {{ formatValue(row.content) }}
              </div>
            </template>
          </el-table-column>

          <!-- SENSITIVE Column -->
          <el-table-column label="SENSITIVE" width="120" align="center" sortable>
            <template #default="{ row }">
              <span class="sensitive-flag" :class="getSensitiveFlagClass(row)">
                {{ getSensitiveLabel(row) }}
              </span>
            </template>
          </el-table-column>

          <!-- INTERACTIONS Column -->
          <el-table-column label="INTERACTIONS" width="140" align="center" sortable :sort-method="interactionsSortMethod">
            <template #default="{ row }">
              <span class="interactions-count" :class="{ high: isHighInteractions(row) }">
                {{ formatInteractions(getInteractions(row)) }}
              </span>
            </template>
          </el-table-column>

          <!-- LINK Column -->
          <el-table-column label="LINK" width="100" align="center">
            <template #default="{ row }">
              <a
                v-if="getLink(row)"
                :href="getLink(row)"
                target="_blank"
                class="link-btn"
                title="查看原文"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
              </a>
              <span v-else class="no-link">-</span>
            </template>
          </el-table-column>

          <!-- NICKNAME Column -->
          <el-table-column label="NICKNAME" prop="nickname" sortable :sort-by="(row) => row.nickname || row.author || ''">
            <template #default="{ row }">
              <span>{{ row.nickname || row.author || '-' }}</span>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="orderedRows.length > 0" class="pagination-wrapper centered">
          <div class="pagination-controls">
            <button
              class="pagination-btn icon-btn"
              :disabled="currentPage === 1"
              @click="goToPage(currentPage - 1)"
              title="上一页"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>
            <select
              class="page-size-select"
              :value="pageSize"
              @change="setPageSize(Number($event.target.value))"
            >
              <option :value="20">20条/页</option>
              <option :value="50">50条/页</option>
              <option :value="100">100条/页</option>
            </select>
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
              class="pagination-btn icon-btn"
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
              title="下一页"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
          </div>
        </div>
        <div v-else-if="loadingPreview" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>
        <div v-else class="empty-state">
          <p>暂无数据</p>
          <p class="hint">请先选择渠道并启动爬虫</p>
        </div>
      </section>
    </div>

    <transition name="drawer">
      <div v-if="drawerVisible" class="drawer-overlay" @click.self="drawerVisible = false">
        <div class="drawer-panel">
          <div class="drawer-header">
            <span>切换渠道</span>
            <button class="drawer-close" type="button" @click="drawerVisible = false">×</button>
          </div>
          <div class="platform-drawer-list">
            <div
              v-for="platform in platformStats"
              :key="platform.value"
              class="platform-item"
              :class="{ active: platform.value === currentPlatform }"
              @click="handleSelectPlatform(platform.value)"
            >
              <div class="platform-info">
                <span class="platform-name">{{ getDisplayLabel(platform.value) || platform.label }}</span>
                <div class="platform-stats">
                  <span v-if="platform.sensitiveCount > 0" class="stat-badge sensitive">{{ platform.sensitiveCount }}</span>
                  <span class="stat-badge total">{{ platform.count }}</span>
                </div>
              </div>
              <div class="platform-progress">
                <div class="platform-progress-track">
                  <div
                    class="platform-progress-fill"
                    :class="{ 'has-sensitive': platform.sensitiveCount > 0 }"
                    :style="{ width: (platform.sensitiveCount / (platform.count || 1) * 100) + '%' }"
                  ></div>
                </div>
              </div>
              <span class="platform-icon">
                <img v-if="getPlatformLogo(platform.value)" :src="getPlatformLogo(platform.value)" :alt="getPlatformLabel(platform.value)" class="platform-logo-img small" />
                <span v-else class="status-icon">{{ getPlatformIcon(platform.value) }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <transition name="dialog">
      <div v-if="crawlerDialogVisible" class="dialog-overlay" @click.self="crawlerDialogVisible = false">
        <div class="dialog-panel">
          <div class="dialog-header">
            <span>爬虫控制</span>
            <button class="drawer-close" type="button" @click="crawlerDialogVisible = false">×</button>
          </div>
          <div class="dialog-body">
            <CrawlerControl @crawler-status-change="onCrawlerStatusChange" />
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import CrawlerControl from '../components/CrawlerControl.vue'
import { getPlatformLogo } from '../assets/platform-logos/index.js'

// State
const platforms = ref([])
const stats = ref(null)
const sentimentStats = ref({})
const route = useRoute()
const currentPlatform = ref(null)
const files = ref([])
const currentFile = ref(null)
const searchKeyword = ref('')
const sentimentFilter = ref('all') // all, positive, negative, neutral, sensitive
const sensitiveFilter = ref('all') // all, sensitive, non-sensitive
const interactionsFilter = ref('all') // all, high, medium, low
const previewData = ref(null)
const loadingPreview = ref(false)
const drawerVisible = ref(false)
const crawlerDialogVisible = ref(false)
const pageSize = ref(50)
const currentPage = ref(1)
const expandedCells = ref(new Set())
const activeTab = ref('sensitive')

const columnDefs = [
  { label: 'AVATAR', keys: ['avatar', 'avatar_url', 'avatarUrl', 'head_url', 'head', 'AVATAR'], type: 'avatar', align: 'center' },
  { label: 'CREATE TIME', keys: ['create_time', 'created_time', 'createTime', 'CREATE TIME'] },
  { label: 'IP LOCATION', keys: ['ip_location', 'ipLocation', 'location', 'IP LOCATION'] },
  { label: 'CONTENT', keys: ['content', 'text', 'desc', 'note', '内容'] },
  { label: 'SENSITIVE', keys: ['is_sensitive', 'isSensitive', 'sensitive', 'sentiment', 'sentiment_label'], type: 'sensitive', align: 'center' },
  { label: 'NICKNAME', keys: ['nickname', 'nick_name', 'user_name', 'author', 'NICKNAME'] }
]
const columnWidths = ['10%', '15%', '14%', '30%', '13%', '18%']

// Computed
const platformStats = computed(() => {
  const map = stats.value?.by_platform || {}
  const sentimentMap = sentimentStats.value || {}
  return platforms.value.map(platform => {
    const sentiment = sentimentMap[platform.value] || {}
    return {
      ...platform,
      count: sentiment.total || map[platform.value] || 0,
      sensitiveCount: sentiment.sensitive || 0
    }
  })
})

const currentPlatformStats = computed(() => {
  return platformStats.value.find(item => item.value === currentPlatform.value) || {}
})

const currentPlatformSentiment = computed(() => {
  if (!currentPlatform.value) return {}
  return sentimentStats.value?.[currentPlatform.value] || {}
})

const currentTotalCount = computed(() => {
  if (currentPlatformSentiment.value.total !== undefined) {
    return currentPlatformSentiment.value.total || 0
  }
  return currentPlatformStats.value.count || 0
})

const currentSensitiveCount = computed(() => {
  return currentPlatformSentiment.value.sensitive || 0
})

const currentPlatformCount = computed(() => {
  if (!currentPlatform.value) return 0
  const map = stats.value?.by_platform || {}
  return map[currentPlatform.value] || 0
})

const orderedRows = computed(() => {
  const rows = previewData.value?.data || []

  // Apply filters
  let filtered = rows

  // Tab filter
  if (activeTab.value === 'sensitive') {
    filtered = filtered.filter(row => {
      const flag = getSensitiveFlag(row)
      return flag === true
    })
  }

  // Sentiment filter
  if (sentimentFilter.value !== 'all') {
    filtered = filtered.filter(row => {
      const sentiment = row.sentiment || row.sentiment_label || ''
      if (sentimentFilter.value === 'sensitive') {
        return sentiment === 'sensitive' || getSensitiveFlag(row) === true
      }
      return sentiment === sentimentFilter.value
    })
  }

  // Sensitive filter
  if (sensitiveFilter.value !== 'all') {
    filtered = filtered.filter(row => {
      const flag = getSensitiveFlag(row)
      if (sensitiveFilter.value === 'sensitive') {
        return flag === true
      }
      return flag !== true
    })
  }

  // Interactions filter
  if (interactionsFilter.value !== 'all') {
    filtered = filtered.filter(row => {
      const interactions = getInteractions(row)
      if (interactionsFilter.value === 'high') {
        return interactions >= 1000
      }
      if (interactionsFilter.value === 'medium') {
        return interactions >= 100 && interactions < 1000
      }
      if (interactionsFilter.value === 'low') {
        return interactions < 100
      }
      return true
    })
  }

  // Search keyword filter
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase().trim()
    filtered = filtered.filter(row => {
      // Search in content, nickname, and other text fields
      const searchableFields = [
        row.content,
        row.desc,
        row.title,
        row.nickname,
        row.author,
        row.text,
        row.note_id,
        row.aweme_id,
        row.video_id,
        row.content_id
      ]
      return searchableFields.some(field =>
        field && String(field).toLowerCase().includes(keyword)
      )
    })
  }

  return filtered
})
const totalPages = computed(() => Math.max(1, Math.ceil(orderedRows.value.length / pageSize.value)))
const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return orderedRows.value.slice(start, end)
})
const displayedPages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  const pages = [1]
  const left = Math.max(2, current - 1)
  const right = Math.min(total - 1, current + 1)
  if (left > 2) pages.push('...')
  for (let i = left; i <= right; i += 1) pages.push(i)
  if (right < total - 1) pages.push('...')
  pages.push(total)
  return pages
})

// Methods
const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp * 1000).toLocaleDateString('zh-CN')
}

const getFieldValue = (row, keys) => {
  if (!row) return null
  for (const key of keys) {
    const val = row[key]
    if (val !== undefined && val !== null && val !== '') return val
  }
  return null
}

const getPlatformIcon = (value) => {
  const icons = {
    'xhs': '📕',
    'dy': '🎵',
    'ks': '📹',
    'bili': '📺',
    'wb': '💬',
    'tieba': '📝',
    'zhihu': '❓'
  }
  return icons[value] || '📄'
}

const getPlatformLabel = (value) => {
  const platform = platforms.value.find(item => item.value === value)
  return platform ? platform.label : value
}

const getDisplayLabel = (value) => {
  const chineseNames = {
    'xhs': '小红书',
    'dy': '抖音',
    'ks': '快手',
    'bili': '哔哩哔哩',
    'wb': '微博',
    'tieba': '百度贴吧',
    'zhihu': '知乎'
  }
  return chineseNames[value] || null
}

const isBrandLogo = (value) => value === 'xhs' || value === 'dy'

const getSensitiveFlag = (row) => {
  if (!row) return null
  const direct = row.is_sensitive ?? row.isSensitive ?? row.sensitive
  if (direct !== undefined && direct !== null && direct !== '') {
    return Boolean(direct)
  }
  const sentiment = row.sentiment ?? row.sentiment_label ?? row.sentimentLabel
  if (typeof sentiment === 'string') {
    return sentiment.toLowerCase() === 'sensitive' || sentiment === '敏感'
  }
  return null
}

const getSensitiveLabel = (row) => {
  const flag = getSensitiveFlag(row)
  if (flag === true) return '敏感'
  if (flag === false) return '正常'
  return '-'
}

const getSensitiveFlagClass = (row) => {
  const flag = getSensitiveFlag(row)
  if (flag === true) return 'on'
  if (flag === false) return 'off'
  return 'unknown'
}

const formatValue = (val) => {
  if (val === null || val === undefined || val === '') return '-'
  if (typeof val === 'object') return JSON.stringify(val)
  if (String(val).startsWith('http')) return val
  return String(val)
}

// Get interactions count (likes + comments + shares)
const getInteractions = (row) => {
  const likes = parseInt(row.liked_count) || parseInt(row.like_count) || 0
  const comments = parseInt(row.comment_count) || 0
  const shares = parseInt(row.share_count) || parseInt(row.shared_count) || 0
  const collected = parseInt(row.collected_count) || 0
  return likes + comments + shares + collected
}

// Format interactions number (e.g., 1.2K, 1.5M)
const formatInteractions = (num) => {
  if (!num || num === 0) return '0'
  if (num < 1000) return String(num)
  if (num < 1000000) return (num / 1000).toFixed(1) + 'K'
  return (num / 1000000).toFixed(1) + 'M'
}

// Check if interactions are high (>= 1000)
const isHighInteractions = (row) => {
  return getInteractions(row) >= 1000
}

// Custom sort method for interactions column (numeric sort)
const interactionsSortMethod = (rowA, rowB) => {
  const interactionsA = getInteractions(rowA)
  const interactionsB = getInteractions(rowB)
  return interactionsB - interactionsA
}

// Get content ID from various possible fields
const getContentId = (row) => {
  return row.content_id || row.note_id || row.aweme_id || row.video_id || row.weibo_id || '-'
}

// Truncate content ID for display
const truncateContentId = (id) => {
  if (!id || id === '-') return '-'
  const str = String(id)
  if (str.length <= 12) return str
  return str.substring(0, 8) + '...' + str.substring(str.length - 4)
}

// Get link URL from various possible fields
const getLink = (row) => {
  return row.note_url || row.video_url || row.aweme_url || row.weibo_url || row.content_url || row.url || null
}

const handleSelectPlatform = async (platformValue) => {
  drawerVisible.value = false
  await selectPlatform(platformValue)
}

const getRowIndex = (idx) => (currentPage.value - 1) * pageSize.value + idx

const isExpandable = (val) => {
  if (val === null || val === undefined) return false
  return String(val).length > 50
}

const isCellExpanded = (row, colLabel) => {
  const key = getRowKey(row, 0)
  return expandedCells.value.has(`${key}-${colLabel}`)
}

const toggleCell = (rowOrIndex, colLabel) => {
  // Handle both row object and index for compatibility
  let key
  if (typeof rowOrIndex === 'object' && rowOrIndex !== null) {
    // It's a row object
    key = getRowKey(rowOrIndex, 0)
  } else {
    // It's an index
    key = rowOrIndex
  }
  const cellKey = `${key}-${colLabel}`
  const next = new Set(expandedCells.value)
  if (next.has(cellKey)) {
    next.delete(cellKey)
  } else {
    next.add(cellKey)
  }
  expandedCells.value = next
}

const goToPage = (page) => {
  const nextPage = Math.min(Math.max(1, page), totalPages.value)
  currentPage.value = nextPage
}

const resetFilters = () => {
  searchKeyword.value = ''
  sentimentFilter.value = 'all'
  sensitiveFilter.value = 'all'
  interactionsFilter.value = 'all'
  currentPage.value = 1
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Create a row key for tracking
const getRowKey = (row, index) => {
  return row.content_id || row.note_id || row.aweme_id || row.video_id || index
}

// Reset page when filters change
watch([searchKeyword, sentimentFilter, sensitiveFilter, interactionsFilter], () => {
  currentPage.value = 1
})

const setPageSize = (size) => {
  pageSize.value = size
  currentPage.value = 1
  expandedCells.value = new Set()
}

// API Calls
const fetchConfig = async () => {
  try {
    const res = await axios.get('/api/config/platforms')
    platforms.value = res.data.platforms
    const statsRes = await axios.get('/api/data/stats')
    stats.value = statsRes.data
    const sentimentRes = await axios.get('/api/monitor/platform-sentiment-stats')
    sentimentStats.value = sentimentRes.data || {}
  } catch (e) {
    console.error('Failed to fetch config', e)
  }
}

const selectPlatform = async (platformValue) => {
  currentPlatform.value = platformValue
  currentFile.value = null
  previewData.value = null
  currentPage.value = 1
  expandedCells.value = new Set()
  try {
    const res = await axios.get('/api/data/files', {
      params: { platform: platformValue }
    })
    files.value = res.data.files || []
    const nextFile = [...files.value].sort((a, b) => (b.modified_at || 0) - (a.modified_at || 0))[0]
    if (nextFile) {
      await selectFile(nextFile)
    }
  } catch (e) {
    console.error('Failed to fetch files', e)
  }
}

const selectFile = async (file) => {
  currentFile.value = file
  loadingPreview.value = true
  previewData.value = null
  currentPage.value = 1
  expandedCells.value = new Set()
  try {
    const res = await axios.get(`/api/data/files/${file.path}`, {
      params: { preview: true, limit: 100 }
    })
    previewData.value = res.data
  } catch (e) {
    console.error('Failed to fetch file content', e)
  } finally {
    loadingPreview.value = false
  }
}

const onCrawlerStatusChange = async (newStatus) => {
  if (currentPlatform.value) {
    await selectPlatform(currentPlatform.value)
  }
}

// Lifecycle
onMounted(async () => {
  await fetchConfig()
  const initialPlatform = route.query?.platform
  if (initialPlatform) {
    await selectPlatform(initialPlatform)
  } else if (platforms.value.length > 0) {
    await selectPlatform(platforms.value[0].value)
  }
})

watch(
  () => route.query?.platform,
  async (nextPlatform) => {
    if (nextPlatform) {
      await selectPlatform(nextPlatform)
    }
  }
)

watch(
  () => [orderedRows.value.length, pageSize.value],
  () => {
    if (currentPage.value > totalPages.value) {
      currentPage.value = totalPages.value
    }
    expandedCells.value = new Set()
  }
)

watch(
  () => activeTab.value,
  () => {
    currentPage.value = 1
    expandedCells.value = new Set()
  }
)

onUnmounted(() => {
  currentPlatform.value = null
})
</script>

<style scoped>
/* === 官方平台Logo图片样式 === */
.platform-logo-img {
  width: 40px;
  height: 40px;
  object-fit: contain;
  border-radius: 8px;
  padding: 0;
  background: transparent;
  filter: none;
  box-shadow: none;
  transition: all 0.3s ease;
}

.platform-logo-img:hover {
  transform: scale(1.05);
  background: transparent;
}

.platform-logo-img.small {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  padding: 0;
}

/* === iOS Style Base === */
.data-wrapper {
  min-height: 100vh;
  background: #050510;
  position: relative;
  overflow: hidden;
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
}

/* === Ambient Background Effects === */
.ambient-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.nebula {
  position: absolute;
  width: 80vw;
  height: 70vh;
  filter: blur(120px);
  opacity: 0.28;
  mix-blend-mode: screen;
}

.nebula.blue {
  background: radial-gradient(circle, #0066ff, transparent 75%);
  top: -10%;
  left: -5%;
}

.nebula.gold {
  background: radial-gradient(circle, #ffaa00, transparent 75%);
  bottom: -10%;
  right: -5%;
}

.breathing-line {
  position: absolute;
  height: 1px;
  background: linear-gradient(90deg, transparent, #ffaa00, transparent);
  filter: blur(1px);
  opacity: 0.3;
  animation: breathe 8s infinite ease-in-out;
}

.gold-1 { width: 100%; top: 30%; left: -50%; transform: rotate(-5deg); }
.gold-2 { width: 100%; bottom: 20%; right: -50%; transform: rotate(3deg); animation-delay: -4s; }

@keyframes breathe {
  0%, 100% { opacity: 0.1; transform: scaleX(0.8) translateY(0); }
  50% { opacity: 0.5; transform: scaleX(1.2) translateY(-20px); }
}

.scan-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: linear-gradient(to bottom, black, transparent);
  animation: gridMove 25s linear infinite;
}

@keyframes gridMove {
  from { background-position: 0 0; }
  to { background-position: 0 50px; }
}

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
  background: #00ccff;
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

.particle:nth-child(1) { left: 10%; }
.particle:nth-child(2) { left: 20%; }
.particle:nth-child(3) { left: 30%; }
.particle:nth-child(4) { left: 40%; }
.particle:nth-child(5) { left: 50%; }
.particle:nth-child(6) { left: 60%; }
.particle:nth-child(7) { left: 70%; }
.particle:nth-child(8) { left: 80%; }

/* === Layout === */
.data-view {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  gap: 12px;
  padding: 32px 40px 40px;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  position: relative;
  z-index: 3;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 204, 255, 0.2);
}

.title-area {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ios-title {
  font-size: 32px;
  letter-spacing: -0.5px;
  background: linear-gradient(180deg, #fff 40%, rgba(255, 255, 255, 0.6));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}

.ios-title .subtitle {
  font-size: 14px;
  color: #ffaa00;
  margin-left: 10px;
  font-weight: 300;
  letter-spacing: 2px;
  display: inline-block;
  margin-top: 0;
}

.crawler-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 1rem;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.crawler-btn:hover {
  border-color: rgba(255, 170, 0, 0.5);
  box-shadow: 0 0 20px rgba(255, 170, 0, 0.2);
}

.btn-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ffaa00;
  box-shadow: 0 0 8px rgba(255, 170, 0, 0.8);
}

/* === iOS Glass Card === */
.ios-glass {
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(50px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  position: relative;
  overflow: visible;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.ios-glass:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8),
              0 0 30px rgba(255, 204, 0, 0.12),
              0 0 60px rgba(255, 204, 0, 0.06);
}

/* === Entrance Animations === */
.entrance-slide-in {
  animation: slideInFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateX(-40px);
}

@keyframes slideInFade {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.entrance-scale-up {
  animation: scaleUpFade 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}

.entrance-scale-up-delay-4 {
  animation: scaleUpFade 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.6s forwards;
  opacity: 0;
  transform: scale(0.92) translateY(30px);
}

@keyframes scaleUpFade {
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* === Hero Section (Match DevicesView) === */
.border-glow {
  position: absolute;
  inset: 0;
  z-index: 0;
  border-radius: 20px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(255, 170, 0, 0.4), transparent 40%, rgba(255, 170, 0, 0.1));
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  animation: borderBreathe 6s infinite ease-in-out;
  pointer-events: none;
}

.border-glow.gold-tint {
  background: linear-gradient(135deg, rgba(255, 170, 0, 0.55), transparent 45%, rgba(255, 170, 0, 0.15));
}

@keyframes borderBreathe {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; box-shadow: inset 0 0 15px rgba(255, 170, 0, 0.2); }
}

.kpi-selector-container {
  margin: 10px 0;
  display: flex;
  justify-content: flex-start;
}

.kpi-card {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  text-align: left;
  border: none;
  width: 100%;
}

.hero-card {
  width: 480px;
}

.selector-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tap-hint {
  font-size: 11px;
  color: #ffaa00;
  opacity: 0.8;
  display: flex;
  align-items: center;
  gap: 4px;
}

.kpi-card:hover,
.kpi-card.active {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), 0 0 15px rgba(255, 170, 0, 0.2);
}

.kpi-card.active .active-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: #ffaa00;
  box-shadow: 0 0 15px #ffaa00;
}

.kpi-icon-box {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  flex-shrink: 0;
  background: rgba(255, 100, 0, 0.2);
  color: #ffaa00;
}

.kpi-icon-box.has-logo {
  background: transparent;
  box-shadow: none;
}

.kpi-icon-box.is-brand-logo {
  background: transparent;
  box-shadow: none;
}

.status-icon {
  font-size: 26px;
}

.kpi-content {
  flex: 1;
  min-width: 0;
}

.kpi-content label {
  display: block;
  font-size: 12px;
  color: #8899aa;
  margin-bottom: 6px;
  font-weight: 500;
  letter-spacing: 1px;
}

.main-value {
  font-size: 28px;
  font-weight: 900;
  color: #fff;
  margin: 4px 0;
}

.main-value.brand-xhs {
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  letter-spacing: 1px;
}

.status-mini-tags {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}

.tag {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.1);
}

.tag.total {
  color: #8899aa;
  border-color: rgba(136, 153, 170, 0.3);
  background: rgba(136, 153, 170, 0.1);
}

.tag.sensitive {
  color: #ffb547;
  border-color: rgba(255, 170, 0, 0.35);
  background: rgba(255, 170, 0, 0.15);
  box-shadow: 0 0 10px rgba(255, 170, 0, 0.2);
}

/* === Data Table Section === */
.data-table-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 20px;
  padding-bottom: 1.25rem;
}

.table-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.75);
}

.table-columns {
  display: grid;
  padding: 0.5rem 0.8rem;
  margin: 0 1.5rem;
  margin-bottom: -4px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px 8px 0 0;
  border-bottom: none;
  backdrop-filter: blur(10px);
}

.table-header-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 0;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
  padding: 4px 8px;
  border-radius: 4px;
  color: #8da0b7;
  font-size: 0.8rem;
  font-weight: 500;
}

.table-header-cell:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #a0b5cc;
}

.table-header-cell:active {
  transform: scale(0.98);
}

.column-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sort-icon {
  flex-shrink: 0;
  opacity: 0.4;
  font-size: 0.7rem;
  transition: all 0.2s ease;
}

.sort-icon.active {
  opacity: 1;
  color: #8da0b7;
}

.table-columns span {
  min-width: 0;
}

.cell-center {
  text-align: center;
}

.sensitive-cell {
  display: flex;
  justify-content: center;
}

.sensitive-flag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.72rem;
  letter-spacing: 0.5px;
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.sensitive-flag.on {
  color: #ffb547;
  border-color: rgba(255, 170, 0, 0.35);
  background: rgba(255, 170, 0, 0.15);
  box-shadow: 0 0 10px rgba(255, 170, 0, 0.2);
}

.sensitive-flag.off {
  color: #7ee787;
  border-color: rgba(0, 255, 136, 0.3);
  background: rgba(0, 255, 136, 0.1);
}

.sensitive-flag.unknown {
  color: rgba(255, 255, 255, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
}

.accent-bar {
  width: 4px;
  height: 18px;
  border-radius: 999px;
  background: linear-gradient(180deg, #ffaa00, #ff6a00);
}

.header-meta {
  margin-left: auto;
  display: flex;
  gap: 12px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}

.table-wrapper {
  flex: 1;
  overflow: auto;
  padding: 0.6rem 1.5rem 1.5rem;
  max-height: 760px;
}

.table-wrapper::-webkit-scrollbar {
  width: 6px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 3px;
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: rgba(0, 204, 255, 0.3);
  border-radius: 3px;
  transition: all 0.3s;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 204, 255, 0.5);
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 6px;
  table-layout: fixed;
  font-size: 0.85rem;
}

th, td {
  padding: 0.85rem 0.6rem;
  text-align: left;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

td.expanded {
  max-width: none;
}

.cell-content {
  line-height: 1.4;
}

.cell-content.expandable {
  cursor: pointer;
}

.cell-content.expanded {
  white-space: normal;
  overflow: visible;
  text-overflow: clip;
  word-break: break-word;
}

thead th {
  position: sticky;
  top: 0;
  z-index: 2;
  background: rgba(6, 10, 18, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 204, 255, 0.2);
  color: rgba(255, 255, 255, 0.75);
}

tbody tr td {
  background: rgba(0, 204, 255, 0.03);
  border-top: 1px solid rgba(0, 204, 255, 0.1);
  border-bottom: 1px solid rgba(0, 204, 255, 0.1);
}

tbody tr td:first-child {
  border-left: 1px solid rgba(0, 204, 255, 0.1);
  border-top-left-radius: 12px;
  border-bottom-left-radius: 12px;
}

tbody tr td:last-child {
  border-right: 1px solid rgba(0, 204, 255, 0.1);
  border-top-right-radius: 12px;
  border-bottom-right-radius: 12px;
}

tbody tr:hover td {
  background: rgba(0, 204, 255, 0.08);
  border-color: rgba(0, 204, 255, 0.25);
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.15);
}

.visually-hidden {
  border: 0;
  clip: rect(0 0 0 0);
  height: 1px;
  margin: -1px;
  overflow: hidden;
  padding: 0;
  position: absolute;
  width: 1px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(0, 204, 255, 0.2);
  flex-wrap: wrap;
  position: relative;
  z-index: 2;
  margin-bottom: 0.5rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.pagination-btn.icon-btn {
  width: 36px;
  height: 36px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  border: 1px solid rgba(0, 204, 255, 0.2);
  background: rgba(0, 204, 255, 0.08);
  color: #00ccff;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.pagination-btn.icon-btn svg {
  width: 18px;
  height: 18px;
}

.pagination-btn.icon-btn:hover:not(:disabled) {
  background: rgba(0, 204, 255, 0.2);
  border-color: rgba(0, 204, 255, 0.5);
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.3);
  transform: translateY(-1px);
}

.pagination-btn.icon-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-size-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  padding: 0.4rem 2rem 0.4rem 0.7rem;
  border-radius: 8px;
  border: 1px solid rgba(0, 204, 255, 0.2);
  background: rgba(0, 204, 255, 0.08) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2300ccff' stroke-width='3'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") no-repeat right 8px center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  min-width: 90px;
}

.page-size-select:hover {
  background-color: rgba(0, 204, 255, 0.12);
  border-color: rgba(0, 204, 255, 0.5);
}

.page-size-select:focus {
  outline: none;
  border-color: rgba(0, 204, 255, 0.5);
  box-shadow: 0 0 10px rgba(0, 204, 255, 0.3);
}

.page-size-select option {
  background: rgba(10, 10, 15, 0.98);
  color: rgba(255, 255, 255, 0.85);
  padding: 0.4rem 0.7rem;
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
  border: 1px solid rgba(0, 204, 255, 0.2);
  background: rgba(0, 204, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
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
  border-color: rgba(0, 204, 255, 0.5);
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.3);
  transform: translateY(-1px);
}

.pagination-number.active {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.4), rgba(0, 204, 255, 0.25));
  border-color: rgba(0, 204, 255, 0.5);
  color: #fff;
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.4);
}

.pagination-number.ellipsis {
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.4);
  cursor: default;
}

.pagination-number:disabled {
  cursor: not-allowed;
}

th {
  background: rgba(0, 0, 0, 0.4);
  position: sticky;
  top: 0;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
  letter-spacing: 1px;
}

td {
  color: rgba(255, 255, 255, 0.7);
}

tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.avatar-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar-cell img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* === Drawer === */
.platform-drawer-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.platform-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
}

.platform-item.active {
  border-color: rgba(255, 170, 0, 0.4);
  box-shadow: 0 0 12px rgba(255, 170, 0, 0.2);
}

.platform-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.platform-name {
  font-size: 0.95rem;
  font-weight: 600;
}

.platform-stats {
  display: flex;
  gap: 6px;
  align-items: center;
}

.stat-badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.stat-badge.sensitive {
  background: rgba(255, 60, 60, 0.2);
  color: #ff6b6b;
  border: 1px solid rgba(255, 60, 60, 0.3);
}

.stat-badge.total {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
}

.platform-progress {
  width: 60px;
  flex-shrink: 0;
}

.platform-progress-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.platform-progress-fill {
  height: 100%;
  background: rgba(255, 170, 0, 0.5);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.platform-progress-fill.has-sensitive {
  background: #ff6b6b;
  box-shadow: 0 0 6px rgba(255, 107, 107, 0.5);
}

.platform-icon {
  font-size: 1.4rem;
  flex-shrink: 0;
}

/* === Drawer + Dialog === */
.drawer-overlay,
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(3, 5, 8, 0.65);
  backdrop-filter: blur(6px);
  z-index: 3000;
  display: flex;
  justify-content: flex-end;
}

.drawer-panel {
  width: min(420px, 90vw);
  height: 100%;
  background: rgba(10, 12, 18, 0.96);
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.dialog-overlay {
  justify-content: center;
  align-items: center;
}

.dialog-panel {
  width: min(520px, 92vw);
  background: rgba(10, 12, 18, 0.98);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 18px 20px 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

/* === Drawer Transition === */
.drawer-enter-active {
  transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-enter-active .drawer-panel {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-leave-active {
  transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-leave-active .drawer-panel {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .drawer-panel,
.drawer-leave-to .drawer-panel {
  transform: translateX(100%);
}

/* === Dialog Transition === */
.dialog-enter-active {
  transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.dialog-enter-active .dialog-panel {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.dialog-leave-active {
  transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.dialog-leave-active .dialog-panel {
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-from .dialog-panel,
.dialog-leave-to .dialog-panel {
  transform: scale(0.95);
  opacity: 0;
}

.dialog-body {
  margin-top: 12px;
}

.drawer-header,
.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.85);
}

.drawer-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.drawer-close:hover {
  background: rgba(255, 170, 0, 0.2);
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

/* === States === */
.welcome-state, .empty-state, .loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: rgba(255, 255, 255, 0.6);
  padding: 40px;
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffaa00;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* === Custom Tab Styles === */
.custom-tabs {
  display: flex;
  gap: 4px;
  padding: 0 25px;
  margin-bottom: 12px;
}

.tab-item {
  position: relative;
  padding: 10px 20px;
  font-size: 0.9rem;
  font-weight: 500;
  color: #8899aa;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  letter-spacing: 0.5px;
}

.tab-item:hover {
  color: #aabbcc;
}

.tab-item.active {
  color: #ffaa00;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: #ffaa00;
  box-shadow: 0 0 10px rgba(255, 170, 0, 0.5);
}

/* === Filter Bar === */
.filter-bar {
  padding: 12px 25px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
}

.filter-search {
  position: relative;
  flex: 1;
  min-width: 200px;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #8899aa;
  pointer-events: none;
  stroke-width: 2;
}

.filter-input {
  width: 100%;
  padding: 8px 36px 8px 36px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  font-size: 0.85rem;
  outline: none;
  transition: all 0.2s ease;
}

.filter-input::placeholder {
  color: #667788;
}

.filter-input:hover {
  border-color: rgba(255, 170, 0, 0.3);
}

.filter-input:focus {
  border-color: #ffaa00;
  background: rgba(255, 255, 255, 0.06);
}

.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #8899aa;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.filter-select {
  padding: 8px 12px;
  padding-right: 30px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  font-size: 0.85rem;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%238899aa' d='M2 4l4 4 4-4z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 32px;
}

.filter-select:hover {
  border-color: rgba(255, 170, 0, 0.3);
}

.filter-select:focus {
  border-color: #ffaa00;
}

.filter-select option {
  background: #1a1d26;
  color: #fff;
}

.filter-reset {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #8899aa;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-reset:hover {
  background: rgba(255, 170, 0, 0.1);
  border-color: rgba(255, 170, 0, 0.3);
  color: #ffaa00;
}

.filter-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.result-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.filter-active {
  font-size: 0.75rem;
  padding: 2px 8px;
  background: rgba(255, 170, 0, 0.15);
  color: #ffaa00;
  border-radius: 10px;
}

/* === Element Plus Table Styles - Transparent === */
.data-table-section :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-row-hover-bg-color: transparent;
  --el-table-header-bg-color: transparent;
  --el-table-border-color: rgba(0, 204, 255, 0.1);
  background: transparent !important;
  color: rgba(255, 255, 255, 0.7);
}

.data-table-section :deep(.el-table__inner-wrapper) {
  background: transparent !important;
}

.data-table-section :deep(.el-table__header-wrapper) {
  background: transparent !important;
}

.data-table-section :deep(.el-table__header th) {
  background: rgba(0, 204, 255, 0.05) !important;
  border-color: rgba(0, 204, 255, 0.1) !important;
  color: rgba(255, 255, 255, 0.7) !important;
  font-size: 12px;
  letter-spacing: 1px;
  font-weight: 600;
  white-space: nowrap;
  user-select: none;
}

.data-table-section :deep(.el-table__header th .cell) {
  white-space: nowrap;
  padding: 0 8px;
  overflow: visible !important;
  text-overflow: clip !important;
}

/* 排序列表头保持统一颜色 */
.data-table-section :deep(.el-table__header th.is-sortable),
.data-table-section :deep(.el-table__header th.is-sortable .cell) {
  color: rgba(255, 255, 255, 0.7) !important;
  cursor: pointer !important;
  background: rgba(0, 204, 255, 0.05) !important;
}

/* 永久禁用表头排序激活色 */
.data-table-section :deep(.el-table__header th:hover .cell),
.data-table-section :deep(.el-table__header th.is-sortable:hover),
.data-table-section :deep(.el-table__header th.is-sortable:hover .cell),
.data-table-section :deep(.el-table__header th.ascending),
.data-table-section :deep(.el-table__header th.ascending .cell),
.data-table-section :deep(.el-table__header th.descending),
.data-table-section :deep(.el-table__header th.descending .cell),
.data-table-section :deep(.el-table__header th.is-sortable .cell:hover) {
  color: rgba(255, 255, 255, 0.7) !important;
  background: rgba(0, 204, 255, 0.05) !important;
}

/* 排序图标颜色 */
.data-table-section :deep(.el-table__header th .caret-wrapper .sort-caret.ascending),
.data-table-section :deep(.el-table__header th .caret-wrapper .sort-caret.descending) {
  color: rgba(255, 255, 255, 0.4) !important;
  border-top-color: rgba(255, 255, 255, 0.4) !important;
  border-bottom-color: rgba(255, 255, 255, 0.4) !important;
  opacity: 0.6;
}

.data-table-section :deep(.el-table__header th .caret-wrapper),
.data-table-section :deep(.el-table__header th .caret-wrapper .sort-caret) {
  cursor: pointer !important;
}

/* 简约菱形排序按钮 */
.data-table-section :deep(.el-table__header th .caret-wrapper) {
  width: 10px;
  height: 12px;
  margin-left: 6px;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.data-table-section :deep(.el-table__header th .caret-wrapper::before),
.data-table-section :deep(.el-table__header th .caret-wrapper::after) {
  content: '';
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  opacity: 0.35;
  transition: opacity 0.15s ease, border-color 0.15s ease;
}

.data-table-section :deep(.el-table__header th .caret-wrapper::before) {
  border-bottom: 5px solid rgba(255, 255, 255, 0.4);
}

.data-table-section :deep(.el-table__header th .caret-wrapper::after) {
  border-top: 5px solid rgba(255, 255, 255, 0.4);
}

.data-table-section :deep(.el-table__header th.ascending .caret-wrapper::before) {
  opacity: 0.9;
  border-bottom-color: rgba(255, 255, 255, 0.7);
}

.data-table-section :deep(.el-table__header th.ascending .caret-wrapper::after) {
  opacity: 0.2;
  border-top-color: rgba(255, 255, 255, 0.4);
}

.data-table-section :deep(.el-table__header th.descending .caret-wrapper::after) {
  opacity: 0.9;
  border-top-color: rgba(255, 255, 255, 0.7);
}

.data-table-section :deep(.el-table__header th.descending .caret-wrapper::before) {
  opacity: 0.2;
  border-bottom-color: rgba(255, 255, 255, 0.4);
}

.data-table-section :deep(.el-table__header th .caret-wrapper .sort-caret) {
  display: none;
}

.data-table-section :deep(.el-table__body-wrapper) {
  background: transparent !important;
}

.data-table-section :deep(.el-table__body tr) {
  background: transparent !important;
}

.data-table-section :deep(.el-table__body tr.el-table__row--striped) {
  background: transparent !important;
}

.data-table-section :deep(.el-table__body td) {
  border-top: 1px solid rgba(0, 204, 255, 0.1) !important;
  border-bottom: 1px solid rgba(0, 204, 255, 0.1) !important;
  background: rgba(0, 204, 255, 0.03) !important;
  color: rgba(255, 255, 255, 0.7) !important;
}

.data-table-section :deep(.el-table__body tr td:first-child) {
  border-left: 1px solid rgba(0, 204, 255, 0.1) !important;
  border-top-left-radius: 12px !important;
  border-bottom-left-radius: 12px !important;
}

.data-table-section :deep(.el-table__body tr td:last-child) {
  border-right: 1px solid rgba(0, 204, 255, 0.1) !important;
  border-top-right-radius: 12px !important;
  border-bottom-right-radius: 12px !important;
}

.data-table-section :deep(.el-table__row:hover td) {
  background: rgba(0, 204, 255, 0.08) !important;
  border-color: rgba(0, 204, 255, 0.25) !important;
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.15) !important;
}

/* 固定列样式 */
.data-table-section :deep(.el-table-fixed-column--right) {
  background: transparent !important;
}

.data-table-section :deep(.el-table-fixed--right .el-table__fixed-body-wrapper) {
  background: transparent !important;
}

/* 限制表格固定列的高度 */
.data-table-section :deep(.el-table__fixed) {
  height: 520px !important;
  background: transparent !important;
}

.data-table-section :deep(.el-table__fixed-right) {
  height: 520px !important;
  background: transparent !important;
}

.data-table-section :deep(.el-table__fixed-right-patch) {
  height: 520px !important;
  background: transparent !important;
}

/* 单体字字体 */
.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  letter-spacing: 0.1px;
}

/* Cell Content Expandable Styles */
.data-table-section :deep(.cell-content) {
  line-height: 1.5;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.data-table-section :deep(.cell-content.expandable) {
  cursor: pointer;
  transition: all 0.2s ease;
}

.data-table-section :deep(.cell-content.expandable:hover) {
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 0 8px rgba(0, 204, 255, 0.3);
}

.data-table-section :deep(.cell-content.expanded) {
  max-width: none;
  white-space: normal;
  overflow: visible;
  text-overflow: clip;
  word-break: break-word;
  line-height: 1.6;
}

/* 表格入场动画 */
.table-entrance {
  animation: tableFadeIn 0.4s ease-out;
}

@keyframes tableFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Interactions Count Styles */
.data-table-section :deep(.interactions-count) {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.2s ease;
}

.data-table-section :deep(.interactions-count.high) {
  color: #ffaa00;
  text-shadow: 0 0 8px rgba(255, 170, 0, 0.3);
}

/* Content ID Styles */
.data-table-section :deep(.content-id) {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 0.5px;
}

/* Link Button Styles */
.data-table-section :deep(.link-btn) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  color: #00ccff;
  background: rgba(0, 204, 255, 0.08);
  border: 1px solid rgba(0, 204, 255, 0.2);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  text-decoration: none;
}

.data-table-section :deep(.link-btn:hover) {
  background: rgba(0, 204, 255, 0.2);
  border-color: rgba(0, 204, 255, 0.5);
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.3);
  transform: translateY(-2px);
}

.data-table-section :deep(.link-btn svg) {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

.data-table-section :deep(.no-link) {
  color: rgba(255, 255, 255, 0.3);
}

@media (max-width: 960px) {
  .data-view {
    padding: 24px;
  }

  .hero-card {
    width: 100%;
  }

  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-search {
    max-width: none;
  }

  .filter-item {
    width: 100%;
  }

  .filter-select,
  .filter-reset {
    width: 100%;
  }

  .header-meta {
    display: none;
  }
}
</style>
