<template>
  <div class="crawler-control">
    <!-- 配置表单 -->
    <div class="config-form">
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
            <el-option label="二维码登录" value="qrcode" />
            <el-option label="Cookie 登录" value="cookie" />
          </el-select>
        </div>

        <div class="form-group">
          <label>爬取模式</label>
          <el-select v-model="config.crawler_type" :disabled="isRunning" class="crawler-select" popper-class="crawler-dropdown" :teleported="false">
            <el-option label="搜索模式" value="search" />
            <el-option label="详情模式" value="detail" />
            <el-option label="创作者模式" value="creator" />
          </el-select>
        </div>
      </div>

      <!-- 根据爬取模式显示不同字段 -->
      <div class="form-row" v-if="config.crawler_type === 'search'">
        <div class="form-group full-width">
          <label>搜索关键词（逗号分隔）</label>
          <input
            type="text"
            v-model="config.keywords"
            placeholder="美食,旅游,科技"
            :disabled="isRunning"
            class="cyber-input"
          />
        </div>
      </div>

      <div class="form-row" v-else-if="config.crawler_type === 'detail'">
        <div class="form-group full-width">
          <label>笔记 ID（逗号分隔）</label>
          <input
            type="text"
            v-model="config.specified_ids"
            placeholder="12345678,87654321"
            :disabled="isRunning"
            class="cyber-input"
          />
        </div>
      </div>

      <div class="form-row" v-else-if="config.crawler_type === 'creator'">
        <div class="form-group full-width">
          <label>创作者 ID（逗号分隔）</label>
          <input
            type="text"
            v-model="config.creator_ids"
            placeholder="user123,user456"
            :disabled="isRunning"
            class="cyber-input"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group checkbox-group">
          <label class="cyber-checkbox">
            <input type="checkbox" v-model="config.enable_comments" :disabled="isRunning" />
            <span>获取评论</span>
          </label>
          <label class="cyber-checkbox">
            <input type="checkbox" v-model="config.enable_sub_comments" :disabled="isRunning" />
            <span>子评论</span>
          </label>
          <label class="cyber-checkbox">
            <input type="checkbox" v-model="config.headless" :disabled="isRunning || config.login_type === 'qrcode'" />
            <span>无头模式</span>
            <span v-if="config.login_type === 'qrcode'" class="warning-hint">(二维码登录时需关闭)</span>
          </label>
        </div>
      </div>

      <div class="form-row" v-if="config.login_type === 'cookie'">
        <div class="form-group full-width">
          <label>Cookies（可选）</label>
          <input
            type="text"
            v-model="config.cookies"
            placeholder="a1=xxx; a2=yyy"
            :disabled="isRunning"
            class="cyber-input"
          />
        </div>
      </div>

      <div class="form-actions">
        <button
          v-if="!isRunning"
          @click="startCrawler"
          class="cyber-btn cyber-btn-primary"
          :disabled="starting"
        >
          {{ starting ? '启动中...' : '启动' }}
        </button>
        <button
          v-else
          @click="stopCrawler"
          class="cyber-btn cyber-btn-danger"
          :disabled="stopping"
        >
          {{ stopping ? '停止中...' : '停止' }}
        </button>
      </div>
    </div>

    <div v-if="qrModal.visible" class="qr-modal-overlay" @click.self="closeQrModal">
      <div class="qr-modal">
        <div class="qr-modal-header">
          <div>
            <h3>扫码登录</h3>
            <p>{{ qrModal.platformLabel }} 登录会话</p>
          </div>
          <button type="button" class="qr-close-btn" @click="closeQrModal">×</button>
        </div>

        <div class="qr-status-pill" :class="`is-${qrModal.status}`">
          {{ getQrStatusLabel(qrModal.status) }}
        </div>

        <div class="qr-image-panel">
          <img v-if="qrModal.imageUrl" :src="qrModal.imageUrl" :alt="`${qrModal.platformLabel} 登录二维码`" class="qr-image" />
          <div v-else class="qr-placeholder">
            <span class="qr-spinner"></span>
            <span>等待二维码生成...</span>
          </div>
        </div>

        <p class="qr-hint">
          {{ qrModal.status === 'success' ? '登录成功，爬虫会继续执行。' : qrModal.status === 'failed' ? '登录失败，请关闭后重试。' : '请使用对应平台 App 扫码确认登录。' }}
        </p>

        <p v-if="qrModal.error" class="qr-error">{{ qrModal.error }}</p>

        <div class="qr-actions">
          <button type="button" class="cyber-btn cyber-btn-secondary" @click="refreshQrState">
            刷新
          </button>
          <button type="button" class="cyber-btn cyber-btn-primary" @click="closeQrModal">
            {{ qrModal.status === 'success' ? '完成' : '关闭' }}
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
let statusInterval = null
let qrInterval = null

