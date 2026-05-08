<template>
  <div class="data-wrapper">
    <AmbientBackground />

    <div class="data-view">
      <header class="page-header entrance-slide-in">
        <div class="title-area">
          <h1 class="ios-title">数据源概览<span class="subtitle">DATA SOURCE</span></h1>
        </div>
        <div class="header-actions">
          <button
            class="crawler-btn"
            type="button"
            @click="crawlerDialogVisible = true"
            :disabled="crawlerStatus === 'running'"
            :class="{ 'is-updating': crawlerStatus === 'running' }"
          >
            <span class="btn-dot"></span>
            <span class="btn-text">{{ crawlerStatus === 'running' ? '更新中...' : '更新' }}</span>
          </button>
          <button
            class="refresh-btn icon-only"
            type="button"
            @click="refreshCurrentPlatform"
            :disabled="loadingPreview"
            :class="{ 'is-refreshing': refreshInFlight }"
            title="同步刷新"
            aria-label="同步刷新"
          >
            <svg class="refresh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 12a8 8 0 0 1 13.66-5.66"/>
              <polyline points="16 3 16 7 12 7"/>
              <path d="M21 12a8 8 0 0 1-13.66 5.66"/>
              <polyline points="8 21 8 17 12 17"/>
            </svg>
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
              <span v-if="currentUpdatedAt" class="update-time">更新于 {{ currentUpdatedAt }}</span>
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

            <!-- Sensitive Filter -->
            <div class="filter-item">
              <el-select v-model="sensitiveFilter" class="dark-select filter-select-item" :teleported="false">
                <el-option label="全部状态" value="all" />
                <el-option label="仅敏感" value="sensitive" />
                <el-option label="非敏感" value="non-sensitive" />
              </el-select>
            </div>

            <!-- Interactions Filter -->
            <div class="filter-item">
              <el-select v-model="interactionsFilter" class="dark-select filter-select-item" :teleported="false">
                <el-option label="全部互动" value="all" />
                <el-option label="高互动 (1000+)" value="high" />
                <el-option label="中互动 (100-999)" value="medium" />
                <el-option label="低互动 (<100)" value="low" />
              </el-select>
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
          <div class="filter-info"></div>
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
          @sort-change="handleSortChange"
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
          <el-table-column label="SENSITIVE" prop="sensitive" width="120" align="center" sortable :sort-by="getSensitiveSortValue">
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
                <div class="platform-updated">
                  更新于 {{ getPlatformUpdatedAt(platform.value) || '-' }}
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
            <span>更新</span>
            <button class="drawer-close" type="button" @click="crawlerDialogVisible = false">×</button>
          </div>
          <div class="dialog-body">
            <CrawlerControl
              :current-platform="currentPlatform"
              @crawler-status-change="onCrawlerStatusChange"
              @platform-change="handleCrawlerPlatformChange"
            />
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
import AmbientBackground from '../components/AmbientBackground.vue'
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
const sensitiveFilter = ref('sensitive') // all, sensitive, non-sensitive
const interactionsFilter = ref('all') // all, high, medium, low
const previewData = ref(null)
const loadingPreview = ref(false)
const drawerVisible = ref(false)
const crawlerDialogVisible = ref(false)
const crawlerStatus = ref('idle')
const crawlerStatusPollingTimer = ref(null)
const refreshTimer = ref(null)
const refreshInFlight = ref(false)
const lastStatsRefresh = ref(0)
const platformUpdatedAt = ref({})
const pageSize = ref(50)
const currentPage = ref(1)
const expandedCells = ref(new Set())
const activeTab = ref('sensitive')
const sensitivePreviewSize = 1000
const sortState = ref({ prop: '', order: '' })

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

