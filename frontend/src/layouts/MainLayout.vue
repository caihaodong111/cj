<template>
  <div class="main-layout">
    <!-- Trigger Zone -->
    <div
      class="sidebar-trigger"
      @mouseenter="showSidebar"
      @mouseleave="hideSidebar"
    >
      <div class="trigger-indicator">
        <span class="trigger-dots">···</span>
      </div>
    </div>

    <!-- Sidebar -->
    <aside
      class="sidebar"
      :class="{ 'sidebar-visible': isSidebarVisible }"
      @mouseenter="showSidebar"
      @mouseleave="hideSidebar"
    >
      <div class="logo">
        <h1>舆镜</h1>
      </div>

      <nav class="nav-menu">
        <router-link to="/dashboard" class="nav-item" active-class="active">
          <span class="icon">◉</span>
          <span class="label">舆情监测总览</span>
        </router-link>
        <router-link to="/data" class="nav-item" active-class="active">
          <span class="icon">▤</span>
          <span class="label">数据源概览</span>
        </router-link>
        <router-link to="/analysis" class="nav-item" active-class="active">
          <span class="icon">🔍</span>
          <span class="label">深度分析</span>
        </router-link>
        <router-link to="/settings" class="nav-item" active-class="active">
          <span class="icon">⚙️</span>
          <span class="label">系统设置</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="version">v1.0.1 Beta</div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="main-content-layout">
      <main class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const isSidebarVisible = ref(false)
let hideTimer = null

const showSidebar = () => {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
  isSidebarVisible.value = true
}

const hideSidebar = () => {
  if (hideTimer) {
    clearTimeout(hideTimer)
  }
  hideTimer = setTimeout(() => {
    isSidebarVisible.value = false
  }, 200)
}
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: radial-gradient(circle at top right, rgba(0, 204, 255, 0.08), transparent 50%),
              radial-gradient(circle at bottom left, rgba(255, 170, 0, 0.05), transparent 50%);
  position: relative;
}

/* Trigger Zone */
.sidebar-trigger {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 8px;
  z-index: 5;
  cursor: pointer;
}

.trigger-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60px;
  background: linear-gradient(180deg, transparent, var(--app-primary), transparent);
  border-radius: 0 4px 4px 0;
  opacity: 0.3;
  transition: opacity 0.3s, width 0.3s, box-shadow 0.3s;
  box-shadow: 0 0 10px rgba(0, 204, 255, 0.3);
}

.sidebar-trigger:hover .trigger-indicator {
  opacity: 0.9;
  width: 6px;
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.6);
}

.trigger-dots {
  display: none;
  position: absolute;
  left: 6px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--app-primary);
  font-size: 14px;
  letter-spacing: 1px;
  writing-mode: vertical-rl;
  text-orientation: upright;
  text-shadow: 0 0 10px rgba(0, 204, 255, 0.5);
}

.sidebar-trigger:hover .trigger-dots {
  display: block;
}

/* Sidebar */
.sidebar {
  width: 240px;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, rgba(10, 12, 18, 0.98) 0%, rgba(8, 10, 16, 0.98) 100%);
  border-right: 1px solid rgba(0, 204, 255, 0.2);
  z-index: 10;
  transform: translateX(-100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  box-shadow: 0 0 40px rgba(0, 102, 255, 0.15), 0 20px 40px rgba(0, 0, 0, 0.5);
}

.sidebar.sidebar-visible {
  transform: translateX(0);
}

.logo {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo h1 {
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--app-primary);
  letter-spacing: 8px;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  background: linear-gradient(135deg, #00ccff 0%, #0099ff 50%, #00ccff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 20px rgba(0, 204, 255, 0.6))
          drop-shadow(0 0 40px rgba(0, 204, 255, 0.4));
  animation: titleGlow 3s ease-in-out infinite alternate;
}

@keyframes titleGlow {
  0% {
    filter: drop-shadow(0 0 20px rgba(0, 204, 255, 0.6))
            drop-shadow(0 0 40px rgba(0, 204, 255, 0.4));
  }
  100% {
    filter: drop-shadow(0 0 30px rgba(0, 204, 255, 0.8))
            drop-shadow(0 0 60px rgba(0, 204, 255, 0.6));
  }
}

.nav-menu {
  flex: 1;
  padding: 1.5rem 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem 1rem;
  border-radius: var(--app-radius);
  color: var(--app-text);
  transition: all 0.2s ease;
  border: 1px solid transparent;
  text-decoration: none;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--app-primary);
  transform: scaleY(0);
  transition: transform 0.2s ease;
}

.nav-item:hover {
  background: var(--app-surface-hover);
  color: #fff;
  transform: translateX(4px);
  border-color: rgba(0, 204, 255, 0.15);
  box-shadow: 0 0 20px rgba(0, 204, 255, 0.1);
}

.nav-item:hover::before {
  transform: scaleY(1);
}

.nav-item.active {
  background: rgba(255, 170, 0, 0.12);
  color: var(--app-accent);
  border-color: rgba(255, 170, 0, 0.3);
  box-shadow: 0 0 25px rgba(255, 170, 0, 0.15);
  text-shadow: 0 0 10px rgba(255, 170, 0, 0.3);
}

.nav-item.active::before {
  background: var(--app-accent);
  transform: scaleY(1);
}

.nav-item .icon {
  font-size: 1.4rem;
  transition: transform 0.2s ease;
  filter: drop-shadow(0 0 8px rgba(0, 204, 255, 0.3));
}

.nav-item:hover .icon {
  transform: scale(1.15);
  filter: drop-shadow(0 0 12px rgba(0, 204, 255, 0.5));
}

.nav-item.active .icon {
  filter: drop-shadow(0 0 12px rgba(255, 170, 0, 0.5));
}

.nav-item .label {
  font-weight: 600;
  letter-spacing: 2px;
  font-size: 0.95rem;
}

.sidebar-footer {
  padding: 1.2rem;
  text-align: center;
  color: var(--app-muted);
  font-size: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  letter-spacing: 1px;
}

.sidebar-footer .version {
  background: rgba(0, 204, 255, 0.08);
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  border: 1px solid rgba(0, 204, 255, 0.15);
  display: inline-block;
}

.main-content-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: 100%;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  position: relative;
}

/* Page Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Scrollbar for content */
.content-wrapper::-webkit-scrollbar {
  width: 6px;
}

.content-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.content-wrapper::-webkit-scrollbar-thumb {
  background: rgba(0, 204, 255, 0.2);
  border-radius: 3px;
}

.content-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 204, 255, 0.4);
}
</style>
