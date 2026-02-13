<template>
  <div class="settings-view">
    <div class="settings-container glass">
      <h3>系统设置</h3>

      <!-- Cookie 管理 -->
      <div class="settings-group">
        <div class="group-header">
          <h4>Cookie 配置管理</h4>
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
        <h4>爬虫配置 (Crawler Config)</h4>
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

      <div class="settings-group">
        <h4>显示设置 (Appearance)</h4>
        <div class="config-item">
          <label>主题色</label>
          <div class="color-picker">
            <div class="color-circle gold active"></div>
            <div class="color-circle blue"></div>
            <div class="color-circle green"></div>
          </div>
        </div>
        <div class="config-item">
          <label>呼吸动画</label>
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

    <!-- 添加/编辑 Cookie 弹窗 -->
    <div v-if="showAddModal || showEditModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal glass">
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
.settings-view {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.settings-container {
  padding: 2rem;
  border-radius: 12px;
}

.settings-container h3 {
  margin: 0 0 2rem 0;
  color: var(--primary-color);
  font-size: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
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

.settings-group h4 {
  margin: 0;
  color: var(--text-color);
  font-weight: 600;
}

/* Cookie 列表 */
.cookie-list {
  min-height: 100px;
}

.loading, .empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--secondary-color);
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
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.3s;
}

.cookie-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.cookie-item.active {
  border-color: var(--primary-color);
  box-shadow: 0 0 10px rgba(255, 215, 0, 0.1);
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

.platform-xhs { background: rgba(255, 60, 60, 0.2); color: #FF3C3C; }
.platform-dy { background: rgba(0, 0, 0, 0.3); color: #fff; }
.platform-ks { background: rgba(255, 100, 0, 0.2); color: #FF6400; }
.platform-bili { background: rgba(0, 160, 233, 0.2); color: #00A0E9; }
.platform-wb { background: rgba(230, 57, 71, 0.2); color: #E63947; }
.platform-tieba { background: rgba(0, 122, 255, 0.2); color: #007AFF; }
.platform-zhihu { background: rgba(0, 153, 153, 0.2); color: #009999; }

.cookie-name {
  color: var(--text-color);
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
  border: 1px solid var(--border-color);
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.1);
}

.btn-icon.danger:hover {
  background: rgba(255, 68, 68, 0.2);
  border-color: #FF4444;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  width: 90%;
  max-width: 500px;
  padding: 2rem;
  border-radius: 12px;
}

.modal h3 {
  margin: 0 0 1.5rem 0;
  color: var(--primary-color);
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
  color: var(--text-color);
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  padding: 0.8rem;
  border-radius: 6px;
  color: var(--text-color);
  font-size: 0.9rem;
}

.form-group textarea {
  resize: vertical;
  font-family: monospace;
}

.form-group small {
  color: var(--secondary-color);
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

/* Buttons */
.btn-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  color: #000;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
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
  color: var(--text-color);
  border: 1px solid var(--border-color);
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 原有样式 */
.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.config-item label {
  color: var(--secondary-color);
}

.config-item input[type="number"] {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  padding: 0.5rem;
  border-radius: 4px;
  color: var(--text-color);
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
  background-color: var(--primary-color);
}

input:focus + .slider {
  box-shadow: 0 0 1px var(--primary-color);
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

.color-picker {
  display: flex;
  gap: 0.5rem;
}

.color-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
}

.color-circle.gold { background: #FFD700; }
.color-circle.blue { background: #00BFFF; }
.color-circle.green { background: #32CD32; }

.color-circle.active {
  border-color: white;
  box-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 2rem;
}
</style>
