<template>
  <div class="crawler-control">
    <div class="control-header">
      <h2>🕷️ 爬虫控制</h2>
      <div class="status-badge" :class="statusClass">
        {{ statusLabel }}
      </div>
    </div>

    <!-- 配置表单 -->
    <div class="config-form">
      <div class="form-row">
        <div class="form-group">
          <label>平台</label>
          <el-select v-model="config.platform" :disabled="isRunning" class="dark-select crawler-select" popper-class="dark-select-dropdown" :teleported="false">
            <el-option v-for="p in platforms" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </div>

        <div class="form-group">
          <label>登录方式</label>
          <el-select v-model="config.login_type" :disabled="isRunning" class="dark-select crawler-select" popper-class="dark-select-dropdown" :teleported="false">
            <el-option label="二维码登录" value="qrcode" />
            <el-option label="Cookie 登录" value="cookie" />
          </el-select>
        </div>

        <div class="form-group">
          <label>爬取模式</label>
          <el-select v-model="config.crawler_type" :disabled="isRunning" class="dark-select crawler-select" popper-class="dark-select-dropdown" :teleported="false">
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
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>保存格式</label>
          <el-select v-model="config.save_option" :disabled="isRunning" class="dark-select crawler-select" popper-class="dark-select-dropdown" :teleported="false">
            <el-option label="JSON" value="json" />
            <el-option label="CSV" value="csv" />
            <el-option label="Excel" value="excel" />
            <el-option label="数据库" value="db" />
          </el-select>
        </div>

        <div class="form-group">
          <label>起始页</label>
          <input
            type="number"
            v-model.number="config.start_page"
            min="1"
            :disabled="isRunning"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group checkbox-group">
          <label>
            <input type="checkbox" v-model="config.enable_comments" :disabled="isRunning" />
            获取评论
          </label>
          <label>
            <input type="checkbox" v-model="config.enable_sub_comments" :disabled="isRunning" />
            子评论
          </label>
          <label>
            <input type="checkbox" v-model="config.headless" :disabled="isRunning || config.login_type === 'qrcode'" />
            无头模式
            <span v-if="config.login_type === 'qrcode'" style="color: #d29922; margin-left: 0.5rem;">(二维码登录时需关闭)</span>
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
          />
        </div>
      </div>

      <div class="form-actions">
        <button
          v-if="!isRunning"
          @click="startCrawler"
          class="btn btn-start"
          :disabled="starting"
        >
          {{ starting ? '启动中...' : '▶ 启动爬虫' }}
        </button>
        <button
          v-else
          @click="stopCrawler"
          class="btn btn-stop"
          :disabled="stopping"
        >
          {{ stopping ? '停止中...' : '⏹ 停止爬虫' }}
        </button>
      </div>
    </div>

    <!-- 日志面板 -->
    <div class="logs-panel">
      <div class="logs-header">
        <h3>运行日志</h3>
        <button @click="clearLogs" class="btn-small">清空</button>
      </div>
      <div class="logs-content" ref="logsContainer">
        <div
          v-for="log in logs"
          :key="log.id"
          class="log-entry"
          :class="log.level"
        >
          <span class="log-time">{{ log.timestamp }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        <div v-if="logs.length === 0" class="logs-empty">暂无日志</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'

// 定义事件
const emit = defineEmits(['crawler-status-change'])

// State
const platforms = ref([])
const status = ref('idle')
const logs = ref([])
const starting = ref(false)
const stopping = ref(false)
const logsContainer = ref(null)
let statusInterval = null
let logsInterval = null

// Computed
const isRunning = computed(() => status.value === 'running')
const statusClass = computed(() => {
  return {
    'status-idle': status.value === 'idle',
    'status-running': status.value === 'running',
    'status-error': status.value === 'error'
  }
})

const statusLabel = computed(() => {
  switch (status.value) {
    case 'idle': return '空闲'
    case 'running': return '运行中'
    case 'error': return '错误'
    default: return '未知'
  }
})

// Config
const config = ref({
  platform: 'xhs',
  login_type: 'qrcode',
  crawler_type: 'search',
  keywords: '',
  specified_ids: '',
  creator_ids: '',
  save_option: 'json',
  start_page: 1,
  enable_comments: true,
  enable_sub_comments: false,
  cookies: '',
  headless: true
})

// Methods
const scrollToBottom = () => {
  if (logsContainer.value) {
    logsContainer.value.scrollTop = logsContainer.value.scrollHeight
  }
}

const addLog = (message, level = 'info') => {
  logs.value.push({
    id: Date.now(),
    timestamp: new Date().toLocaleTimeString('zh-CN'),
    message,
    level
  })
  nextTick(() => scrollToBottom())
}

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

const fetchLogs = async () => {
  try {
    const res = await axios.get('/api/crawler/logs')
    logs.value = res.data.logs || []
    await nextTick()
    scrollToBottom()
  } catch (e) {
    console.error('获取日志失败:', e)
  }
}

const startCrawler = async () => {
  console.log('[前端] 准备启动爬虫，配置:', config.value)
  starting.value = true
  try {
    // 验证输入
    if (config.value.crawler_type === 'search' && !config.value.keywords) {
      addLog('请输入搜索关键词', 'error')
      return
    }
    if (config.value.crawler_type === 'detail' && !config.value.specified_ids) {
      addLog('请输入笔记 ID', 'error')
      return
    }
    if (config.value.crawler_type === 'creator' && !config.value.creator_ids) {
      addLog('请输入创作者 ID', 'error')
      return
    }

    // 二维码登录时强制关闭无头模式，否则用户无法看到二维码
    const requestConfig = { ...config.value }
    if (requestConfig.login_type === 'qrcode') {
      requestConfig.headless = false
      addLog('二维码登录模式已自动开启浏览器窗口', 'info')
    }

    console.log('[前端] 发送启动请求到 /api/crawler/start')
    const response = await axios.post('/api/crawler/start', requestConfig)
    console.log('[前端] 响应:', response.data)
    addLog('爬虫启动成功', 'success')
    await fetchStatus()
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.message
    console.error('[前端] 启动爬虫错误:', e)
    console.error('[前端] 错误响应:', e.response?.data)
    addLog(`启动失败: ${errorMsg}`, 'error')
  } finally {
    starting.value = false
  }
}

const stopCrawler = async () => {
  stopping.value = true
  try {
    await axios.post('/api/crawler/stop')
    addLog('正在停止爬虫...', 'warning')
    await fetchStatus()
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.message
    addLog(`停止失败: ${errorMsg}`, 'error')
    console.error('停止爬虫错误:', e)
  } finally {
    stopping.value = false
  }
}

const clearLogs = () => {
  logs.value = []
}

// Lifecycle
onMounted(async () => {
  await fetchPlatforms()
  await fetchStatus()
  await fetchLogs()

  // 每2秒轮询状态和日志
  statusInterval = setInterval(async () => {
    await fetchStatus()
  }, 2000)

  logsInterval = setInterval(async () => {
    await fetchLogs()
  }, 2000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
  if (logsInterval) {
    clearInterval(logsInterval)
  }
})
</script>

<style scoped>
/* === iOS Style Base === */
.crawler-control {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
}

.control-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 204, 255, 0.15);
  background: linear-gradient(135deg, rgba(0, 204, 255, 0.06), rgba(255, 170, 0, 0.05));
}