// Computed
const isRunning = computed(() => status.value === 'running')

// Config
const config = ref({
  platform: 'xhs',
  login_type: 'qrcode',
  crawler_type: 'search',
  keywords: '',
  specified_ids: '',
  creator_ids: '',
  enable_comments: false,
  enable_sub_comments: false,
  cookies: '',
  headless: true
})

const platformLabels = {
  xhs: '小红书',
  dy: '抖音',
  ks: '快手',
  bili: 'B站',
  wb: '微博',
  tieba: '贴吧',
  zhihu: '知乎'
}

const qrModal = ref({
  visible: false,
  platform: '',
  platformLabel: '',
  status: 'idle',
  imageUrl: '',
  error: ''
})

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

// Methods
const fetchPlatforms = async () => {
  try {
    const res = await axios.get('/api/config/platforms')
    platforms.value = res.data.platforms
  } catch (e) {
    console.error('获取平台列表失败:', e)
  }
}

const fetchStatus = async () => {
  try {
    const res = await axios.get('/api/crawler/status')
    const newStatus = res.data.status

    // 只有状态变化时才通知父组件
    if (status.value !== newStatus) {
      status.value = newStatus
      emit('crawler-status-change', newStatus)
    }
  } catch (e) {
    console.error('获取状态失败:', e)
  }
}

const stopQrPolling = () => {
  if (qrInterval) {
    clearInterval(qrInterval)
    qrInterval = null
  }
}

const resetQrModal = () => {
  qrModal.value = {
    visible: false,
    platform: '',
    platformLabel: '',
    status: 'idle',
    imageUrl: '',
    error: ''
  }
}

const openQrModal = (platform) => {
  qrModal.value = {
    visible: true,
    platform,
    platformLabel: platformLabels[platform] || platform,
    status: 'pending',
    imageUrl: '',
    error: ''
  }
}

const closeQrModal = () => {
  stopQrPolling()
  resetQrModal()
}

const getQrStatusLabel = (statusValue) => {
  const labels = {
    idle: '待启动',
    pending: '等待扫码',
    success: '登录成功',
    failed: '登录失败'
  }
  return labels[statusValue] || '等待扫码'
}

const refreshQrState = async () => {
  const platform = qrModal.value.platform
  if (!platform) return

  try {
    const [qrRes, statusRes] = await Promise.all([
      axios.get(`/api/login/qr/${platform}`),
      axios.get(`/api/login/qr/${platform}/status`)
    ])

    qrModal.value.imageUrl = qrRes.data?.qr_code || ''
    qrModal.value.status = statusRes.data?.status || 'pending'
    qrModal.value.error = ''

    if (qrModal.value.status === 'success' || qrModal.value.status === 'failed') {
      stopQrPolling()
    }
  } catch (e) {
    qrModal.value.error = e.response?.data?.error || e.message || '二维码状态获取失败'
  }
}

const startQrPolling = async (platform) => {
  stopQrPolling()
  openQrModal(platform)
  await refreshQrState()
  qrInterval = setInterval(async () => {
    await refreshQrState()
  }, 2000)
}

