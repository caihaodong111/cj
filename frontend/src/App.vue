<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo">
        <span class="logo-icon">🕷️</span>
        <h1>MediaCrawler 控制台</h1>
      </div>
      <div class="stats" v-if="stats">
        <span class="stat-item">
          <strong>{{ stats.total_files }}</strong> 文件
        </span>
        <span class="stat-item">
          <strong>{{ formatBytes(stats.total_size) }}</strong> 数据大小
        </span>
      </div>
    </header>

    <main class="main-content">
      <!-- 左侧：爬虫控制面板 -->
      <aside class="crawler-panel">
        <CrawlerControl @crawler-status-change="onCrawlerStatusChange" />
      </aside>

      <!-- 右侧：数据展示区域 -->
      <section class="data-panel">
        <!-- 平台选择器 -->
        <div class="platform-bar">
          <h3>数据来源</h3>
          <div class="platform-tabs">
            <div
              v-for="platform in platforms"
              :key="platform.value"
              class="platform-tab"
              :class="{ active: currentPlatform === platform.value }"
              @click="selectPlatform(platform.value)"
            >
              <span class="tab-icon">{{ getPlatformIcon(platform.value) }}</span>
              <span class="tab-label">{{ platform.label }}</span>
              <span class="tab-count" v-if="stats?.by_platform && stats.by_platform[platform.value]">
                {{ stats.by_platform[platform.value] }}
              </span>
            </div>
          </div>
        </div>

        <!-- 文件列表和数据预览 -->
        <div class="content-area" v-if="currentPlatform">
          <!-- 文件列表 -->
          <div class="files-section">
            <div class="section-header">
              <h4>{{ getPlatformLabel(currentPlatform) }} 数据文件</h4>
              <div class="file-controls">
                <input
                  type="text"
                  v-model="searchQuery"
                  placeholder="搜索文件..."
                  class="search-input"
                />
                <select v-model="fileTypeFilter" class="type-select">
                  <option value="">全部类型</option>
                  <option value="json">JSON</option>
                  <option value="csv">CSV</option>
                  <option value="xlsx">Excel</option>
                </select>
              </div>
            </div>

            <div class="files-list" v-if="filteredFiles.length > 0">
              <div
                v-for="file in filteredFiles"
                :key="file.path"
                class="file-item"
                :class="{ active: currentFile?.path === file.path }"
                @click="selectFile(file)"
              >
                <div class="file-icon">{{ getFileIcon(file.type) }}</div>
                <div class="file-info">
                  <div class="file-name" :title="file.name">{{ file.name }}</div>
                  <div class="file-meta">
                    <span>{{ formatBytes(file.size) }}</span>
                    <span>{{ formatDate(file.modified_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="loadingFiles" class="loading-state">
              <div class="loading-spinner"></div>
              <p>加载中...</p>
            </div>
            <div v-else class="empty-state">
              <p>暂无数据文件</p>
              <p class="hint">请先在左侧启动爬虫</p>
            </div>
          </div>

          <!-- 数据预览 -->
          <div class="preview-section" v-if="currentFile">
            <div class="section-header">
              <h4>{{ currentFile.name }}</h4>
              <span class="record-count" v-if="previewData?.total">
                {{ previewData.total }} 条记录
              </span>
            </div>

            <div class="table-wrapper" v-if="previewData && previewData.data && previewData.data.length > 0">
              <table>
                <thead>
                  <tr>
                    <th v-for="key in getDataKeys(previewData.data[0])" :key="key">{{ formatHeader(key) }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in previewData.data" :key="idx">
                    <td v-for="key in getDataKeys(previewData.data[0])" :key="key">
                      <div class="cell-content" :title="String(row[key])">
                        {{ formatValue(row[key]) }}
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else-if="loadingPreview" class="loading-state">
              <div class="loading-spinner"></div>
              <p>加载中...</p>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-else-if="!currentFile" class="welcome-state full">
            <div class="welcome-content">
              <span class="welcome-icon">📊</span>
              <h4>数据预览</h4>
              <p>选择一个文件查看数据内容</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import CrawlerControl from './components/CrawlerControl.vue'

// State
const platforms = ref([])
const stats = ref(null)
const currentPlatform = ref(null)
const files = ref([])
const currentFile = ref(null)
const previewData = ref(null)
const loadingFiles = ref(false)
const loadingPreview = ref(false)
const searchQuery = ref('')
const fileTypeFilter = ref('')
const crawlerStatus = ref('idle')

// Computed
const filteredFiles = computed(() => {
  return files.value.filter(file => {
    const matchesSearch = !searchQuery.value || file.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesType = !fileTypeFilter.value || file.type === fileTypeFilter.value
    return matchesSearch && matchesType
  })
})

// Methods
const formatBytes = (bytes, decimals = 2) => {
  if (!bytes) return '0 B'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

const formatDate = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleDateString('zh-CN')
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

const getFileIcon = (type) => {
  const icons = {
    'json': '📋',
    'csv': '📊',
    'xlsx': '📈',
    'xls': '📈'
  }
  return icons[type] || '📄'
}

const getPlatformLabel = (value) => {
  const p = platforms.value.find(p => p.value === value)
  return p ? p.label : value
}

const formatHeader = (key) => {
  const headerMap = {
    'id': 'ID',
    'title': '标题',
    'content': '内容',
    'author': '作者',
    'likes': '点赞数',
    'created_time': '创建时间',
    'url': '链接'
  }
  return headerMap[key] || key.replace(/_/g, ' ').toUpperCase()
}

const getDataKeys = (row) => {
  if (!row) return []
  return Object.keys(row)
}

const formatValue = (val) => {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'object') return JSON.stringify(val)
  if (String(val).startsWith('http')) return val
  return String(val).length > 50 ? String(val).substring(0, 50) + '...' : val
}

// API Calls
const fetchConfig = async () => {
  try {
    const res = await axios.get('/api/config/platforms')
    platforms.value = res.data.platforms
    const statsRes = await axios.get('/api/data/stats')
    stats.value = statsRes.data
  } catch (e) {
    console.error('Failed to fetch config', e)
  }
}

const selectPlatform = async (platformValue) => {
  currentPlatform.value = platformValue
  currentFile.value = null
  previewData.value = null
  loadingFiles.value = true
  try {
    const res = await axios.get('/api/data/files', {
      params: { platform: platformValue }
    })
    files.value = res.data.files

    console.log('[App] Files loaded:', files.value.length, 'files for', platformValue)
    console.log('[App] Files:', files.value.map(f => ({ name: f.name, type: f.type, size: f.size, modified: new Date(f.modified_at * 1000).toLocaleString('zh-CN') })))
  } catch (e) {
    console.error('Failed to fetch files', e)
  } finally {
    loadingFiles.value = false
  }
}

const selectFile = async (file) => {
  currentFile.value = file
  loadingPreview.value = true
  previewData.value = null
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
  console.log('[App] Crawler status changed:', newStatus)
  crawlerStatus.value = newStatus

  // 爬虫状态变化时刷新文件列表
  if (currentPlatform.value) {
    await selectPlatform(currentPlatform.value)
  }
}

// Lifecycle
onMounted(async () => {
  await fetchConfig()
  // Auto-load first platform's files
  if (platforms.value.length > 0) {
    await selectPlatform(platforms.value[0].value)
  }
})

onUnmounted(() => {
  currentPlatform.value = null
})
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  color: var(--text-color);
}

.app-header {
  height: 56px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1.5rem;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--primary-color);
}

.stats {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9rem;
  color: var(--secondary-color);
}

.stat-item strong {
  color: var(--text-color);
}

.stat-item {
  font-size: 0.8rem;
}

/* 左侧爬虫面板 */
.crawler-panel {
  width: 360px;
  min-width: 360px;
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  flex-shrink: 0;
}

/* 右侧数据面板 */
.data-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 平台标签栏 */
.platform-bar {
  padding: 0.75rem 1rem;
  background: rgba(13, 17, 23, 0.4);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.platform-bar h3 {
  margin: 0 0.75rem 0 0;
  font-size: 0.75rem;
  color: var(--secondary-color);
  text-transform: uppercase;
}

.platform-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.platform-tab {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.75rem;
  background: var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.platform-tab:hover {
  background: var(--hover-color);
}

.platform-tab.active {
  background: var(--primary-color);
  color: white;
}

.tab-icon {
  font-size: 1rem;
}

.tab-label {
  font-weight: 500;
}

.tab-count {
  background: rgba(255, 255, 255, 0.2);
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 0.7rem;
}

/* 内容区域 */
.content-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 文件列表 */
.files-section {
  width: 320px;
  min-width: 320px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-header {
  padding: 0.75rem 1rem;
  background: rgba(22, 27, 34, 0.5);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--secondary-color);
}

.file-controls {
  display: flex;
  gap: 0.5rem;
}

.search-input {
  width: 120px;
}

.type-select {
  width: 80px;
}

.files-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  max-height: calc(100vh - 250px);
  scrollbar-width: 6px;
}

.file-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.file-item:hover {
  background: var(--hover-color);
}

.file-item.active {
  background: rgba(35, 134, 54, 0.15);
  border-left: 3px solid var(--primary-color);
}

.file-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.7rem;
  color: var(--secondary-color);
}

/* 数据预览 */
.preview-section {
  flex: 1;
  overflow: hidden;
}

.table-wrapper {
  flex: 1;
  overflow: auto;
  padding: 0.5rem;
  scrollbar-width: 6px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

th, td {
  padding: 0.6rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

th {
  background: rgba(22, 27, 34, 0.9);
  position: sticky;
  top: 0;
  z-index: 1;
  font-weight: 600;
  color: var(--secondary-color);
}

.cell-content {
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 状态提示 */
.welcome-state {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: var(--secondary-color);
}

.welcome-content {
  text-align: center;
}

.welcome-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.welcome-content h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: var(--text-color);
}

.welcome-content p {
  margin: 0;
  font-size: 0.9rem;
}

.loading-spinner {
  border: 3px solid var(--primary-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: var(--secondary-color);
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--secondary-color);
  font-style: italic;
  font-size: 0.8rem;
}
</style>
