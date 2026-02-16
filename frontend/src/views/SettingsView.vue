<template>
    <div class="settings-wrapper">
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

    <div class="settings-view">
      <header class="page-header entrance-slide-in">
        <div class="title-area">
          <h1 class="ios-title">系统设置<span class="subtitle">System Settings</span></h1>
        </div>
      </header>

      <div class="settings-container ios-glass entrance-scale-up">
        <div class="border-glow"></div>
        <!-- Cookie 管理 -->
        <div class="settings-group">
          <div class="group-header">
            <div class="group-title">
              <span class="accent-bar"></span>
              <h4>Cookie 配置管理</h4>
            </div>
            <button class="btn-secondary" @click="openAddModal">+ 添加配置</button>
          </div>

          <div class="cookie-list">
            <div v-if="loading" class="loading">加载中...</div>
            <div v-else-if="cookies.length === 0" class="empty-state">暂无 Cookie 配置</div>
            <div v-else class="cookie-items">
              <div v-for="cookie in cookies" :key="cookie.id" class="cookie-item" :class="{ active: cookie.is_active }">
                <div class="cookie-info">
                  <span class="platform-badge" :class="'platform-' + cookie.platform">{{ cookie.platform_display }}</span>
                  <span class="cookie-name">{{ cookie.name }}</span>
                  <span v-if="!cookie.is_valid" class="invalid-badge">无效</span>
                </div>
                <div class="cookie-actions">
                  <button class="btn-icon" @click="editCookie(cookie)" title="编辑">✏️</button>
                  <button class="btn-icon" @click="toggleActive(cookie)" :title="cookie.is_active ? '禁用' : '启用'">
                    {{ cookie.is_active ? '🔒' : '🔓' }}
                  </button>
                  <button class="btn-icon danger" @click="deleteCookie(cookie)" title="删除">🗑️</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="settings-group">
          <div class="group-title">
            <span class="accent-bar"></span>
            <h4>爬虫配置 (Crawler Config)</h4>
          </div>
          <div class="config-item">
            <label>并发线程数</label>
            <input type="number" value="4" />
          </div>
          <div class="config-item">
            <label>请求间隔 (ms)</label>
            <input type="number" value="1000" />
          </div>
          <div class="config-item">
            <label>包含图片下载</label>
            <label class="switch">
              <input type="checkbox" checked>
              <span class="slider round"></span>
            </label>
          </div>
        </div>

        <div class="actions">
          <button class="btn-primary">保存配置</button>
        </div>
      </div>

      <div v-if="showAddModal || showEditModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal ios-glass">
          <div class="border-glow purple-tint"></div>
          <h3>{{ showEditModal ? '编辑 Cookie 配置' : '添加 Cookie 配置' }}</h3>
          <form @submit.prevent="saveCookie" class="cookie-form">
            <div class="form-group">
              <label>平台 *</label>
              <select v-model="formData.platform" required>
                <option value="">请选择平台</option>
                <option value="xhs">小红书</option>
                <option value="dy">抖音</option>
                <option value="ks">快手</option>
                <option value="bili">哔哩哔哩</option>
                <option value="wb">微博</option>
                <option value="tieba">百度贴吧</option>
                <option value="zhihu">知乎</option>
              </select>
            </div>
            <div class="form-group">
              <label>配置名称 *</label>
              <input v-model="formData.name" type="text" placeholder="如: 账号1" required />
            </div>
            <div class="form-group">
              <label>Cookie 字符串 *</label>
              <textarea v-model="formData.cookies" rows="5" placeholder="格式: key1=value1;key2=value2" required></textarea>
              <small>格式: key1=value1;key2=value2</small>
            </div>
            <div class="form-group">
              <label>备注</label>
              <input v-model="formData.remark" type="text" placeholder="可选备注信息" />
            </div>
            <div class="form-group checkbox-group">
              <label>
                <input v-model="formData.is_active" type="checkbox" />
                <span>启用此配置</span>
              </label>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeModal">取消</button>
              <button type="submit" class="btn-primary">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_BASE = 'http://localhost:8000/api'

const cookies = ref([])
const loading = ref(false)
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingId = ref(null)

const formData = ref({
  platform: '',
  name: '',
  cookies: '',
  remark: '',
  is_active: true
})

const openAddModal = () => {
  showAddModal.value = true
}

const fetchCookies = async () => {
  loading.value = true
  try {
    const response = await fetch(`${API_BASE}/cookies`)
    const data = await response.json()
    cookies.value = data.cookies || []
  } catch (error) {
    console.error('获取 Cookie 列表失败:', error)
    alert('获取 Cookie 列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const saveCookie = async () => {
  try {
    const url = showEditModal.value
      ? `${API_BASE}/cookies/${editingId.value}/update`
      : `${API_BASE}/cookies/create`

    const method = showEditModal.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData.value)
    })

    const result = await response.json()

    if (response.ok) {
      closeModal()
      await fetchCookies()
      alert('保存成功')
    } else {
      alert('保存失败: ' + (result.error || '未知错误'))
    }
  } catch (error) {
    console.error('保存 Cookie 失败:', error)
    alert('保存 Cookie 失败: ' + error.message)
  }
}

