<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo">
        <span class="logo-icon">🕷️</span>
        <h1>MediaCrawler Insights</h1>
      </div>
      <div class="stats" v-if="stats">
        <span class="stat-item">
          <strong>{{ stats.total_files }}</strong> Files
        </span>
        <span class="stat-item">
          <strong>{{ formatBytes(stats.total_size) }}</strong> Data Size
        </span>
      </div>
    </header>

    <main class="main-content">
      <!-- Sidebar / Platform Selector -->
      <aside class="sidebar">
        <h3>Data Sources</h3>
        <div class="platform-list">
          <div 
            v-for="platform in platforms" 
            :key="platform.value"
            class="platform-card"
            :class="{ active: currentPlatform === platform.value }"
            @click="selectPlatform(platform.value)"
          >
            <span class="platform-icon">{{ getPlatformIcon(platform.value) }}</span>
            <span class="platform-name">{{ platform.label }}</span>
            <span class="platform-count" v-if="stats?.by_platform">{{ stats.by_platform[platform.value] || 0 }}</span>
          </div>
        </div>
      </aside>

      <!-- Content Area -->
      <section class="content-area">
        <!-- File Selector -->
        <div class="file-selector-bar" v-if="currentPlatform">
          <div class="file-list-header">
            <h2>{{ getPlatformLabel(currentPlatform) }} Files</h2>
            <div class="controls">
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Search files..." 
                class="search-input"
              />
              <select v-model="fileTypeFilter" class="type-select">
                <option value="">All Types</option>
                <option value="json">JSON</option>
                <option value="csv">CSV</option>
                <option value="xlsx">Excel</option>
              </select>
            </div>
          </div>

          <div class="files-grid" v-if="filteredFiles.length > 0">
            <div 
              v-for="file in filteredFiles" 
              :key="file.path"
              class="file-card"
              :class="{ active: currentFile?.path === file.path }"
              @click="selectFile(file)"
            >
              <div class="file-info">
                <div class="file-name" :title="file.name">{{ file.name }}</div>
                <div class="file-meta">
                  <span class="file-type">{{ file.type.toUpperCase() }}</span>
                  <span class="file-size">{{ formatBytes(file.size) }}</span>
                  <span class="file-date">{{ formatDate(file.modified_at) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="loadingFiles" class="loading-state">
            <div class="loading-spinner"></div>
            <p style="text-align:center; color: var(--secondary-color);">Fetching files...</p>
          </div>
          <div v-else class="empty-state">
            No files found for this platform.
          </div>
        </div>

        <!-- Data Preview -->
        <div class="data-preview-panel" v-if="currentFile">
          <div class="panel-header">
            <h3>{{ currentFile.name }} <span class="record-count" v-if="previewData?.total">({{ previewData.total }} records)</span></h3>
            <div class="actions">
              <button @click="downloadFile(currentFile)" class="btn-download">Download</button>
            </div>
          </div>

          <div class="table-container" v-if="previewData && previewData.data && previewData.data.length > 0">
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
          </div>
          <div v-else class="empty-preview">
            Select a file to preview data.
          </div>
        </div>
        
        <div v-else-if="!currentPlatform" class="welcome-screen">
          <div class="welcome-content">
            <h2>Select a Data Source</h2>
            <p>Choose a platform from the sidebar to view crawled data.</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

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

// Computed
const filteredFiles = computed(() => {
  return files.value.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(searchQuery.value.toLowerCase())
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
  return new Date(timestamp * 1000).toLocaleDateString()
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
  const p = platforms.value.find(p => p.value === value)
  return p ? p.label : value
}

const formatHeader = (key) => {
  return key.replace(/_/g, ' ').toUpperCase()
}

const getDataKeys = (row) => {
  if (!row) return []
  return Object.keys(row)
}

const formatValue = (val) => {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'object') return JSON.stringify(val)
  if (String(val).startsWith('http')) return val // Could render as link
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

const downloadFile = (file) => {
  window.open(`/api/data/download/${file.path}`, '_blank')
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 100vw;
  color: var(--text-color);
}

.app-header {
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--primary-color);
}

.stats {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: var(--secondary-color);
}

.stat-item strong {
  color: var(--text-color);
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background: rgba(13, 17, 23, 0.4);
  border-right: 1px solid var(--border-color);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sidebar h3 {
  font-size: 0.8rem;
  text-transform: uppercase;
  color: var(--secondary-color);
  margin-bottom: 0.5rem;
}

.platform-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.platform-card {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-color);
}

.platform-card:hover {
  background: var(--hover-color);
}

.platform-card.active {
  background: rgba(88, 166, 255, 0.15);
  color: var(--primary-color);
  border-left: 3px solid var(--primary-color);
}

.platform-icon {
  margin-right: 0.75rem;
  font-size: 1.2rem;
}

.platform-name {
  flex: 1;
  font-weight: 500;
}

.platform-count {
  font-size: 0.8rem;
  background: var(--border-color);
  padding: 2px 6px;
  border-radius: 10px;
  color: var(--text-color);
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 1rem;
  gap: 1rem;
}

.file-selector-bar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 40%;
}

.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.controls {
  display: flex;
  gap: 0.5rem;
}

.search-input, .type-select {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 0.5rem;
  border-radius: 4px;
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.file-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.file-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  border-color: var(--primary-color);
}

.file-card.active {
  border-color: var(--primary-color);
  background: rgba(88, 166, 255, 0.05);
}

.file-name {
  font-weight: 600;
  margin-bottom: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--secondary-color);
}

.data-preview-panel {
  flex: 1;
  background: var(--glass-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-download {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.table-container {
  overflow: auto;
  flex: 1;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

th, td {
  padding: 0.75rem 1rem;
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

tr:hover {
  background: var(--hover-color);
}

.welcome-screen, .empty-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--secondary-color);
  text-align: center;
}
</style>
