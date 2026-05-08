<template>
  <div class="crawler-control">
    <div class="overview-grid">
      <div class="overview-card primary">
        <span class="overview-label">当前平台</span>
        <strong class="overview-value">{{ getPlatformLabel(config.platform) }}</strong>
        <span class="overview-meta">跟随当前数据源</span>
      </div>

      <div class="overview-card">
        <span class="overview-label">登录方式</span>
        <strong class="overview-value">{{ loginTypeLabel }}</strong>
        <span class="overview-meta">{{ loginTypeMeta }}</span>
      </div>

      <div class="overview-card" :class="isRunning ? 'running' : 'idle'">
        <span class="overview-label">任务状态</span>
        <strong class="overview-value">{{ isRunning ? '更新中' : '待启动' }}</strong>
        <span class="overview-meta">{{ statusMetaText }}</span>
      </div>
    </div>

    <div v-if="formMessage" class="inline-notice" :class="formMessage.type">
      {{ formMessage.text }}
    </div>

    <div class="config-form">
      <section class="form-section">
        <div class="section-header">
          <div>
            <h3 class="section-title">任务配置</h3>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>平台</label>
            <el-select v-model="config.platform" :disabled="isRunning" class="crawler-select" popper-class="crawler-dropdown" :teleported="false">
              <el-option v-for="p in platforms" :key="p.value" :label="p.label" :value="p.value" />
            </el-select>
          </div>

          <div class="form-group">
            <label>登录方式</label>
            <el-select v-model="config.login_type" :disabled="isRunning" class="crawler-select" popper-class="crawler-dropdown" :teleported="false">
              <el-option label="Cookie 登录" value="cookie" />
              <el-option label="扫码登录" value="qrcode" />
            </el-select>
          </div>

          <div class="form-group">
            <label>更新模式</label>
            <el-select v-model="config.crawler_type" :disabled="isRunning" class="crawler-select" popper-class="crawler-dropdown" :teleported="false">
              <el-option label="搜索模式" value="search" />
              <el-option label="详情模式" value="detail" />
              <el-option label="创作者模式" value="creator" />
            </el-select>
          </div>
        </div>
      </section>

      <section class="form-section">
        <div class="section-header">
          <div>
            <h3 class="section-title">{{ scopeTitle }}</h3>
            <p v-if="crawlerTypeHint" class="section-description">{{ crawlerTypeHint }}</p>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group full-width" v-if="config.crawler_type === 'search'">
            <input
              type="text"
              v-model="config.keywords"
              placeholder="例如：品牌名, 产品词, 事件词"
              :disabled="isRunning"
              class="cyber-input"
            />
            <p class="field-hint">多个关键词用逗号分隔。</p>
          </div>

          <div class="form-group full-width" v-else-if="config.crawler_type === 'detail'">
            <input
              type="text"
              v-model="config.specified_ids"
              placeholder="例如：12345678,87654321"
              :disabled="isRunning"
              class="cyber-input"
            />
            <p class="field-hint">多个 ID 用逗号分隔。</p>
          </div>

          <div class="form-group full-width" v-else>
            <input
              type="text"
              v-model="config.creator_ids"
              placeholder="例如：user123,user456"
              :disabled="isRunning"
              class="cyber-input"
            />
            <p class="field-hint">多个 ID 用逗号分隔。</p>
          </div>
        </div>
      </section>

      <section class="form-section">
        <div class="section-header">
          <div>
            <h3 class="section-title">采集选项</h3>
          </div>
        </div>

        <div class="checkbox-group">
          <label class="cyber-checkbox" :class="{ 'is-disabled': isRunning }">
            <input type="checkbox" v-model="config.enable_comments" :disabled="isRunning" />
            <span>抓取评论</span>
          </label>

          <label class="cyber-checkbox" :class="{ 'is-disabled': isRunning || !config.enable_comments }">
            <input type="checkbox" v-model="config.enable_sub_comments" :disabled="isRunning || !config.enable_comments" />
            <span>抓取子评论</span>
          </label>

          <label class="cyber-checkbox" :class="{ 'is-disabled': isRunning || config.login_type === 'qrcode' }">
            <input type="checkbox" v-model="config.headless" :disabled="isRunning || config.login_type === 'qrcode'" />
            <span>无头模式</span>
          </label>
        </div>

        <div v-if="config.login_type === 'cookie'" class="support-card" :class="{ warning: !cookieState.exists }">
          <div>
            <p class="support-card-title">{{ cookieState.exists ? '已检测到有效 Cookie' : '未检测到有效 Cookie' }}</p>
            <p class="support-card-body">
              {{ cookieState.exists ? '启动时自动使用系统设置中的激活 Cookie。' : '请先在系统设置中启用当前平台的 Cookie。' }}
            </p>
          </div>
          <span class="support-pill" :class="cookieState.exists ? 'success' : 'warning'">
            {{ cookieState.loading ? '检测中' : (cookieState.exists ? '可直接启动' : '需先配置') }}
          </span>
        </div>

        <div v-else class="support-card">
          <div>
            <p class="support-card-title">{{ qrSupportTitle }}</p>
            <p class="support-card-body">{{ qrSupportBody }}</p>
          </div>
          <button
            v-if="showNoVncShortcut"
            type="button"
            class="cyber-btn cyber-btn-secondary support-card-action"
            :disabled="isRunning"
            @click="openRemoteDesktop"
          >
            打开 noVNC
          </button>
        </div>

        <div v-if="config.login_type === 'qrcode'" class="form-row qr-mode-row">
          <div class="form-group">
            <label>扫码浏览器</label>
            <el-select v-model="config.qr_browser_mode" :disabled="isRunning" class="crawler-select" popper-class="crawler-dropdown" :teleported="false">
              <el-option label="独立浏览器（推荐）" value="isolated" />
              <el-option label="外部 Chrome CDP" value="external_cdp" />
            </el-select>
            <p class="field-hint">{{ qrBrowserModeHint }}</p>
          </div>

          <div v-if="isExternalCdpMode" class="form-group">
            <label>外部 CDP 地址</label>
            <input
              type="text"
              v-model="config.external_cdp_url"
              placeholder="例如：http://127.0.0.1:9222"
              :disabled="isRunning"
              class="cyber-input"
            />
            <p class="field-hint">只有在你明确要复用已开启调试端口的 Chrome 时才需要填写。</p>
          </div>
        </div>
      </section>

      <div class="form-actions">
        <button
          v-if="!isRunning"
          @click="startCrawler"
          class="cyber-btn cyber-btn-primary action-btn"
          :disabled="starting || (config.login_type === 'cookie' && !cookieState.exists)"
        >
          <span class="action-btn-kicker">{{ starting ? 'Submitting' : 'Update Task' }}</span>
          <span class="action-btn-label">{{ starting ? '提交中...' : '提交更新任务' }}</span>
        </button>
        <button
          v-else
          @click="stopCrawler"
          class="cyber-btn cyber-btn-danger action-btn"
          :disabled="stopping"
        >
          <span class="action-btn-kicker">{{ stopping ? 'Stopping' : 'Stop Task' }}</span>
          <span class="action-btn-label">{{ stopping ? '停止中...' : '停止更新任务' }}</span>
        </button>
      </div>
    </div>

    <div v-if="qrDialog.visible" class="qr-modal-overlay" @click.self="closeQrDialog">
      <div class="qr-modal">
        <div class="qr-modal-header">
          <div>
            <h3>{{ qrDialogTitle }}</h3>
            <p>{{ qrDialogSubtitle }}</p>
          </div>
          <button type="button" class="qr-close-btn" aria-label="关闭" @click="closeQrDialog">
            ×
          </button>
        </div>

        <div class="qr-status-pill" :class="`is-${qrDialog.status}`">
          {{ qrStatusText }}
        </div>

        <div class="qr-image-panel">
          <img
            v-if="qrDialog.image"
            :src="qrDialog.image"
            :alt="`${qrDialogPlatformLabel} 二维码`"
            class="qr-image"
          />
          <div v-else class="qr-placeholder">
            <div class="qr-spinner"></div>
            <span>{{ qrPlaceholderText }}</span>
          </div>
        </div>

        <p class="qr-hint">{{ qrPrimaryHint }}</p>
        <p class="qr-hint qr-meta">{{ qrSecondaryHint }}</p>
        <p v-if="qrUpdatedAtText" class="qr-hint qr-meta">最近更新时间：{{ qrUpdatedAtText }}</p>
        <p v-if="qrDialog.error" class="qr-error">{{ qrDialog.error }}</p>

        <div class="qr-actions">
          <button v-if="showNoVncShortcut" type="button" class="cyber-btn cyber-btn-secondary" @click="openRemoteDesktop">
            打开 noVNC
          </button>
          <button
            type="button"
            class="cyber-btn cyber-btn-secondary"
            :disabled="qrDialog.loading"
            @click="refreshQrDialog"
          >
            {{ qrDialog.loading ? '刷新中...' : '刷新二维码' }}
          </button>
          <button type="button" class="cyber-btn cyber-btn-primary" @click="closeQrDialog">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'