const startCrawler = async () => {
  console.log('[前端] 准备启动爬虫，配置:', config.value)
  starting.value = true
  try {
    // 验证输入
    if (config.value.crawler_type === 'search' && !config.value.keywords) {
      console.warn('请输入搜索关键词')
      return
    }
    if (config.value.crawler_type === 'detail' && !config.value.specified_ids) {
      console.warn('请输入笔记 ID')
      return
    }
    if (config.value.crawler_type === 'creator' && !config.value.creator_ids) {
      console.warn('请输入创作者 ID')
      return
    }

    // 构建请求配置，添加默认值
    const requestConfig = {
      ...config.value,
      save_option: 'db',  // 默认保存到数据库
      start_page: 1       // 默认从第1页开始
    }

    // 二维码登录时强制关闭无头模式，否则用户无法看到二维码
    if (requestConfig.login_type === 'qrcode') {
      requestConfig.headless = true
      console.log('[前端] 二维码登录模式走无头浏览器，由 Web QR bridge 提供二维码')
      openQrModal(requestConfig.platform)
    }

    emit('platform-change', requestConfig.platform)
    console.log('[前端] 发送启动请求到 /api/crawler/start')
    const response = await axios.post('/api/crawler/start', requestConfig)
    console.log('[前端] 响应:', response.data)
    if (requestConfig.login_type === 'qrcode') {
      await startQrPolling(requestConfig.platform)
    }
    await fetchStatus()
  } catch (e) {
    const errorMsg = e.response?.data?.error || e.response?.data?.detail || e.message
    console.error('[前端] 启动爬虫错误:', e)
    console.error('[前端] 错误响应:', e.response?.data)
    if (config.value.login_type === 'qrcode') {
      qrModal.value.error = errorMsg
      qrModal.value.status = 'failed'
      stopQrPolling()
    }
    window.alert(`启动爬虫失败: ${errorMsg}`)
  } finally {
    starting.value = false
  }
}

