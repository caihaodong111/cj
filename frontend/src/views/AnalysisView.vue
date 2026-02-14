<template>
  <div class="analysis-wrapper">
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

    <div class="analysis-view">
      <header class="page-header entrance-slide-in">
        <div class="title-area">
          <h1 class="ios-title">深度分析<span class="subtitle">Deep Sentiment Analysis</span></h1>
        </div>
      </header>

      <div class="header-filters ios-glass entrance-scale-up">
        <div class="border-glow gold-tint"></div>
        <div class="section-header">
          <span class="accent-bar"></span>
          分析条件
        </div>
        <div class="filters">
          <select class="filter-select">
            <option>过去 7 天</option>
            <option>过去 30 天</option>
            <option>自定义时间</option>
          </select>
          <select class="filter-select">
            <option>所有平台</option>
            <option>小红书</option>
            <option>抖音</option>
            <option>微博</option>
          </select>
          <button class="btn-primary">开始分析</button>
        </div>
      </div>

      <!-- Word Cloud Section -->
      <section class="analysis-section ios-glass entrance-scale-up-delay-2">
        <div class="border-glow"></div>
        <div class="section-header">
          <span class="accent-bar"></span>
          核心关键词云 <span class="section-subtitle">Keywords</span>
        </div>
        <div class="word-cloud-container">
          <span
            v-for="(word, index) in keywords"
            :key="index"
            class="cloud-word"
            :style="{
              fontSize: word.size + 'px',
              top: word.top + '%',
              left: word.left + '%',
              color: word.color,
              animationDelay: index * 0.1 + 's'
            }"
          >
            {{ word.text }}
          </span>
        </div>
      </section>

      <div class="charts-row">
        <div class="chart-wrapper ios-glass entrance-scale-up-delay-3">
          <div class="border-glow blue-tint"></div>
          <ChartCard title="平台声量分布" :options="platformChartOptions" />
        </div>

        <div class="chart-wrapper ios-glass entrance-scale-up-delay-3">
          <div class="border-glow purple-tint"></div>
          <ChartCard title="情感演变趋势" :options="sentimentEvolutionOptions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ChartCard from '../components/ChartCard.vue'

// Mock Data for Word Cloud
const keywords = ref([
  { text: '人工智能', size: 40, top: 40, left: 45, color: '#FFD700' },
  { text: '发布会', size: 30, top: 20, left: 30, color: '#FF4500' },
  { text: '遥遥领先', size: 35, top: 60, left: 60, color: '#00BFFF' },
  { text: '价格', size: 25, top: 30, left: 70, color: '#FFFFFF' },
  { text: '性能', size: 28, top: 70, left: 30, color: '#32CD32' },
  { text: '外观', size: 20, top: 15, left: 55, color: '#FF69B4' },
  { text: '电池', size: 22, top: 80, left: 50, color: '#FFA500' },
  { text: '系统', size: 26, top: 50, left: 20, color: '#9370DB' },
  { text: '卡顿', size: 18, top: 25, left: 10, color: '#808080' },
  { text: '期待', size: 24, top: 85, left: 80, color: '#FFD700' },
])

// Chart Options
const platformChartOptions = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#333' } },
    axisLabel: { color: '#aaa' }
  },
  yAxis: {
    type: 'category',
    data: ['微博', '抖音', '小红书', 'B站', '知乎'],
    axisLabel: { color: '#fff' }
  },
  series: [
    {
      name: '声量',
      type: 'bar',
      data: [320, 302, 290, 150, 80],
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#188df0' }
        ])
      },
      label: { show: true, position: 'right', color: '#fff' }
    }
  ]
}))

import * as echarts from 'echarts'

const sentimentEvolutionOptions = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['积极', '消极'],
    textStyle: { color: '#aaa' },
    bottom: 0
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    axisLine: { lineStyle: { color: '#555' } }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#333' } }
  },
  series: [
    {
      name: '积极',
      type: 'line',
      smooth: true,
      data: [120, 132, 101, 134, 90, 230, 210],
      itemStyle: { color: '#91CC75' }
    },
    {
      name: '消极',
      type: 'line',
      smooth: true,
      data: [22, 18, 19, 23, 29, 33, 31],
      itemStyle: { color: '#EE6666' }
    }
  ]
}))
</script>

<style scoped>
.analysis-wrapper {
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

.analysis-view {
  position: relative;
  z-index: 1;
  padding: 32px 40px 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: 100vh;
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

.border-glow.blue-tint {
  background: linear-gradient(135deg, rgba(0, 195, 255, 0.55), transparent 45%, rgba(0, 195, 255, 0.15));
}

.border-glow.purple-tint {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.55), transparent 45%, rgba(168, 85, 247, 0.15));
}

.border-glow.gold-tint {
  background: linear-gradient(135deg, rgba(255, 170, 0, 0.55), transparent 45%, rgba(255, 170, 0, 0.15));
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

.entrance-scale-up-delay-2 {
  animation: scaleUpFade 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.4s forwards;
  opacity: 0;
  transform: scale(0.95) translateY(24px);
}

.entrance-scale-up-delay-3 {
  animation: scaleUpFade 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.6s forwards;
  opacity: 0;
  transform: scale(0.92) translateY(30px);
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

.header-filters {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.75);
}

.section-subtitle {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.45);
  margin-left: 8px;
  letter-spacing: 1px;
}

.accent-bar {
  width: 4px;
  height: 18px;
  border-radius: 999px;
  background: linear-gradient(180deg, #ffaa00, #ff6a00);
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-select {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.85);
  padding: 0.6rem 1rem;
  border-radius: 999px;
  outline: none;
}

.analysis-section {
  padding: 20px 24px;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.word-cloud-container {
  flex: 1;
  position: relative;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.cloud-word {
  position: absolute;
  transform: translate(-50%, -50%);
  font-weight: bold;
  opacity: 0;
  animation: fadeIn 0.5s ease-out forwards;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
  cursor: default;
  transition: transform 0.3s;
}

.cloud-word:hover {
  transform: translate(-50%, -50%) scale(1.2);
  z-index: 10;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  min-height: 400px;
}

.chart-wrapper {
  padding: 12px;
}
</style>
