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
      class="sidebar glass"
      :class="{ 'sidebar-visible': isSidebarVisible }"
      @mouseenter="showSidebar"
      @mouseleave="hideSidebar"
    >
      <div class="logo">
        <span class="logo-icon">🕷️</span>
        <h1>舆情分析</h1>
      </div>

      <nav class="nav-menu">
        <router-link to="/dashboard" class="nav-item" active-class="active">
          <span class="icon">📊</span>
          <span class="label">概览仪表盘</span>
        </router-link>
        <router-link to="/data" class="nav-item" active-class="active">
          <span class="icon">💾</span>
          <span class="label">数据采集</span>
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
      <header class="top-header glass">
        <div class="header-left">
          <h2>{{ currentRouteTitle }}</h2>
        </div>
        <div class="header-right">
          <div class="user-profile">
            <span class="avatar">Admin</span>
          </div>
        </div>
      </header>

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
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRouteTitle = computed(() => route.meta.title || 'MediaCrawler')

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
  background: radial-gradient(circle at top right, rgba(255, 215, 0, 0.05), transparent 40%);
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
  background: linear-gradient(180deg, transparent, var(--primary-color), transparent);
  border-radius: 0 4px 4px 0;
  opacity: 0.3;
  transition: opacity 0.3s, width 0.3s;
}

.sidebar-trigger:hover .trigger-indicator {
  opacity: 0.8;
  width: 6px;
}

.trigger-dots {
  display: none;
  position: absolute;
  left: 6px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--primary-color);
  font-size: 14px;
  letter-spacing: 1px;
  writing-mode: vertical-rl;
  text-orientation: upright;
}

.sidebar-trigger:hover .trigger-dots {
  display: block;
}

/* Sidebar */
.sidebar {
  width: 240px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
  background: var(--sidebar-bg);
  z-index: 10;
  transform: translateX(-100%);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  box-shadow: 2px 0 20px rgba(0, 0, 0, 0.5);
}

.sidebar.sidebar-visible {
  transform: translateX(0);
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  gap: 0.8rem;
  border-bottom: 1px solid var(--border-color);
}

.logo-icon {
  font-size: 1.5rem;
  filter: drop-shadow(0 0 5px var(--primary-color));
}

.logo h1 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--primary-color);
  letter-spacing: 1px;
}

.nav-menu {
  flex: 1;
  padding: 1.5rem 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  color: var(--secondary-color);
  transition: all 0.3s;
  border: 1px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-color);
  transform: translateX(4px);
}

.nav-item.active {
  background: rgba(255, 215, 0, 0.1);
  color: var(--primary-color);
  border-color: rgba(255, 215, 0, 0.2);
  box-shadow: 0 0 15px rgba(255, 215, 0, 0.1);
}

.nav-item .icon {
  font-size: 1.2rem;
}

.nav-item .label {
  font-weight: 500;
}

.sidebar-footer {
  padding: 1rem;
  text-align: center;
  color: #555;
  font-size: 0.8rem;
  border-top: 1px solid var(--border-color);
}

.main-content-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: 100%;
}

.top-header {
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  border-bottom: 1px solid var(--border-color);
  background: rgba(13, 17, 23, 0.6);
  backdrop-filter: blur(10px);
}

.top-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  letter-spacing: 0.5px;
}

.user-profile .avatar {
  padding: 0.4rem 1rem;
  background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
  color: #000;
  font-weight: bold;
  border-radius: 20px;
  font-size: 0.85rem;
  box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  position: relative;
}

/* Page Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