// 定义事件
const emit = defineEmits(['crawler-status-change', 'platform-change'])
const props = defineProps({
  currentPlatform: {
    type: String,
    default: ''
  }
})

// State
const platforms = ref([])
const status = ref('idle')
const starting = ref(false)
const stopping = ref(false)
const formMessage = ref(null)
const cookieState = ref({
  loading: false,
  exists: false,
  platform: ''
})
let statusInterval = null
let qrInterval = null

const createQrDialogState = () => ({
  visible: false,
  platform: '',
  image: '',
  status: 'idle',
  error: '',
  updatedAt: null,
  loading: false
})

const qrDialog = ref(createQrDialogState())

// Computed
const isRunning = computed(() => status.value === 'running')
const remoteDesktopUrl = computed(() => {
  if (typeof window === 'undefined') {
    return 'http://服务器IP:6080'
  }
  const host = window.location.hostname || '服务器IP'
  return `http://${host}:6080`
})
const isExternalCdpMode = computed(() => config.value.login_type === 'qrcode' && normalizeQrBrowserMode(config.value.qr_browser_mode) === 'external_cdp')
const showNoVncShortcut = computed(() => config.value.login_type === 'qrcode' && !isExternalCdpMode.value)
const qrDialogPlatformLabel = computed(() => getPlatformLabel(qrDialog.value.platform))
const qrDialogTitle = computed(() => `${qrDialogPlatformLabel.value} 扫码登录`)
const qrDialogSubtitle = computed(() => {
  if (qrDialog.value.status === 'success' && !qrDialog.value.image) {
    return '已检测到当前平台仍处于登录态，任务正在继续执行。'
  }
  return '仅在当前任务确实需要扫码时显示二维码。'
})
const qrStatusText = computed(() => {
  const textMap = {
    idle: '检查登录状态',
    pending: '等待扫码',
    success: qrDialog.value.image ? '登录成功' : '已复用登录态',
    failed: '登录失败'
  }
  return textMap[qrDialog.value.status] || qrDialog.value.status || '等待启动'
})
const qrPlaceholderText = computed(() => {
  if (qrDialog.value.status === 'failed') {
    return '二维码生成失败或登录流程已中断'
  }
  if (qrDialog.value.status === 'success') {
    return qrDialog.value.image
      ? '登录已成功，等待后端同步页面状态'
      : '当前平台已复用登录态，无需再次扫码'
  }
  if (qrDialog.value.status === 'pending') {
    return '二维码同步中，请稍候...'
  }
  return '正在检查当前平台是否仍处于登录态，如需扫码会自动显示二维码。'
})
const qrPrimaryHint = computed(() => {
  if (isExternalCdpMode.value) {
    return '后台页面会保持当前界面；如需扫码，请在你连接的外部 Chrome 页面中完成。'
  }
  return `后台页面会保持当前界面；本地部署请在独立浏览器中扫码，服务器部署请打开 ${remoteDesktopUrl.value} 完成扫码。`
})
const qrSecondaryHint = computed(() => {
  if (isExternalCdpMode.value) {
    return '登录状态每 2 秒自动刷新；只有真正需要扫码时才会弹出二维码。'
  }
  return '系统会优先使用独立浏览器或 noVNC 完成扫码，后台页不会强制切换到目标平台。'
})
const qrUpdatedAtText = computed(() => {
  if (!qrDialog.value.updatedAt) return ''
  const updatedAt = new Date(qrDialog.value.updatedAt * 1000)
  if (Number.isNaN(updatedAt.getTime())) return ''
  return updatedAt.toLocaleString()
})
const loginTypeLabel = computed(() => config.value.login_type === 'cookie' ? 'Cookie 登录' : '扫码登录')
const loginTypeMeta = computed(() => {
  if (config.value.login_type === 'cookie') {
    if (cookieState.value.loading) return '检测系统 Cookie'
    return cookieState.value.exists ? '复用系统 Cookie' : '当前平台无可用 Cookie'
  }
  return isExternalCdpMode.value
    ? '当前页保持不动，扫码在外部 Chrome 中进行'
    : '当前页保持不动，扫码在独立浏览器或 noVNC 中进行'
})
const qrSupportTitle = computed(() => {
  return isExternalCdpMode.value ? '扫码登录 / 外部 Chrome' : '扫码登录 / 独立浏览器'
})
const qrSupportBody = computed(() => {
  if (isExternalCdpMode.value) {
    return '后台前端会留在当前页面，任务会在你连接的外部 Chrome CDP 上下文中打开平台登录页。'
  }
  return '后台前端会留在当前页面，任务会在独立浏览器标签页或服务器 noVNC 浏览器中打开平台登录页。'
})
const qrBrowserModeHint = computed(() => {
  if (isExternalCdpMode.value) {
    return '适合本地调试或需要复用现有浏览器环境的场景，必须提供可访问的 Chrome DevTools 地址。'
  }
  return '推荐：使用系统单独拉起的浏览器配置目录，扫码过程不会打断当前后台界面。'
})
const statusMetaText = computed(() => {
  return isRunning.value
    ? '后端任务执行中'
    : '可提交更新任务'
})
const scopeTitle = computed(() => {
  const textMap = {
    search: '搜索关键词',
    detail: '内容 ID',
    creator: '创作者 ID'
  }
  return textMap[config.value.crawler_type] || '更新范围'
})
const crawlerTypeHint = computed(() => {
  const textMap = {
    search: '',
    detail: '输入内容 ID，补抓单条内容详情。',
    creator: '输入创作者 ID，更新指定账号内容。'
  }
  return textMap[config.value.crawler_type] || ''
})