const editCookie = (cookie) => {
  editingId.value = cookie.id
  formData.value = {
    platform: cookie.platform,
    name: cookie.name,
    cookies: cookie.cookies,
    remark: cookie.remark || '',
    is_active: cookie.is_active
  }
  showEditModal.value = true
  showAddModal.value = false
}

const toggleActive = async (cookie) => {
  try {
    const response = await fetch(`${API_BASE}/cookies/${cookie.id}/toggle`, { method: 'POST' })
    if (response.ok) {
      await fetchCookies()
    } else {
      alert('切换状态失败')
    }
  } catch (error) {
    console.error('切换状态失败:', error)
    alert('切换状态失败: ' + error.message)
  }
}

const deleteCookie = async (cookie) => {
  if (!confirm(`确定要删除 "${cookie.name}" 吗？`)) return

  try {
    const response = await fetch(`${API_BASE}/cookies/${cookie.id}/delete`, { method: 'DELETE' })
    if (response.ok) {
      await fetchCookies()
    } else {
      alert('删除失败')
    }
  } catch (error) {
    console.error('删除 Cookie 失败:', error)
    alert('删除 Cookie 失败: ' + error.message)
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  editingId.value = null
  formData.value = {
    platform: '',
    name: '',
    cookies: '',
    remark: '',
    is_active: true
  }
}

onMounted(() => {
  fetchCookies()
})
</script>

<style scoped>
.settings-wrapper {
  min-height: 100vh;
  background: #050510;
  position: relative;
  overflow: hidden;
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
}

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

.settings-view {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  padding: 32px 40px 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
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

.ios-glass > :not(.border-glow) {
  position: relative;
  z-index: 1;
}

.ios-glass:hover {
  transform: scale(1.01) translateY(-1px);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8),
              0 0 30px rgba(255, 204, 0, 0.12),
              0 0 60px rgba(255, 204, 0, 0.06);
}

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

.border-glow.purple-tint {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.55), transparent 45%, rgba(168, 85, 247, 0.15));
}

@keyframes borderBreathe {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; box-shadow: inset 0 0 15px rgba(255, 170, 0, 0.2); }
}

.entrance-slide-in {
  animation: slideInFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
  transform: translateX(-40px);
}

.entrance-scale-up {
  animation: scaleUpFade 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}

@keyframes slideInFade {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleUpFade {
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.settings-container {
  padding: 24px;
  width: min(980px, 100%);
  margin: 0 auto;
}

.settings-group {
  margin-bottom: 2rem;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.group-title h4 {
  margin: 0;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 600;
}

.accent-bar {
  width: 4px;
  height: 18px;
  border-radius: 999px;
  background: linear-gradient(180deg, #ffaa00, #ff6a00);
}

.cookie-list {
  min-height: 100px;
}

.loading, .empty-state {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.55);
}

.cookie-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cookie-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s;
}

.cookie-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.cookie-item.active {
  border-color: rgba(255, 170, 0, 0.5);
  box-shadow: 0 0 10px rgba(255, 215, 0, 0.12);
}

.cookie-info {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.platform-badge {
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.platform-xhs { background: rgba(255, 100, 0, 0.2); color: #FF6400; }
.platform-dy { background: rgba(255, 100, 0, 0.2); color: #FF6400; }
.platform-ks { background: rgba(255, 100, 0, 0.2); color: #FF6400; }
.platform-bili { background: rgba(255, 100, 0, 0.2); color: #FF6400; }
.platform-wb { background: rgba(255, 100, 0, 0.2); color: #FF6400; }
.platform-tieba { background: rgba(255, 100, 0, 0.2); color: #FF6400; }
.platform-zhihu { background: rgba(255, 100, 0, 0.2); color: #FF6400; }

.cookie-name {
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
}

.invalid-badge {
  padding: 0.2rem 0.5rem;
  background: rgba(255, 0, 0, 0.2);
  color: #FF4444;
  border-radius: 4px;
  font-size: 0.75rem;
}

.cookie-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
  color: rgba(255, 255, 255, 0.8);
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.btn-icon.danger:hover {
  background: rgba(255, 68, 68, 0.2);
  border-color: #FF4444;
  color: #FFBBBB;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(6, 8, 14, 0.7);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  width: 90%;
  max-width: 520px;
  padding: 2rem;
}

.modal h3 {
  margin: 0 0 1.5rem 0;
  color: rgba(255, 255, 255, 0.9);
}

.cookie-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0.8rem;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.9rem;
}

.form-group textarea {
  resize: vertical;
  font-family: monospace;
}

.form-group small {
  color: rgba(255, 255, 255, 0.45);
  font-size: 0.8rem;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #ffaa00, #ff6a00);
  color: #000;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 215, 0, 0.3);
}

.btn-secondary {
  background: transparent;
  color: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.6rem 1.2rem;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.config-item label {
  color: rgba(255, 255, 255, 0.6);
}

.config-item input[type="number"] {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.85);
  width: 100px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #333;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
}

input:checked + .slider {
  background-color: #ffaa00;
}

input:focus + .slider {
  box-shadow: 0 0 1px rgba(255, 170, 0, 0.8);
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 2rem;
}
</style>
