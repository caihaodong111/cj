<template>
  <div class="main-layout">
    <!-- Sidebar -->
    <aside class="sidebar glass">
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
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRouteTitle = computed(() => route.meta.title || 'MediaCrawler')
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: radial-gradient(circle at top right, rgba(255, 215, 0, 0.05), transparent 40%);
}

.sidebar {
  width: 240px;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
  background: var(--sidebar-bg);
  z-index: 10;
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
  overflow: hidden;
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