.control-header h2 {
  margin: 0;
  font-size: 16px;
  color: #fff;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border: 1px solid;
  transition: all 0.3s ease;
}

.status-idle {
  background: rgba(0, 204, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
  border-color: rgba(0, 204, 255, 0.2);
}

.status-running {
  background: rgba(0, 204, 255, 0.15);
  color: #00ccff;
  border-color: rgba(0, 204, 255, 0.45);
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.3);
  animation: statusPulse 2s ease-in-out infinite;
}

@keyframes statusPulse {
  0%, 100% { box-shadow: 0 0 15px rgba(74, 222, 128, 0.2); }
  50% { box-shadow: 0 0 25px rgba(74, 222, 128, 0.4); }
}

.status-error {
  background: rgba(255, 107, 107, 0.18);
  color: #ff7b7b;
  border-color: rgba(255, 107, 107, 0.45);
  box-shadow: 0 0 15px rgba(255, 107, 107, 0.25);
}

.config-form {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 140px;
}

.form-group.full-width {
  flex: 100%;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select {
  width: 100%;
  padding: 10px 36px 10px 12px;
  background: rgba(0, 204, 255, 0.06);
  border: 1px solid rgba(0, 204, 255, 0.15);
  border-radius: 12px;
  color: #fff;
  font-size: 12px;
  transition: all 0.2s ease;
}

.form-group input[type="text"]:focus,
.form-group input[type="number"]:focus,
.form-group select:focus {
  outline: none;
  border-color: rgba(0, 204, 255, 0.5);
  box-shadow: 0 0 12px rgba(0, 204, 255, 0.25);
  background: rgba(0, 204, 255, 0.1);
}

.form-group input[type="text"]::placeholder,
.form-group input[type="number"]::placeholder {
  color: #8899aa;
}

/* === Dark Select Styles === */
:deep(.dark-select) {
  --el-select-input-focus-border-color: #ffaa00;
  --el-select-border-color-hover: rgba(255, 170, 0, 0.3);
}

:deep(.dark-select .el-select__wrapper) {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: none;
  padding: 4px 12px;
  min-height: 36px;
  transition: all 0.2s ease;
}

:deep(.dark-select .el-select__wrapper:hover) {
  border-color: rgba(255, 170, 0, 0.3);
  background: rgba(255, 255, 255, 0.06);
}

:deep(.dark-select .el-select__wrapper.is-focus) {
  border-color: #ffaa00;
  box-shadow: 0 0 12px rgba(255, 170, 0, 0.25);
}

:deep(.dark-select .el-select__selected-item) {
  color: #fff;
  font-size: 12px;
  line-height: 1.5;
}

:deep(.dark-select .el-select__placeholder) {
  color: #8899aa;
  font-size: 12px;
}

:deep(.dark-select .el-select__suffix) {
  color: #8899aa;
}

:deep(.dark-select.is-focus .el-select__suffix) {
  color: #ffaa00;
}

:deep(.dark-select.is-disabled .el-select__wrapper) {
  opacity: 0.4;
  cursor: not-allowed;
  border-color: rgba(0, 204, 255, 0.12);
}

/* === Dark Select Dropdown Styles === */
:deep(.dark-select-dropdown) {
  background: rgba(26, 29, 38, 0.98);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

:deep(.dark-select-dropdown .el-select-dropdown__item) {
  color: rgba(255, 255, 255, 0.85);
  font-size: 12px;
  padding: 8px 16px;
  transition: all 0.2s ease;
}

:deep(.dark-select-dropdown .el-select-dropdown__item:hover) {
  background: rgba(255, 170, 0, 0.15);
  color: #ffaa00;
}

:deep(.dark-select-dropdown .el-select-dropdown__item.is-selected) {
  background: rgba(255, 170, 0, 0.25);
  color: #ffaa00;
  font-weight: 500;
}

:deep(.dark-select-dropdown .el-select-dropdown__item.is-disabled) {
  color: rgba(255, 255, 255, 0.3);
}

.form-group input:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  border-color: rgba(0, 204, 255, 0.12);
}

.checkbox-group {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  cursor: pointer;
  font-size: 12px;
  margin: 0;
  color: #dbe6f5;
  transition: all 0.2s;
}

.checkbox-group label:hover {
  color: #00ccff;
}

.checkbox-group input[type="checkbox"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
  accent-color: #00ccff;
  border-radius: 4px;
  border: 1px solid rgba(0, 204, 255, 0.3);
  background: rgba(0, 204, 255, 0.08);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 204, 255, 0.12);
  margin-top: 8px;
}