// Config
const config = ref({
  platform: 'xhs',
  login_type: 'cookie',
  crawler_type: 'search',
  keywords: '',
  specified_ids: '',
  creator_ids: '',
  enable_comments: false,
  enable_sub_comments: false,
  headless: true,
  qr_browser_mode: 'isolated',
  external_cdp_url: ''
})

const QR_BROWSER_PREFS_KEY = 'mediacrawler.qr_browser_prefs'

const normalizeQrBrowserMode = (mode) => {
  return mode === 'external_cdp' ? 'external_cdp' : 'isolated'
}

const loadQrBrowserPrefs = () => {
  if (typeof window === 'undefined') return

  try {
    const rawPrefs = window.localStorage.getItem(QR_BROWSER_PREFS_KEY)
    if (!rawPrefs) return

    const parsedPrefs = JSON.parse(rawPrefs)
    config.value.qr_browser_mode = normalizeQrBrowserMode(parsedPrefs?.qr_browser_mode)
    config.value.external_cdp_url = typeof parsedPrefs?.external_cdp_url === 'string'
      ? parsedPrefs.external_cdp_url
      : ''
  } catch (e) {
    console.warn('读取扫码浏览器偏好失败:', e)
  }
}

const persistQrBrowserPrefs = () => {
  if (typeof window === 'undefined') return

  try {
    window.localStorage.setItem(QR_BROWSER_PREFS_KEY, JSON.stringify({
      qr_browser_mode: normalizeQrBrowserMode(config.value.qr_browser_mode),
      external_cdp_url: config.value.external_cdp_url || ''
    }))
  } catch (e) {
    console.warn('保存扫码浏览器偏好失败:', e)
  }
}

