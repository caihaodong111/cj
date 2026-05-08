<template>
  <div class="main-layout">
    <div
      class="sidebar-trigger"
      @click="toggleSidebar"
      @mouseenter="showSidebar"
      @mouseleave="hideSidebar"
    >
      <div class="trigger-indicator">
        <span class="trigger-pulse"></span>
        <span class="trigger-label">NAV</span>
      </div>
    </div>

    <aside
      class="sidebar"
      :class="{ 'sidebar-visible': isSidebarVisible }"
      @click.stop
      @mouseenter="showSidebar"
      @mouseleave="hideSidebar"
    >
      <div class="sidebar-shell">
        <div class="sidebar-glow cyan"></div>
        <div class="sidebar-glow gold"></div>

        <div class="brand-panel">
          <div class="brand-mark" aria-hidden="true">
            <span class="brand-ring outer"></span>
            <span class="brand-ring inner"></span>
            <span class="brand-core"></span>
          </div>
          <div class="brand-copy">
            <span class="brand-eyebrow">Media Intelligence</span>
            <h1>舆镜</h1>
            <p>Sentiment Control Deck</p>
          </div>
        </div>

        <div class="menu-eyebrow">Navigation</div>

        <nav class="nav-menu">
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="nav-item"
            active-class="active"
          >
            <span class="nav-icon" aria-hidden="true">
              <svg v-if="item.key === 'dashboard'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 12h16" />
                <path d="M12 4v16" />
                <circle cx="12" cy="12" r="3.5" />
              </svg>
              <svg v-else-if="item.key === 'data'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <rect x="4" y="5" width="16" height="14" rx="2.5" />
                <path d="M4 10h16" />
                <path d="M9 5v14" />
                <path d="M15 5v14" />
              </svg>
              <svg v-else-if="item.key === 'analysis'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="5.5" />
                <path d="M16 16l4 4" />
                <path d="M11 8v6" />
                <path d="M8 11h6" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3.2" />
                <path d="M12 2.8v2.4" />
                <path d="M12 18.8v2.4" />
                <path d="M4.8 4.8l1.7 1.7" />
                <path d="M17.5 17.5l1.7 1.7" />
                <path d="M2.8 12h2.4" />
                <path d="M18.8 12h2.4" />
                <path d="M4.8 19.2l1.7-1.7" />
                <path d="M17.5 6.5l1.7-1.7" />
              </svg>
            </span>

            <span class="nav-copy">
              <span class="nav-title">{{ item.label }}</span>
              <span class="nav-subtitle">{{ item.subtitle }}</span>
            </span>

            <span class="nav-arrow" aria-hidden="true">
              <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 14L14 6" />
                <path d="M7 6h7v7" />
              </svg>
            </span>
          </router-link>
        </nav>

        <div class="sidebar-footer">
          <div class="version">v1.0.1 Beta</div>
        </div>
      </div>
    </aside>

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

const navItems = [
  {
    key: 'dashboard',
    to: '/dashboard',
    label: '舆情监测总览',
    subtitle: 'Sentiment Dashboard'
  },
  {
    key: 'data',
    to: '/data',
    label: '数据源概览',
    subtitle: 'Data Source Overview'
  },
  {
    key: 'analysis',
    to: '/analysis',
    label: '深度分析',
    subtitle: 'Deep Analysis'
  },
  {
    key: 'settings',
    to: '/settings',
    label: '系统设置',
    subtitle: 'System Settings'
  }
]

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
  }, 180)
}

const closeSidebar = () => {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
  isSidebarVisible.value = false
}

const toggleSidebar = () => {
  if (isSidebarVisible.value) {
    closeSidebar()
    return
  }
  showSidebar()
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

.sidebar-trigger {
  position: fixed;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 132px;
  z-index: 15;
  cursor: pointer;
}

.trigger-indicator {
  position: absolute;
  left: 0;
  inset: 0;
  border-radius: 999px;
  border: 1px solid rgba(0, 204, 255, 0.16);
  background: linear-gradient(180deg, rgba(0, 204, 255, 0.14), rgba(8, 12, 18, 0.82), rgba(255, 170, 0, 0.1));
  backdrop-filter: blur(18px);
  box-shadow:
    0 0 18px rgba(0, 204, 255, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  transition: all 0.28s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.sidebar-trigger:hover .trigger-indicator {
  transform: translateX(2px);
  border-color: rgba(0, 204, 255, 0.28);
  box-shadow:
    0 0 24px rgba(0, 204, 255, 0.28),
    0 0 40px rgba(255, 170, 0, 0.08);
}

.trigger-label {
  color: #9fe6ff;
  font-size: 11px;
  letter-spacing: 2px;
  writing-mode: vertical-rl;
  text-orientation: upright;
  text-shadow: 0 0 12px rgba(0, 204, 255, 0.45);
}

.trigger-pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #00d6ff;
  box-shadow: 0 0 14px rgba(0, 214, 255, 0.75);
  animation: triggerPulse 2s ease-in-out infinite;
}

@keyframes triggerPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.75;
  }
  50% {
    transform: scale(1.35);
    opacity: 1;
  }
}

.sidebar {
  z-index: 10;
  position: fixed;
  left: 18px;
  top: 18px;
  bottom: 18px;
  width: 286px;
  transform: translateX(calc(-100% - 34px));
  transition: transform 0.34s cubic-bezier(0.16, 1, 0.3, 1);
}

.sidebar.sidebar-visible {
  transform: translateX(0);
}

.sidebar-shell {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 18px;
  border-radius: 30px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(8, 12, 18, 0.92) 0%, rgba(6, 9, 15, 0.94) 100%);
  backdrop-filter: blur(28px) saturate(165%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 28px 70px rgba(0, 0, 0, 0.45),
    0 0 0 1px rgba(255, 255, 255, 0.03),
    0 0 36px rgba(0, 204, 255, 0.12);
}