.btn {
  padding: 10px 20px;
  border: 1px solid;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-start {
  background: linear-gradient(135deg, rgba(0, 204, 255, 0.18), rgba(0, 102, 255, 0.1));
  border-color: rgba(0, 204, 255, 0.6);
  color: #e6fbff;
  box-shadow: 0 6px 18px rgba(0, 204, 255, 0.25);
}

.btn-start:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(0, 204, 255, 0.3), rgba(0, 102, 255, 0.2));
  box-shadow: 0 12px 28px rgba(0, 204, 255, 0.4);
  transform: translateY(-2px);
}

.btn-stop {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.22), rgba(255, 55, 95, 0.16));
  border-color: rgba(255, 107, 107, 0.6);
  color: #ffe6e6;
  box-shadow: 0 6px 18px rgba(255, 107, 107, 0.25);
}

.btn-stop:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.35), rgba(255, 55, 95, 0.26));
  box-shadow: 0 12px 28px rgba(255, 107, 107, 0.4);
  transform: translateY(-2px);
}

.btn-small {
  padding: 6px 12px;
  background: rgba(0, 204, 255, 0.08);
  border: 1px solid rgba(0, 204, 255, 0.2);
  border-radius: 10px;
  color: #00ccff;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.btn-small:hover {
  background: rgba(0, 204, 255, 0.18);
  border-color: rgba(0, 204, 255, 0.4);
  box-shadow: 0 0 15px rgba(0, 204, 255, 0.25);
}