const getPlatformLabel = (platformValue) => {
  const matched = platforms.value.find((item) => item.value === platformValue)
  return matched?.label || platformValue || '平台'
}

const setFormMessage = (type, text) => {
  formMessage.value = { type, text }
}

const clearFormMessage = () => {
  formMessage.value = null
}

const stopQrPolling = () => {
  if (qrInterval) {
    clearInterval(qrInterval)
    qrInterval = null
  }
}

const closeQrDialog = () => {
  stopQrPolling()
  qrDialog.value = {
    ...qrDialog.value,
    visible: false,
    error: '',
    loading: false
  }
}

const openRemoteDesktop = () => {
  window.open(remoteDesktopUrl.value, '_blank', 'noopener,noreferrer')
}

const applyQrPayload = (platform, qrPayload = {}, statusPayload = {}) => {
  if (platform !== qrDialog.value.platform) return

  const previousStatus = qrDialog.value.status
  const wasVisible = qrDialog.value.visible
  const nextImage = qrPayload.qr_code || ''
  const nextStatus = statusPayload.status || (nextImage ? 'pending' : 'idle')

  qrDialog.value.image = nextImage
  qrDialog.value.updatedAt = qrPayload.updated_at || statusPayload.updated_at || null
  qrDialog.value.status = nextStatus
  qrDialog.value.error = ''

  if (nextStatus === 'success' && !nextImage) {
    qrDialog.value.visible = false
    if (previousStatus !== 'success') {
      setFormMessage('success', `${getPlatformLabel(platform)} 已检测到现有登录态，无需再次扫码。`)
    }
  } else if (nextStatus === 'failed') {
    qrDialog.value.visible = true
    if (previousStatus !== 'failed') {
      setFormMessage('error', `${getPlatformLabel(platform)} 登录流程失败，未能获取可用二维码。`)
    }
  } else if (nextImage || nextStatus === 'pending') {
    qrDialog.value.visible = true
    if (!wasVisible) {
      setFormMessage('info', '二维码已准备好，请在面板中完成扫码。')
    }
  }

  if (nextStatus === 'success' || nextStatus === 'failed') {
    stopQrPolling()
  }
}

const fetchQrDialogData = async ({ silent = false } = {}) => {
  const platform = qrDialog.value.platform
  if (!platform) return

  if (!silent) {
    qrDialog.value.loading = true
  }

  try {
    const [qrRes, statusRes] = await Promise.all([
      axios.get(`/api/login/qr/${platform}`),
      axios.get(`/api/login/qr/${platform}/status`)
    ])
    applyQrPayload(platform, qrRes.data, statusRes.data)
  } catch (e) {
    if (platform !== qrDialog.value.platform) return
    const errorMsg = e.response?.data?.error || e.message || '获取二维码失败'
    qrDialog.value.error = errorMsg
  } finally {
    if (platform === qrDialog.value.platform) {
      qrDialog.value.loading = false
    }
  }
}