.sidebar-glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(64px);
  opacity: 0.6;
  pointer-events: none;
}

.sidebar-glow.cyan {
  width: 220px;
  height: 220px;
  left: -80px;
  top: -30px;
  background: rgba(0, 204, 255, 0.18);
}

.sidebar-glow.gold {
  width: 180px;
  height: 180px;
  right: -70px;
  bottom: 44px;
  background: rgba(255, 170, 0, 0.14);
}

.brand-panel,
.nav-menu,
.sidebar-footer,
.menu-eyebrow {
  position: relative;
  z-index: 1;
}

.brand-panel {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 6px 20px;
  margin-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.brand-mark {
  position: relative;
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(0, 204, 255, 0.22), rgba(255, 170, 0, 0.14));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 0 24px rgba(0, 204, 255, 0.18);
}

.brand-ring,
.brand-core {
  position: absolute;
  inset: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
}

.brand-ring.outer {
  width: 28px;
  height: 28px;
  border: 1px solid rgba(0, 204, 255, 0.7);
}

.brand-ring.inner {
  width: 16px;
  height: 16px;
  border: 1px solid rgba(255, 170, 0, 0.8);
}

.brand-core {
  width: 6px;
  height: 6px;
  background: #ffffff;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.9);
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.brand-eyebrow {
  font-size: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: rgba(0, 204, 255, 0.72);
}

.brand-copy h1 {
  margin: 0;
  font-size: 1.7rem;
  font-weight: 800;
  letter-spacing: 6px;
  background: linear-gradient(135deg, #f8fbff 0%, #7ce6ff 45%, #f0f7ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 24px rgba(0, 204, 255, 0.18);
}

.brand-copy p {
  margin: 0;
  font-size: 11px;
  letter-spacing: 1px;
  color: #7f94b3;
}

.menu-eyebrow {
  padding: 12px 6px 10px;
  font-size: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: rgba(255, 170, 0, 0.75);
}

.nav-menu {
  flex: 1;
  padding: 0.2rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.nav-item {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr) 18px;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 18px;
  color: #c8d5ea;
  transition: all 0.24s ease;
  border: 1px solid rgba(255, 255, 255, 0.04);
  text-decoration: none;
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.015);
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 10px;
  right: 10px;
  top: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
  opacity: 0;
  transition: opacity 0.24s ease;
}

.nav-item::after {
  content: '';
  position: absolute;
  left: 0;
  top: 16px;
  bottom: 16px;
  width: 3px;
  border-radius: 999px;
  background: linear-gradient(180deg, #00ccff, #ffae00);
  opacity: 0;
  transform: scaleY(0.4);
  transition: all 0.24s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.045);
  color: #fff;
  transform: translateX(3px);
  border-color: rgba(0, 204, 255, 0.12);
  box-shadow: 0 0 22px rgba(0, 204, 255, 0.08);
}

.nav-item:hover::before,
.nav-item:hover::after {
  opacity: 1;
  transform: scaleY(1);
}

.nav-item.active {
  background:
    linear-gradient(135deg, rgba(255, 170, 0, 0.12), rgba(0, 204, 255, 0.06)),
    rgba(255, 255, 255, 0.035);
  color: #fff7de;
  border-color: rgba(255, 170, 0, 0.24);
  box-shadow:
    0 0 26px rgba(255, 170, 0, 0.12),
    0 0 18px rgba(0, 204, 255, 0.08);
}

.nav-item.active::before,
.nav-item.active::after {
  opacity: 1;
  transform: scaleY(1);
}

.nav-icon {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #93e7ff;
  background: linear-gradient(135deg, rgba(0, 204, 255, 0.12), rgba(255, 255, 255, 0.03));
  border: 1px solid rgba(0, 204, 255, 0.12);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
  transition: all 0.24s ease;
}

.nav-icon svg {
  width: 20px;
  height: 20px;
}

.nav-item:hover .nav-icon {
  transform: translateY(-1px);
  color: #c4f4ff;
  border-color: rgba(0, 204, 255, 0.2);
}

.nav-item.active .nav-icon {
  color: #ffd98d;
  background: linear-gradient(135deg, rgba(255, 170, 0, 0.16), rgba(0, 204, 255, 0.08));
  border-color: rgba(255, 170, 0, 0.22);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.08),
    0 0 18px rgba(255, 170, 0, 0.14);
}

.nav-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.nav-title {
  font-weight: 600;
  letter-spacing: 0.5px;
  font-size: 0.98rem;
  color: inherit;
}

.nav-subtitle {
  font-size: 0.72rem;
  letter-spacing: 0.9px;
  color: #7f94b3;
  text-transform: uppercase;
}

.nav-arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.28);
  transition: all 0.24s ease;
}

.nav-arrow svg {
  width: 14px;
  height: 14px;
}

.nav-item:hover .nav-arrow,
.nav-item.active .nav-arrow {
  color: #9fe6ff;
  transform: translate(1px, -1px);
}

.sidebar-footer {
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.version {
  align-self: flex-start;
  padding: 0.42rem 0.8rem;
  border-radius: 999px;
  background: rgba(0, 204, 255, 0.08);
  border: 1px solid rgba(0, 204, 255, 0.15);
  color: #9edcf4;
  font-size: 0.72rem;
  letter-spacing: 1px;
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

@media (max-width: 900px) {
  .sidebar {
    width: min(286px, calc(100vw - 32px));
    left: 16px;
    top: 16px;
    bottom: 16px;
  }

  .sidebar-trigger {
    left: 8px;
    width: 26px;
    height: 116px;
  }
}
</style>
