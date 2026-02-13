<template>
  <div class="analysis-view">
    <div class="header-filters glass">
      <h3>深度舆情分析</h3>
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
    <section class="analysis-section glass">
      <h4>核心关键词云 (Keywords)</h4>
      <div class="word-cloud-container">
        <!-- Simulated Word Cloud using absolute positioning for now -->
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
      <!-- Platform Breakdown -->
      <div class="chart-wrapper glass">
        <ChartCard title="平台声量分布" :options="platformChartOptions" />
      </div>
      
      <!-- Sentiment Evolution -->
      <div class="chart-wrapper glass">
        <ChartCard title="情感演变趋势" :options="sentimentEvolutionOptions" />
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
.analysis-view {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
  overflow-y: auto;
}

.header-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-radius: 12px;
}

.header-filters h3 {
  margin: 0;
  color: var(--primary-color);
}

.filters {
  display: flex;
  gap: 1rem;
}

.filter-select {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  outline: none;
}

/* Word Cloud */
.analysis-section {
  padding: 1.5rem;
  border-radius: 12px;
  min-height: 300px;
  display: flex;
  flex-direction: column;
}

.analysis-section h4 {
  margin: 0 0 1rem 0;
  color: var(--secondary-color);
}

.word-cloud-container {
  flex: 1;
  position: relative;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  overflow: hidden;
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

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  min-height: 400px;
}

.chart-wrapper {
  border-radius: 12px;
  overflow: hidden;
}
</style>