const startQrPolling = () => {
  stopQrPolling()
  void fetchQrDialogData()
  qrInterval = setInterval(() => {
    void fetchQrDialogData({ silent: true })
  }, 2000)
}

const openQrDialog = (platform) => {
  qrDialog.value = {
    ...createQrDialogState(),
    visible: false,
    platform,
    status: 'idle'
  }
  startQrPolling()
}

const refreshQrDialog = async () => {
  await fetchQrDialogData()
}

const fetchActiveCookieStatus = async (platform = config.value.platform) => {
  if (!platform) return

  cookieState.value = {
    ...cookieState.value,
    loading: true,
    platform
  }

  try {
    const res = await axios.get('/api/cookies/active', {
      params: { platform }
    })
    if (platform !== config.value.platform) return
    cookieState.value = {
      loading: false,
      exists: Boolean(res.data?.exists),
      platform
    }
  } catch (e) {
    if (platform !== config.value.platform) return
    cookieState.value = {
      loading: false,
      exists: false,
      platform
    }
  }
}

watch(
  () => props.currentPlatform,
  (nextPlatform) => {
    if (!nextPlatform) return
    if (config.value.platform !== nextPlatform) {
      config.value.platform = nextPlatform
    }
  },
  { immediate: true }
)

watch(
  () => config.value.platform,
  (nextPlatform) => {
    if (!nextPlatform) return
    clearFormMessage()
    void fetchActiveCookieStatus(nextPlatform)
  },
  { immediate: true }
)

watch(
  () => config.value.login_type,
  (nextLoginType) => {
    clearFormMessage()
    if (nextLoginType === 'qrcode') {
      config.value.headless = false
    }
    if (nextLoginType !== 'qrcode' && qrDialog.value.visible) {
      closeQrDialog()
    }
  }
)

watch(
  () => config.value.crawler_type,
  () => {
    clearFormMessage()
  }
)

watch(
  () => [config.value.qr_browser_mode, config.value.external_cdp_url],
  () => {
    persistQrBrowserPrefs()
  }
)

watch(
  () => config.value.enable_comments,
  (enabled) => {
    if (!enabled) {
      config.value.enable_sub_comments = false
    }
  }
)

// Methods
const fetchPlatforms = async () => {
  try {
    const res = await axios.get('/api/config/platforms')
    platforms.value = res.data.platforms
    if (!platforms.value.some(item => item.value === config.value.platform) && platforms.value[0]) {
      config.value.platform = platforms.value[0].value
    }
  } catch (e) {
    console.error('获取平台列表失败:', e)
  }
}

const fetchStatus = async ({ emitIfUnchanged = false } = {}) => {
  try {
    const res = await axios.get('/api/crawler/status')
    const newStatus = res.data.status
    const previousStatus = status.value

    status.value = newStatus

    // 组件重新挂载时也要把当前状态同步给父组件，避免父级残留旧状态。
    if (previousStatus !== newStatus || emitIfUnchanged) {
      emit('crawler-status-change', newStatus)
    }
  } catch (e) {
    console.error('获取状态失败:', e)
  }
}

const startCrawler = async () => {
  clearFormMessage()
  starting.value = true
  try {
    if (config.value.login_type === 'cookie' && !cookieState.value.exists) {
      setFormMessage('error', '当前平台还没有可用 Cookie，请先到系统设置中配置并启用。')
      return
    }

    if (config.value.crawler_type === 'search' && !config.value.keywords.trim()) {
      setFormMessage('error', '请输入至少一个搜索关键词。')
      return
    }

    if (config.value.crawler_type === 'detail' && !config.value.specified_ids.trim()) {
      setFormMessage('error', '请输入至少一个内容 ID。')
      return
    }

    if (config.value.crawler_type === 'creator' && !config.value.creator_ids.trim()) {
      setFormMessage('error', '请输入至少一个创作者 ID。')
      return
    }

    const requestConfig = {
      ...config.value,
      save_option: 'db',
      start_page: 1
    }

    if (requestConfig.login_type === 'qrcode') {
      requestConfig.headless = false
      requestConfig.qr_browser_mode = normalizeQrBrowserMode(requestConfig.qr_browser_mode)

      if (requestConfig.qr_browser_mode === 'external_cdp') {
        const cdpUrl = (requestConfig.external_cdp_url || '').trim()
        if (!cdpUrl) {
          setFormMessage('error', '外部 Chrome CDP 模式需要先填写可访问的 CDP 地址。')
          return
        }
        requestConfig.cdp_url = cdpUrl
      }
    }

    if (!requestConfig.enable_comments) {
      requestConfig.enable_sub_comments = false
    }

    delete requestConfig.qr_browser_mode
    delete requestConfig.external_cdp_url

    emit('platform-change', requestConfig.platform)
    await axios.post('/api/crawler/start', requestConfig)
    if (requestConfig.login_type === 'qrcode') {
      openQrDialog(requestConfig.platform)
      setFormMessage(
        'info',
        requestConfig.cdp_url
          ? '任务已提交，后台页面会保持当前界面；如需扫码，请在外部 Chrome 页面中完成。'
          : '任务已提交，后台页面会保持当前界面；如需扫码，请在独立浏览器或 noVNC 中完成。'
      )
    } else {
      setFormMessage('success', '任务已提交，平台数据开始更新。')
    }
    await fetchStatus()
  } catch (e) {
    const errorMsg = e.response?.data?.error || e.response?.data?.detail || e.message
    setFormMessage('error', `启动失败：${errorMsg}`)
  } finally {
    starting.value = false
  }
}