.logs-panel {
  display: flex;
  flex-direction: column;
  background: rgba(0, 204, 255, 0.04);
  border-top: 1px solid rgba(0, 204, 255, 0.15);
  flex: 1;
  min-height: 200px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: rgba(0, 204, 255, 0.08);
  border-bottom: 1px solid rgba(0, 204, 255, 0.15);
}

.logs-header h3 {
  margin: 0;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.logs-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  font-family: 'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Code', monospace;
  font-size: 11px;
  max-height: 300px;
  background: rgba(6, 10, 18, 0.65);
}

.log-entry {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  line-height: 1.5;
  border-bottom: 1px solid rgba(0, 204, 255, 0.08);
}

.log-entry:last-child {
  border-bottom: none;
}

.log-time {
  color: #8899aa;
  flex-shrink: 0;
  font-family: 'JetBrains Mono', monospace;
}

.log-message {
  color: #dbe6f5;
  word-break: break-all;
  flex: 1;
}

.log-entry.info .log-message {
  color: #dbe6f5;
}

.log-entry.success .log-message {
  color: #4ade80;
  text-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
}

.log-entry.warning .log-message {
  color: #ffaa00;
  text-shadow: 0 0 10px rgba(255, 170, 0, 0.3);
}

.log-entry.error .log-message {
  color: #ff6b6b;
  text-shadow: 0 0 10px rgba(255, 107, 107, 0.3);
}

.logs-empty {
  text-align: center;
  padding: 32px;
  color: rgba(255, 255, 255, 0.55);
  font-style: italic;
  font-size: 12px;
}

/* Scrollbar for logs panel */
.logs-content::-webkit-scrollbar {
  width: 6px;
}

.logs-content::-webkit-scrollbar-track {
  background: rgba(0, 204, 255, 0.08);
  border-radius: 3px;
}

.logs-content::-webkit-scrollbar-thumb {
  background: rgba(0, 204, 255, 0.3);
  border-radius: 3px;
}

.logs-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 204, 255, 0.5);
}
</style>
