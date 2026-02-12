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
          <select v-model="config.platform" :disabled="isRunning">
            <option v-for="p in platforms" :key="p.value" :value="p.value">
              {{ p.label }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>登录方式</label>
          <select v-model="config.login_type" :disabled="isRunning">
            <option value="qrcode">二维码登录</option>
            <option value="cookie">Cookie 登录</option>
          </select>
        </div>

        <div class="form-group">
          <label>爬取模式</label>
          <select v-model="config.crawler_type" :disabled="isRunning">
            <option value="search">搜索模式</option>
            <option value="detail">详情模式</option>
            <option value="creator">创作者模式</option>
          </select>
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
          <select v-model="config.save_option" :disabled="isRunning">
            <option value="json">JSON</option>
            <option value="csv">CSV</option>
            <option value="excel">Excel</option>
            <option value="db">数据库</option>
          </select>
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
            <input type="checkbox" v-model="config.headless" :disabled="isRunning" />
            无头模式
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

// State
const platforms = ref([])
const status = ref('idle')
const logs = ref([])
const starting = ref(false)
const stopping = ref(false)
const logsContainer = ref(null)
let statusInterval = null

// Config
const config = ref({
  platform: 'xhs',
  login_type: 'qrcode',
  crawler_type: 'search',
  keywords: '',
  specified_ids: '',
  creator_ids: '',
  save_option: 'db',
  start_page: 1,
  enable_comments: true,
  enable_sub_comments: false,
  cookies: '',
  headless: true
})

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
    status.value = res.data.status
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

const scrollToBottom = () => {
  if (logsContainer.value) {
    logsContainer.value.scrollTop = logsContainer.value.scrollHeight
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

    console.log('[前端] 发送启动请求到 /api/crawler/start')
    const response = await axios.post('/api/crawler/start', config.value)
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

const addLog = (message, level = 'info') => {
  logs.value.push({
    id: Date.now(),
    timestamp: new Date().toLocaleTimeString('zh-CN'),
    message,
    level
  })
  nextTick(() => scrollToBottom())
}

// Lifecycle
onMounted(async () => {
  await fetchPlatforms()
  await fetchStatus()
  await fetchLogs()

  // 每2秒轮询状态和日志
  statusInterval = setInterval(async () => {
    await fetchStatus()
    await fetchLogs()
  }, 2000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>

<style scoped>
.crawler-control {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
}

.control-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  background: rgba(22, 27, 34, 0.5);
}

.control-header h2 {
  margin: 0;
  font-size: 1rem;
  color: var(--primary-color);
}

.status-badge {
  padding: 0.25rem 0.6rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-idle {
  background: var(--border-color);
  color: var(--secondary-color);
}

.status-running {
  background: rgba(35, 134, 54, 0.3);
  color: #3fb950;
}

.status-error {
  background: rgba(218, 54, 51, 0.3);
  color: #f85149;
}

.config-form {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 120px;
}

.form-group.full-width {
  flex: 100%;
}

.form-group label {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.75rem;
  color: var(--secondary-color);
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select {
  width: 100%;
  padding: 0.4rem 0.5rem;
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-color);
  font-size: 0.8rem;
}

.form-group input:disabled,
.form-group select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.checkbox-group {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: normal;
  cursor: pointer;
  font-size: 0.8rem;
  margin: 0;
}

.checkbox-group input[type="checkbox"] {
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color);
  margin-top: 0.5rem;
}

.btn {
  padding: 0.5rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-start {
  background: var(--accent-color);
  color: white;
}

.btn-start:hover:not(:disabled) {
  background: #2ea043;
}

.btn-stop {
  background: #da3633;
  color: white;
}

.btn-stop:hover:not(:disabled) {
  background: #f85149;
}

.btn-small {
  padding: 0.25rem 0.5rem;
  background: var(--border-color);
  border: none;
  border-radius: 4px;
  color: var(--text-color);
  font-size: 0.75rem;
  cursor: pointer;
}

.btn-small:hover {
  background: var(--hover-color);
}

.logs-panel {
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.3);
  border-top: 1px solid var(--border-color);
  flex: 1;
  min-height: 200px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: rgba(22, 27, 34, 0.8);
  border-bottom: 1px solid var(--border-color);
}

.logs-header h3 {
  margin: 0;
  font-size: 0.8rem;
  color: var(--secondary-color);
}

.logs-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  max-height: 300px;
}

.log-entry {
  display: flex;
  gap: 0.5rem;
  padding: 0.2rem 0;
  line-height: 1.4;
}

.log-time {
  color: var(--secondary-color);
  flex-shrink: 0;
}

.log-message {
  color: var(--text-color);
  word-break: break-all;
}

.log-entry.info .log-message {
  color: var(--text-color);
}

.log-entry.success .log-message {
  color: #3fb950;
}

.log-entry.warning .log-message {
  color: #d29922;
}

.log-entry.error .log-message {
  color: #f85149;
}

.logs-empty {
  text-align: center;
  padding: 2rem;
  color: var(--secondary-color);
  font-style: italic;
  font-size: 0.8rem;
}
</style>