const stopCrawler = async () => {
  clearFormMessage()
  stopping.value = true
  try {
    await axios.post('/api/crawler/stop')
    closeQrDialog()
    await fetchStatus()
    setFormMessage('info', '已发送停止指令，任务状态会在后端完成同步后更新。')
  } catch (e) {
    const errorMsg = e.response?.data?.error || e.response?.data?.detail || e.message
    setFormMessage('error', `停止失败：${errorMsg}`)
  } finally {
    stopping.value = false
  }
}

// Lifecycle
onMounted(async () => {
  loadQrBrowserPrefs()
  await fetchPlatforms()
  await fetchStatus({ emitIfUnchanged: true })
  await fetchActiveCookieStatus(config.value.platform)

  statusInterval = setInterval(async () => {
    await fetchStatus()
  }, 2000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
  stopQrPolling()
})
</script>

<style scoped>
.crawler-control {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 72vh;
  overflow-y: auto;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  color: #fff;
  padding-right: 6px;
}

.crawler-control::-webkit-scrollbar {
  width: 5px;
}

.crawler-control::-webkit-scrollbar-track {
  background: transparent;
}

.crawler-control::-webkit-scrollbar-thumb {
  background: rgba(0, 204, 255, 0.26);
  border-radius: 999px;
}

.crawler-control::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 204, 255, 0.42);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.overview-card {
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background:
    radial-gradient(circle at top right, rgba(0, 204, 255, 0.1), transparent 45%),
    rgba(255, 255, 255, 0.03);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.overview-card.primary {
  background:
    radial-gradient(circle at top right, rgba(255, 170, 0, 0.12), transparent 45%),
    radial-gradient(circle at bottom left, rgba(0, 204, 255, 0.1), transparent 40%),
    rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 170, 0, 0.16);
}

.overview-card.running {
  border-color: rgba(255, 170, 0, 0.2);
  box-shadow: 0 0 24px rgba(255, 170, 0, 0.08);
}

.overview-label {
  font-size: 10px;
  letter-spacing: 1.8px;
  text-transform: uppercase;
  color: rgba(255, 170, 0, 0.74);
}

.overview-value {
  font-size: 18px;
  font-weight: 700;
  color: #f3f8ff;
  letter-spacing: 0.2px;
}

.overview-meta {
  color: #89a0c1;
  font-size: 12px;
  line-height: 1.55;
}

.inline-notice {
  padding: 12px 14px;
  border-radius: 16px;
  font-size: 13px;
  line-height: 1.6;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.inline-notice.info {
  color: #d9ecff;
  background: rgba(0, 204, 255, 0.08);
  border-color: rgba(0, 204, 255, 0.18);
}

.inline-notice.success {
  color: #d8f7ea;
  background: rgba(32, 195, 115, 0.1);
  border-color: rgba(32, 195, 115, 0.2);
}

.inline-notice.error {
  color: #ffd7d7;
  background: rgba(255, 77, 109, 0.1);
  border-color: rgba(255, 77, 109, 0.22);
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-section {
  padding: 16px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background:
    radial-gradient(circle at top right, rgba(0, 204, 255, 0.06), transparent 45%),
    rgba(255, 255, 255, 0.025);
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-title {
  margin: 0;
  font-size: 14px;
  color: #f1f6ff;
  letter-spacing: 0.3px;
}

.section-description {
  margin: 5px 0 0;
  color: #8298b7;
  font-size: 12px;
  line-height: 1.6;
}

.form-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 150px;
}

.form-group.full-width {
  flex: 1 1 100%;
}

.form-group > label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.72);
  font-weight: 500;
  letter-spacing: 0.3px;
}

.field-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: #8399b8;
  line-height: 1.55;
}

.cyber-input {
  width: 100%;
  padding: 10px 12px;
  background: rgba(10, 10, 15, 0.78);
  border: 1px solid rgba(0, 204, 255, 0.16);
  border-radius: 14px;
  color: #fff;
  font-size: 13px;
  transition: all 0.18s ease;
}