const currentUpdatedAt = computed(() => {
  if (!currentPlatform.value) return ''
  return platformUpdatedAt.value[currentPlatform.value] || ''
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
const hasActiveFilters = computed(() => {
  return Boolean(
    searchKeyword.value.trim() ||
    sentimentFilter.value !== 'all' ||
    sensitiveFilter.value !== 'all' ||
    interactionsFilter.value !== 'all'
  )
})

const isSensitiveOnlyFilter = computed(() => {
  return (
    activeTab.value === 'all' &&
    sensitiveFilter.value === 'sensitive' &&
    sentimentFilter.value === 'all' &&
    interactionsFilter.value === 'all' &&
    !searchKeyword.value.trim()
  )
})

const useServerPagination = computed(() => {
  const hasTotal = previewData.value && typeof previewData.value.total === 'number'
  if (!hasTotal) return false
  if (activeTab.value === 'sensitive' || isSensitiveOnlyFilter.value) return true
  if (hasActiveFilters.value) return false
  return true
})

const totalCount = computed(() => {
  if (useServerPagination.value && previewData.value) {
    return previewData.value.total || 0
  }
  return orderedRows.value.length
})

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))
const pagedRows = computed(() => {
  if (useServerPagination.value) {
    return orderedRows.value
  }
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

const getPlatformUpdatedAt = (value) => {
  return platformUpdatedAt.value[value] || ''
}

const isBrandLogo = (value) => value === 'xhs' || value === 'dy'

const getSensitiveFlag = (row) => {
  if (!row) return null
  const direct = row.is_sensitive ?? row.isSensitive
  const sentiment = row.sentiment ?? row.sentiment_label ?? row.sentimentLabel
    ?? (typeof row.sensitive === 'string' ? row.sensitive : undefined)
  if (direct !== undefined && direct !== null && direct !== '') {
    if (direct === true || direct === 1 || direct === '1') {
      return true
    }
    if (typeof sentiment === 'string') {
      return sentiment.toLowerCase() === 'sensitive' || sentiment === '敏感'
    }
    return false
  }
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

const getSensitiveSortValue = (row) => {
  const flag = getSensitiveFlag(row)
  if (flag === true) return 0
  if (flag === false) return 1
  return 2
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

const handleCrawlerPlatformChange = async (platformValue) => {
  if (!platformValue || platformValue === currentPlatform.value) return
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
    const updatedMap = statsRes.data?.updated_at_by_platform || {}
    const nextUpdated = {}
    Object.keys(updatedMap).forEach((platform) => {
      const ts = updatedMap[platform]
      if (ts) {
        nextUpdated[platform] = formatFetchedAt(ts)
      }
    })
    platformUpdatedAt.value = {
      ...platformUpdatedAt.value,
      ...nextUpdated
    }
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
  if (activeTab.value === 'sensitive' || isSensitiveOnlyFilter.value) {
    await fetchSensitivePreview(platformValue, 1, pageSize.value)
    return
  }
  await fetchAllFeedData(platformValue, 1, pageSize.value)
}

const selectFile = async (file, options = {}) => {
  const { page = 1, limit = 100, keepPage = false } = options
  currentFile.value = file
  loadingPreview.value = true
  previewData.value = null
  if (!keepPage) {
    currentPage.value = 1
  }
  expandedCells.value = new Set()
  try {
    const res = await axios.get(`/api/data/files/${file.path}`, {
      params: { preview: true, limit, page }
    })
    previewData.value = res.data
  } catch (e) {
    console.error('Failed to fetch file content', e)
  } finally {
    loadingPreview.value = false
  }
}

const formatFetchedAt = (timestampMs) => {
  if (!timestampMs) return ''
  const date = new Date(timestampMs)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const fetchAllFeedData = async (platformValue, page = 1, pageSize = 50, keepPage = false) => {
  if (!platformValue) return
  loadingPreview.value = true
  previewData.value = null
  if (!keepPage) {
    currentPage.value = 1
  }
  expandedCells.value = new Set()
  try {
    const params = { platform: platformValue, page, page_size: pageSize }
    if (sortState.value.prop === 'sensitive' && sortState.value.order) {
      params.sort_by = 'sensitive'
      params.sort_order = sortState.value.order === 'ascending' ? 'asc' : 'desc'
    }
    const res = await axios.get('/api/monitor/feed/all', {
      params
    })
    const items = res.data.items || []
    previewData.value = {
      data: items.map(item => ({
        content_id: item.content_id,
        note_id: item.content_id,
        create_time: item.created_at,
        created_time: item.created_at,
        content: item.content,
        nickname: item.author,
        author: item.author,
        url: item.url,
        sentiment: item.sentiment,
        is_sensitive: item.is_sensitive,
        ip_location: item.ip_location,
        liked_count: item.liked_count,
        comment_count: item.comment_count,
        share_count: item.share_count,
        collected_count: item.collected_count
      })),
      total: res.data.pagination?.total_count || items.length
    }
    const updateTs = res.data.latest_update_ts || res.data.fetched_at
    if (updateTs) {
      platformUpdatedAt.value = {
        ...platformUpdatedAt.value,
        [platformValue]: formatFetchedAt(updateTs)
      }
    }
  } catch (e) {
    console.error('Failed to fetch all feed data', e)
  } finally {
    loadingPreview.value = false
  }
}

const fetchSensitivePreview = async (platformValue, page = 1, pageSize = sensitivePreviewSize, keepPage = false) => {
  if (!platformValue) return
  loadingPreview.value = true
  previewData.value = null
  if (!keepPage) {
    currentPage.value = 1
  }
  expandedCells.value = new Set()
  try {
    const params = { platform: platformValue, page, page_size: pageSize }
    if (sortState.value.prop === 'sensitive' && sortState.value.order) {
      params.sort_by = 'sensitive'
      params.sort_order = sortState.value.order === 'ascending' ? 'asc' : 'desc'
    }
    const res = await axios.get('/api/monitor/feed/sensitive', {
      params
    })
    const items = res.data.items || []
    previewData.value = {
      data: items.map(item => ({
        content_id: item.content_id,
        note_id: item.content_id,
        create_time: item.created_at,
        created_time: item.created_at,
        content: item.content,
        nickname: item.author,
        author: item.author,
        url: item.url,
        sentiment: item.sentiment,
        is_sensitive: item.is_sensitive,
        ip_location: item.ip_location,
        liked_count: item.liked_count,
        comment_count: item.comment_count,
        share_count: item.share_count,
        collected_count: item.collected_count
      })),
      total: res.data.pagination?.total_count || items.length
    }
    const updateTs = res.data.latest_update_ts || res.data.fetched_at
    if (updateTs) {
      platformUpdatedAt.value = {
        ...platformUpdatedAt.value,
        [platformValue]: formatFetchedAt(updateTs)
      }
    }
  } catch (e) {
    console.error('Failed to fetch sensitive feed', e)
  } finally {
    loadingPreview.value = false
  }
}

const refreshCurrentPlatform = async ({ refreshStats = false } = {}) => {
  if (loadingPreview.value || refreshInFlight.value) return
  refreshInFlight.value = true
  try {
    const now = Date.now()
    const shouldRefreshStats = refreshStats || now - lastStatsRefresh.value > 30000
    if (shouldRefreshStats) {
      await fetchConfig()
      lastStatsRefresh.value = now
    }
    if (currentPlatform.value) {
      if (activeTab.value === 'sensitive' || isSensitiveOnlyFilter.value) {
        await fetchSensitivePreview(currentPlatform.value, currentPage.value, pageSize.value, true)
      } else {
        // 所有数据列表也从MonitorFeed加载
        await fetchAllFeedData(currentPlatform.value, currentPage.value, pageSize.value, true)
      }
    }
  } finally {
    refreshInFlight.value = false
  }
}

const fetchCrawlerStatus = async ({ refreshOnIdle = false } = {}) => {
  try {
    const res = await axios.get('/api/crawler/status')
    const nextStatus = res.data.status
    const previousStatus = crawlerStatus.value

    crawlerStatus.value = nextStatus

    if (nextStatus === 'running' && !crawlerStatusPollingTimer.value) {
      startCrawlerStatusPolling()
    } else if (crawlerStatusPollingTimer.value) {
      clearInterval(crawlerStatusPollingTimer.value)
      crawlerStatusPollingTimer.value = null
    }

    if (refreshOnIdle && previousStatus !== 'idle' && nextStatus === 'idle') {
      await refreshCurrentPlatform({ refreshStats: true })
    }
  } catch (e) {
    console.error('获取爬虫状态失败:', e)
  }
}

const onCrawlerStatusChange = async (newStatus) => {
  crawlerStatus.value = newStatus
  await refreshCurrentPlatform({ refreshStats: true })

  // 如果爬虫正在运行，启动状态轮询确保及时更新
  if (newStatus === 'running' && !crawlerStatusPollingTimer.value) {
    startCrawlerStatusPolling()
  }
}

// 启动爬虫状态轮询
const startCrawlerStatusPolling = () => {
  // 清除现有轮询
  if (crawlerStatusPollingTimer.value) {
    clearInterval(crawlerStatusPollingTimer.value)
  }
  // 每2秒检查一次状态
  crawlerStatusPollingTimer.value = setInterval(async () => {
    await fetchCrawlerStatus({ refreshOnIdle: true })
  }, 2000)
}

const handleSortChange = ({ prop, order }) => {
  if (prop !== 'sensitive') return
  sortState.value = { prop, order: order || '' }
  refreshCurrentPlatform()
}

const fetchPageData = async () => {
  if (!useServerPagination.value) return
  if (activeTab.value === 'sensitive' || isSensitiveOnlyFilter.value) {
    await fetchSensitivePreview(currentPlatform.value, currentPage.value, pageSize.value, true)
  } else {
    // 所有数据列表使用服务端分页
    await fetchAllFeedData(currentPlatform.value, currentPage.value, pageSize.value, true)
  }
}

// Lifecycle
onMounted(async () => {
  await fetchConfig()
  await fetchCrawlerStatus()
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
  () => sensitiveFilter.value,
  () => {
    if (activeTab.value === 'all') {
      refreshCurrentPlatform()
    }
  }
)

watch(
  () => [currentPage.value, pageSize.value],
  () => {
    fetchPageData()
  }
)

watch(
  () => crawlerStatus.value,
  (nextStatus) => {
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
      refreshTimer.value = null
    }
    if (nextStatus === 'idle') {
      refreshCurrentPlatform({ refreshStats: true })
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
    if (activeTab.value === 'sensitive') {
      sensitiveFilter.value = 'sensitive'
    } else if (sensitiveFilter.value === 'sensitive') {
      sensitiveFilter.value = 'all'
    }
    refreshCurrentPlatform()
  }
)

onUnmounted(() => {
  currentPlatform.value = null
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
  if (crawlerStatusPollingTimer.value) {
    clearInterval(crawlerStatusPollingTimer.value)
  }
})
</script>


<style scoped src="../styles/views/data-view.css"></style>
<style src="../styles/views/data-view-global.css"></style>
