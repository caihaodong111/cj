<template>
  <div class="data-wrapper">
    <!-- Ambient Background Effects -->
    <div class="ambient-background">
      <div class="nebula blue"></div>
      <div class="nebula gold"></div>
      <div class="breathing-line gold-1"></div>
      <div class="breathing-line gold-2"></div>
      <div class="scan-grid"></div>
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
          <div class="kpi-icon-box" :class="{ 'is-brand-logo': isBrandLogo(currentPlatform) }">
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
              <span class="tag total">总数 {{ currentPlatformStats.count || 0 }}</span>
            </div>
          </div>
        </button>
      </div>

      <section class="data-table-section ios-glass entrance-scale-up-delay-4">
        <div class="table-header">
          <span class="accent-bar"></span>
          <span>{{ getPlatformLabel(currentPlatform) || '数据源' }} 数据列表</span>
          <div class="header-meta" v-if="currentFile">
            <span class="file-name">{{ currentFile.name }}</span>
            <span class="file-time">{{ formatDate(currentFile.modified_at) }}</span>
          </div>
        </div>

        <div class="table-wrapper" v-if="orderedRows.length">
          <table>
            <thead>
              <tr>
                <th v-for="col in columnDefs" :key="col.label">{{ col.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in orderedRows" :key="idx">
                <td v-for="col in columnDefs" :key="col.label">
                  <div v-if="col.type === 'avatar'" class="avatar-cell">
                    <img v-if="getFieldValue(row, col.keys)" :src="getFieldValue(row, col.keys)" alt="avatar" />
                    <span v-else>-</span>
                  </div>
                  <div v-else class="cell-content" :title="String(getFieldValue(row, col.keys))">
                    {{ formatValue(getFieldValue(row, col.keys)) }}
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
        <div v-else class="empty-state">
          <p>暂无数据</p>
          <p class="hint">请先选择渠道并启动爬虫</p>
        </div>
      </section>
    </div>

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
              <span class="platform-count">{{ platform.count }} 条</span>
            </div>
            <span class="platform-icon">
              <img v-if="getPlatformLogo(platform.value)" :src="getPlatformLogo(platform.value)" :alt="getPlatformLabel(platform.value)" class="platform-logo-img small" />
              <span v-else class="status-icon">{{ getPlatformIcon(platform.value) }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

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
const route = useRoute()
const currentPlatform = ref(null)
const files = ref([])
const currentFile = ref(null)
const previewData = ref(null)
const loadingPreview = ref(false)
const drawerVisible = ref(false)
const crawlerDialogVisible = ref(false)

const columnDefs = [
  { label: 'CREATE TIME', keys: ['create_time', 'created_time', 'createTime', 'CREATE TIME'] },
  { label: 'IP LOCATION', keys: ['ip_location', 'ipLocation', 'location', 'IP LOCATION'] },
  { label: 'CONTENT', keys: ['content', 'text', 'desc', 'note', '内容'] },
  { label: 'NICKNAME', keys: ['nickname', 'nick_name', 'user_name', 'author', 'NICKNAME'] },
  { label: 'AVATAR', keys: ['avatar', 'avatar_url', 'avatarUrl', 'head_url', 'head', 'AVATAR'], type: 'avatar' }
]

// Computed
const platformStats = computed(() => {
  const map = stats.value?.by_platform || {}
  return platforms.value.map(platform => ({
    ...platform,
    count: map[platform.value] || 0
  }))
})

const currentPlatformStats = computed(() => {
  return platformStats.value.find(item => item.value === currentPlatform.value) || {}
})

const currentPlatformCount = computed(() => {
  if (!currentPlatform.value) return 0
  const map = stats.value?.by_platform || {}
  return map[currentPlatform.value] || 0
})

const orderedRows = computed(() => previewData.value?.data || [])

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
  if (value === 'xhs') return '小红书'
  if (value === 'dy') return '抖音'
  return null
}

const isBrandLogo = (value) => value === 'xhs' || value === 'dy'

const formatValue = (val) => {
  if (val === null || val === undefined || val === '') return '-'
  if (typeof val === 'object') return JSON.stringify(val)
  if (String(val).startsWith('http')) return val
  return String(val).length > 50 ? String(val).substring(0, 50) + '...' : val
}

const handleSelectPlatform = async (platformValue) => {
  drawerVisible.value = false
  await selectPlatform(platformValue)
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
  padding: 2px;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.platform-logo-img:hover {
  transform: scale(1.05);
  background: rgba(255, 255, 255, 0.15);
}

.platform-logo-img.small {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  padding: 2px;
}

/* === iOS Style Base === */
.data-wrapper {
  min-height: 100vh;
  background: #030508;
  position: relative;
  overflow: hidden;
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
}

/* === Ambient Background Effects === */
.ambient-background {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.nebula {
  position: absolute;
  filter: blur(120px);
  opacity: 0.28;
  mix-blend-mode: screen;
}

.nebula.blue {
  width: 80vw;
  height: 70vh;
  background: radial-gradient(circle, #0066ff, transparent 75%);
  top: -10%;
  left: -5%;
}

.nebula.gold {
  width: 80vw;
  height: 70vh;
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
  background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: linear-gradient(to bottom, black, transparent);
  animation: gridMove 25s linear infinite;
}

@keyframes gridMove {
  from { background-position: 0 0; }
  to { background-position: 0 50px; }
}

/* === Layout === */
.data-view {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  gap: 24px;
  padding: 32px 40px 40px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 3;
}

.ios-title {
  font-size: 1.6rem;
  font-weight: 600;
  letter-spacing: 1px;
  margin: 0;
}

.subtitle {
  display: block;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 1px;
  margin-top: 6px;
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
  border-radius: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.8);
  transition: all 0.3s ease;
}

.ios-glass:hover {
  border-color: rgba(255, 170, 0, 0.15);
  box-shadow: 0 15px 40px rgba(0,0,0,0.5), 0 0 20px rgba(255, 170, 0, 0.1);
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
  border-radius: 24px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(255, 170, 0, 0.4), transparent 40%, rgba(255, 170, 0, 0.1));
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  animation: borderBreathe 6s infinite ease-in-out;
}

.border-glow.gold-tint {
  background: linear-gradient(135deg, rgba(255, 170, 0, 0.55), transparent 45%, rgba(255, 170, 0, 0.15));
}

@keyframes borderBreathe {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; box-shadow: inset 0 0 15px rgba(255, 170, 0, 0.2); }
}

.kpi-selector-container {
  margin: 30px 0;
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
  background: rgba(255, 170, 0, 0.12);
  color: #ffaa00;
}

.kpi-icon-box.is-brand-logo {
  background: transparent;
}

.status-icon {
  font-size: 26px;
}

.xhs-logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #ff2442;
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  user-select: none;
  box-shadow: none;
}

.xhs-logo.small {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  font-size: 10px;
  letter-spacing: 0.4px;
  box-shadow: none;
}

.douyin-logo {
  width: 40px;
  aspect-ratio: 0.87;
  padding: 6px calc(6px + 40px / 0.87 * 0.13 / 2);
  background-color: #000;
  display: grid;
  position: relative;
  border-radius: 10px;
}

.douyin-logo::before,
.douyin-logo::after {
  content: '';
  grid-area: 1 / 1;
}

.douyin-logo::before {
  background:
    radial-gradient(100% 100% at 100% 100%, transparent 0 50%, #08fff9 50% 100%, transparent) left 52%/41% 36% no-repeat,
    radial-gradient(50% 100% at top, transparent 44%, #08fff9 45% 98%, transparent) 0 100%/73% 31% no-repeat,
    linear-gradient(#08fff9, #08fff9) 66% 0/20% 70% no-repeat,
    radial-gradient(100% 100% at 100% 0, transparent 0 58%, #08fff9 58.5% 99%, transparent) 100% 0/47% 41.8% no-repeat;
}

.douyin-logo::after {
  --color: #f00044;
  background:
    radial-gradient(100% 100% at 100% 100%, transparent 0 50%, var(--color) 50% 100%, transparent) left 52%/41% 36% no-repeat,
    radial-gradient(50% 100% at top, transparent 44%, var(--color) 45% 98%, transparent) 0 100%/73% 31% no-repeat,
    linear-gradient(var(--color), var(--color)) 66% 0/20% 70% no-repeat,
    radial-gradient(100% 100% at 100% 0, transparent 0 58%, var(--color) 58.5% 99%, transparent) 100% 0/47% 41.8% no-repeat;
  transform: translate(3%, 3%);
  mix-blend-mode: lighten;
}

.douyin-logo.small {
  width: 32px;
  padding: 5px calc(5px + 32px / 0.87 * 0.13 / 2);
  border-radius: 8px;
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

/* === Data Table Section === */
.data-table-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 20px;
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
  padding: 1rem 1.5rem 1.5rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

th, td {
  padding: 0.85rem 0.6rem;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  justify-content: space-between;
  align-items: center;
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
  gap: 4px;
}

.platform-name {
  font-size: 0.95rem;
  font-weight: 600;
}

.platform-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.platform-icon {
  font-size: 1.4rem;
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
  animation: slideInRight 0.25s ease;
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
  animation: scaleIn 0.2s ease;
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

@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
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

@media (max-width: 960px) {
  .data-view {
    padding: 24px;
  }

  .hero-card {
    width: 100%;
  }

  .header-meta {
    display: none;
  }
}
</style>