.cyber-input:focus {
  outline: none;
  border-color: rgba(255, 170, 0, 0.45);
  box-shadow: 0 0 14px rgba(255, 170, 0, 0.16);
  background: rgba(16, 18, 28, 0.88);
}

.cyber-input::placeholder {
  color: rgba(255, 255, 255, 0.34);
}

.cyber-input:disabled {
  opacity: 0.42;
  cursor: not-allowed;
  border-color: rgba(255, 255, 255, 0.08);
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.cyber-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 12px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  font-size: 13px;
  color: #eef6ff;
  transition: all 0.18s ease;
}

.cyber-checkbox:hover {
  border-color: rgba(255, 170, 0, 0.16);
  background: rgba(255, 255, 255, 0.04);
}

.cyber-checkbox.is-disabled {
  opacity: 0.46;
  cursor: not-allowed;
}

.cyber-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #ffae00;
  cursor: pointer;
}

.support-card {
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid rgba(0, 204, 255, 0.14);
  background:
    radial-gradient(circle at top right, rgba(0, 204, 255, 0.08), transparent 45%),
    rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.support-card.warning {
  border-color: rgba(255, 170, 0, 0.24);
  background:
    radial-gradient(circle at top right, rgba(255, 170, 0, 0.1), transparent 45%),
    rgba(255, 255, 255, 0.03);
}

.support-card-action {
  flex-shrink: 0;
  align-self: center;
}

.support-card-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #f2f7ff;
}

.support-card-body {
  margin: 6px 0 0;
  color: #8ba0bf;
  font-size: 12px;
  line-height: 1.65;
}

.qr-mode-row {
  margin-top: 14px;
}

.support-pill {
  flex-shrink: 0;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 11px;
  letter-spacing: 0.4px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.support-pill.success {
  color: #baf5d8;
  background: rgba(32, 195, 115, 0.12);
  border-color: rgba(32, 195, 115, 0.22);
}

.support-pill.warning {
  color: #ffd78b;
  background: rgba(255, 170, 0, 0.12);
  border-color: rgba(255, 170, 0, 0.22);
}

:deep(.crawler-select .el-select__wrapper) {
  background: rgba(10, 10, 15, 0.78);
  border: 1px solid rgba(0, 204, 255, 0.16);
  border-radius: 14px;
  box-shadow: none;
  padding: 7px 12px;
  min-height: 38px;
  transition: all 0.18s ease;
}

:deep(.crawler-select .el-select__wrapper:hover) {
  border-color: rgba(255, 170, 0, 0.26);
  background: rgba(16, 18, 28, 0.88);
}

:deep(.crawler-select .el-select__wrapper.is-focus) {
  border-color: rgba(255, 170, 0, 0.45);
  box-shadow: 0 0 14px rgba(255, 170, 0, 0.16);
}

:deep(.crawler-select .el-select__selected-item) {
  color: #fff;
  font-size: 13px;
}

:deep(.crawler-select .el-select__placeholder) {
  color: rgba(255, 255, 255, 0.34);
  font-size: 13px;
}

:deep(.crawler-select .el-select__suffix) {
  color: rgba(255, 255, 255, 0.48);
}

:deep(.crawler-select.is-disabled .el-select__wrapper) {
  opacity: 0.42;
  border-color: rgba(255, 255, 255, 0.08);
}

:deep(.crawler-dropdown) {
  background: rgba(12, 16, 24, 0.88) !important;
  backdrop-filter: blur(30px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 18px !important;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35) !important;
}

:deep(.crawler-dropdown .el-select-dropdown__list) {
  background: transparent !important;
  padding: 6px 8px !important;
}

:deep(.crawler-dropdown .el-select-dropdown__item) {
  color: #9bb0cc !important;
  font-size: 13px !important;
  height: 36px !important;
  line-height: 36px !important;
  margin: 1px 4px !important;
  border-radius: 10px !important;
  padding: 0 12px !important;
  transition: all 0.16s ease !important;
}

:deep(.crawler-dropdown .el-select-dropdown__item:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #ffffff !important;
}

:deep(.crawler-dropdown .el-select-dropdown__item.is-selected) {
  background: rgba(255, 170, 0, 0.15) !important;
  color: #ffcf69 !important;
  font-weight: 500 !important;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 16px;
  margin-top: 4px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.cyber-btn {
  padding: 10px 20px;
  border: 1px solid;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.3px;
  background: rgba(10, 10, 15, 0.82);
}

.action-btn {
  min-width: 220px;
  min-height: 54px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 3px;
  padding: 11px 18px;
  border-radius: 18px;
}

.action-btn-kicker {
  font-size: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
  opacity: 0.72;
}

.action-btn-label {
  font-size: 14px;
  line-height: 1.2;
}

.cyber-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.cyber-btn-primary {
  border-color: rgba(0, 204, 255, 0.24);
  color: #f5fbff;
  background:
    linear-gradient(135deg, rgba(255, 170, 0, 0.26), rgba(0, 204, 255, 0.18)),
    rgba(10, 10, 15, 0.88);
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.28), 0 8px 24px rgba(0, 204, 255, 0.18);
}

.cyber-btn-primary:hover:not(:disabled) {
  background:
    linear-gradient(135deg, rgba(255, 170, 0, 0.34), rgba(0, 204, 255, 0.24)),
    rgba(10, 10, 15, 0.92);
  box-shadow: 0 18px 32px rgba(0, 0, 0, 0.34), 0 10px 28px rgba(255, 170, 0, 0.18);
  transform: translateY(-2px);
}

.cyber-btn-secondary {
  border-color: rgba(255, 255, 255, 0.22);
  color: rgba(241, 247, 255, 0.88);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.08);
}

