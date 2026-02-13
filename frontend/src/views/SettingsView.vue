<template>
  <div class="settings-view">
    <div class="settings-container glass">
      <h3>系统设置</h3>
      
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
  </div>
</template>

<script setup>
</script>

<style scoped>
.settings-view {
  padding: 2rem;
  max-width: 800px;
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

.settings-group h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-weight: 600;
}

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

/* Switch Toggle */
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

/* Color Picker */
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