const stopCrawler = async () => {
  stopping.value = true
  try {
    await axios.post('/api/crawler/stop')
    console.log('[前端] 正在停止爬虫...')
    await fetchStatus()
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.message
    console.error('停止爬虫错误:', e)
  } finally {
    stopping.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await fetchPlatforms()
  await fetchStatus()

  // 每2秒轮询状态
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
/* === 赛博朋克科技风格 === */
.crawler-control {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  color: #fff;
}

.config-form {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
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
  z-index: 2100;
}

.qr-modal {
  width: min(420px, 100%);
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

.form-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 130px;
}

.form-group.full-width {
  flex: 100%;
}

.form-group > label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* === Cyberpunk Input === */
.cyber-input {
  width: 100%;
  padding: 8px 12px;
  background: var(--app-surface, rgba(10, 10, 15, 0.85));
  border: 1px solid var(--app-glass-border, rgba(0, 204, 255, 0.2));
  border-radius: var(--app-radius, 12px);
  color: #fff;
  font-size: 13px;
  transition: all 0.15s ease;
}

.cyber-input:focus {
  outline: none;
  border-color: var(--app-accent, #ffae00);
  box-shadow: 0 0 12px rgba(255, 174, 0, 0.2);
  background: var(--app-surface-hover, rgba(20, 20, 30, 0.9));
}

.cyber-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.cyber-input:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  border-color: rgba(255, 255, 255, 0.08);
}

/* === Cyberpunk Select === */
:deep(.crawler-select .el-select__wrapper) {
  background: var(--app-surface, rgba(10, 10, 15, 0.85));
  border: 1px solid var(--app-glass-border, rgba(0, 204, 255, 0.2));
  border-radius: var(--app-radius, 12px);
  box-shadow: none;
  padding: 6px 12px;
  min-height: 34px;
  transition: all 0.15s ease;
}

:deep(.crawler-select .el-select__wrapper:hover) {
  border-color: rgba(255, 174, 0, 0.3);
  background: var(--app-surface-hover, rgba(20, 20, 30, 0.9));
}

:deep(.crawler-select .el-select__wrapper.is-focus) {
  border-color: var(--app-accent, #ffae00);
  box-shadow: 0 0 12px rgba(255, 174, 0, 0.2);
}

:deep(.crawler-select .el-select__selected-item) {
  color: #fff;
  font-size: 13px;
  line-height: 1.4;
}

:deep(.crawler-select .el-select__placeholder) {
  color: rgba(255, 255, 255, 0.35);
  font-size: 13px;
}

:deep(.crawler-select .el-select__suffix) {
  color: rgba(255, 255, 255, 0.5);
}

:deep(.crawler-select.is-focus .el-select__suffix) {
  color: var(--app-accent, #ffae00);
}

:deep(.crawler-select.is-disabled .el-select__wrapper) {
  opacity: 0.4;
  cursor: not-allowed;
  border-color: rgba(255, 255, 255, 0.08);
}

/* === Cyberpunk Dropdown === */
:deep(.crawler-dropdown) {
  background: rgba(20, 25, 35, 0.75) !important;
  backdrop-filter: blur(40px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(40px) saturate(180%) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 20px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
  z-index: 9999 !important;
  position: absolute !important;
}

:deep(.crawler-dropdown .el-select-dropdown__list) {
  background: transparent !important;
  padding: 6px 8px !important;
}

:deep(.crawler-dropdown .el-select-dropdown__item) {
  color: #8da0b7 !important;
  font-size: 13px !important;
  height: 36px !important;
  line-height: 36px !important;
  margin: 1px 4px !important;
  border-radius: 8px !important;
  padding: 0 12px !important;
  transition: all 0.15s ease !important;
  cursor: pointer !important;
}

:deep(.crawler-dropdown .el-select-dropdown__item:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #ffffff !important;
}

:deep(.crawler-dropdown .el-select-dropdown__item.is-selected) {
  background: rgba(255, 174, 0, 0.15) !important;
  color: #ffae00 !important;
  font-weight: 500 !important;
}

:deep(.crawler-dropdown .el-select-dropdown__item.is-disabled) {
  color: rgba(255, 255, 255, 0.2) !important;
  cursor: not-allowed !important;
}

/* === Checkbox === */
.checkbox-group {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.cyber-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  margin: 0;
  color: #fff;
  transition: all 0.15s ease;
  user-select: none;
}

.cyber-checkbox:hover {
  color: var(--app-accent, #ffae00);
}

.cyber-checkbox input[type="checkbox"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
  accent-color: var(--app-accent, #ffae00);
  border-radius: 4px;
  border: 1px solid var(--app-glass-border, rgba(0, 204, 255, 0.2));
  background: var(--app-surface, rgba(10, 10, 15, 0.85));
}

.warning-hint {
  color: var(--app-accent, #ffae00);
  font-size: 11px;
  margin-left: 4px;
}

/* === Actions === */
.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px solid var(--app-glass-border, rgba(0, 204, 255, 0.15));
  margin-top: 4px;
}

.cyber-btn {
  padding: 9px 20px;
  border: 1px solid;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.3px;
  background: var(--app-surface, rgba(10, 10, 15, 0.85));
}

.cyber-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.cyber-btn-primary {
  border-color: var(--app-primary, #00ccff);
  color: var(--app-primary, #00ccff);
  box-shadow: 0 4px 12px rgba(0, 204, 255, 0.15);
}

.cyber-btn-primary:hover:not(:disabled) {
  background: rgba(0, 204, 255, 0.12);
  box-shadow: 0 6px 16px rgba(0, 204, 255, 0.25);
  transform: translateY(-1px);
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
  color: rgba(255, 107, 107, 0.9);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.15);
}

.cyber-btn-danger:hover:not(:disabled) {
  background: rgba(255, 107, 107, 0.12);
  box-shadow: 0 6px 16px rgba(255, 107, 107, 0.25);
  transform: translateY(-1px);
}

/* === Scrollbar === */
.crawler-control::-webkit-scrollbar {
  width: 4px;
}

.crawler-control::-webkit-scrollbar-track {
  background: transparent;
}

.crawler-control::-webkit-scrollbar-thumb {
  background: rgba(0, 204, 255, 0.3);
  border-radius: 2px;
}

.crawler-control::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 204, 255, 0.5);
}
</style>