.cyber-btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 6px 16px rgba(255, 255, 255, 0.14);
  transform: translateY(-1px);
}

.cyber-btn-danger {
  border-color: rgba(255, 107, 107, 0.6);
  color: #ffe9e9;
  background:
    linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(255, 77, 109, 0.12)),
    rgba(10, 10, 15, 0.88);
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.28), 0 8px 24px rgba(255, 107, 107, 0.16);
}

.cyber-btn-danger:hover:not(:disabled) {
  background:
    linear-gradient(135deg, rgba(255, 107, 107, 0.28), rgba(255, 77, 109, 0.16)),
    rgba(10, 10, 15, 0.92);
  box-shadow: 0 18px 32px rgba(0, 0, 0, 0.34), 0 10px 28px rgba(255, 107, 107, 0.2);
  transform: translateY(-2px);
}

.qr-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5, 7, 14, 0.78);
  backdrop-filter: blur(18px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 3200;
}

.qr-modal {
  width: min(440px, 100%);
  background: linear-gradient(180deg, rgba(11, 16, 26, 0.96), rgba(6, 9, 18, 0.98));
  border: 1px solid rgba(105, 180, 255, 0.2);
  border-radius: 24px;
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.45);
  padding: 24px;
}

.qr-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.qr-modal-header h3 {
  margin: 0;
  font-size: 22px;
  color: #eef7ff;
}

.qr-modal-header p {
  margin: 6px 0 0;
  color: rgba(222, 236, 255, 0.68);
  font-size: 13px;
  line-height: 1.55;
}

.qr-close-btn {
  border: 0;
  background: transparent;
  color: rgba(255, 255, 255, 0.75);
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
}

.qr-status-pill {
  margin-top: 16px;
  width: fit-content;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  letter-spacing: 0.4px;
  border: 1px solid transparent;
}

.qr-status-pill.is-pending,
.qr-status-pill.is-idle {
  color: #ffe08f;
  background: rgba(255, 191, 73, 0.12);
  border-color: rgba(255, 191, 73, 0.28);
}

.qr-status-pill.is-success {
  color: #77f0b5;
  background: rgba(32, 195, 115, 0.14);
  border-color: rgba(32, 195, 115, 0.32);
}

.qr-status-pill.is-failed {
  color: #ff9c9c;
  background: rgba(255, 77, 109, 0.14);
  border-color: rgba(255, 77, 109, 0.32);
}

.qr-image-panel {
  margin-top: 18px;
  min-height: 280px;
  border-radius: 20px;
  background:
    radial-gradient(circle at top, rgba(100, 170, 255, 0.14), transparent 55%),
    rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.qr-image {
  width: min(260px, 100%);
  aspect-ratio: 1;
  object-fit: contain;
  background: #fff;
  border-radius: 16px;
  padding: 12px;
}

.qr-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: rgba(228, 238, 255, 0.72);
  font-size: 14px;
}

.qr-spinner {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.18);
  border-top-color: #6ab2ff;
  animation: qr-spin 0.9s linear infinite;
}

.qr-hint {
  margin: 16px 0 0;
  color: rgba(233, 240, 255, 0.82);
  line-height: 1.6;
  font-size: 14px;
}

.qr-meta {
  color: rgba(176, 206, 238, 0.7);
  font-size: 12px;
}

.qr-error {
  margin: 12px 0 0;
  color: #ff9c9c;
  font-size: 13px;
}

.qr-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 18px;
}

@keyframes qr-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 760px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .checkbox-group {
    grid-template-columns: 1fr;
  }

  .support-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-actions {
    justify-content: stretch;
  }

  .form-actions .cyber-btn {
    flex: 1;
  }

  .qr-actions {
    flex-direction: column;
  }

  .qr-actions .cyber-btn {
    width: 100%;
  }
}
</style>
